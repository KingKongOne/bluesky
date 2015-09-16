"""bluesky.web.api.v1.run"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import io
import json
import logging
import tornado.web

#from bluesky.web.lib.auth import b_auth
from bluesky import modules, models, process
from bluesky.configuration import config_from_dict
from bluesky.exceptions import BlueSkyImportError, BlueSkyModuleError


class Run(tornado.web.RequestHandler):
    # def _bad_request(self, msg):
    #     self.set_status(400)
    #     self.write({"error": msg})

    def post(self):
        if not self.request.body:
            self.set_status(400, 'Bad request: empty post data')
            return

        data = json.loads(self.request.body)
        if "modules" not in data:
            self.set_status(400, "Bad request: 'modules' not specified")
        elif "fire_information" not in data:
            self.set_status(400, "Bad request: 'fire_information' not specified")
        else:
            fires = [models.fires.Fire(f) for f in data['fire_information']]
            fires_manager = models.fires.FiresManager(fires=fires)
            config = config_from_dict(data.get('config') or {})

            # TODO: somehow commincate back from process.run_modules if exception
            # was caught while running modules set status appropriately?  (or should
            # module error not result in http error status, since error is recorded
            # in fires_manager.error
            try:
                process.run_modules(data['modules'], fires_manager, config)
            except BlueSkyModuleError, e:
                # The error was added to fires_manager's meta data, and will
                # be included in the output data
                pass
            except BlueSkyImportError, e:
                self.set_status(400, "Bad request: {}".format(e.message))
            except Exception, e:
                logging.error('Exception: {}'.format(e))
                self.set_status(500)

            # If you pass a dict into self.write, it will dump it to json and set
            # content-type to json;  we need to specify a json encoder, though, so
            # we'll manaually set the header adn dump the json
            self.set_header('Content-Type', 'application/json') #; charset=UTF-8')
            self.write(json.dumps({"fire_information":fires}, cls=models.fires.FireEncoder))
