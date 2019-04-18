"""bluesky.modules.plumerise

Requires time profiled emissions and localmet data.
"""

__author__ = "Joel Dubowy"

import copy
import datetime
import logging
import os

from plumerise import sev, feps, __version__ as plumerise_version
from pyairfire import sun

from bluesky import datautils, datetimeutils, locationutils
from bluesky.config import Config

__all__ = [
    'run'
]

__version__ = "0.1.1"


def run(fires_manager):
    """Runs plumerise module

    Args:
     - fires_manager -- bluesky.models.fires.FiresManager object
    """
    compute_func = ComputeFunction(fires_manager)

    for fire in fires_manager.fires:
        with fires_manager.fire_failure_handler(fire):
            compute_func(fire)

    # TODO: spread out emissions over plume and set in activity or fuelbed
    #   objects ??? (be consistent with profiled emissions, setting in
    #   same place or not setting at all)

    # TODO: set summary?
    # fires_manager.summarize(plumerise=...)

class ComputeFunction(object):
    def __init__(self, fires_manager):
        model = Config.get('plumerising', 'model').lower()
        fires_manager.processed(__name__, __version__,
            plumerise_version=plumerise_version, model=model)

        logging.debug('Generating %s plumerise compution function', model)
        generator = getattr(self, '_{}'.format(model), None)
        if not generator:
            raise BlueSkyConfigurationError(
                "Invalid plumerise model: '{}'".format(model))

        config = Config.get('plumerising', model)
        self._compute_func = generator(config)

        if config.get('working_dir'):
            fires_manager.plumerising = {
                'output': {
                    'directory': config['working_dir']
                }
            }

    def __call__(self, fire):
        if 'activity' not in fire:
            raise ValueError("Missing activity data required for plumerise")
        if any([not a.get('location', {}).get('area') for a in fire.activity]):
            raise ValueError("Missing fire activity area required for plumerise")
        self._compute_func(fire)

    ## compute function generators

    def _feps(self, config):
        pr = feps.FEPSPlumeRise(**config)

        def _get_working_dir(fire):
            if config.get('working_dir'):
                working_dir = os.path.join(config['working_dir'],
                    "feps-plumerise-{}".format(fire.id))
                if not os.path.exists(working_dir):
                    os.makedirs(working_dir)
                return working_dir

        def _f(fire):
            # TODO: create and change to working directory here (per fire),
            #   above (one working dir per all fires), or below (per activity
            #   window)...or just let plumerise create temp workingdir (as
            #   it's currently doing?
            for a in fire.activity:
                if not a.get('consumption', {}).get('summary'):
                    raise ValueError("Missing fire activity consumption data "
                        "required for FEPS plumerise")

                # Fill in missing sunrise / sunset
                if any([a['location'].get(k) is None for k in
                        ('sunrise_hour', 'sunset_hour')]):
                    start = datetimeutils.parse_datetime(a['start'], 'start')
                    if not start:
                        raise ValueError("Missing fire activity start time "
                            "required by FEPS plumerise")

                    # default: UTC
                    utc_offset = datetimeutils.parse_utc_offset(
                        a['location'].get('utc_offset', 0.0))

                    # Use NOAA-standard sunrise/sunset calculations
                    latlng = locationutils.LatLng(a['location'])
                    s = sun.Sun(lat=latlng.latitude, lng=latlng.longitude)
                    d = start.date()
                    # just set them both, even if one is already set
                    a['location']["sunrise_hour"] = s.sunrise_hr(d, utc_offset)
                    a['location']["sunset_hour"] = s.sunset_hr(d, utc_offset)

                if not a.get('timeprofile'):
                    raise ValueError("Missing timeprofile data required for "
                        "computing FEPS plumerise")

                plumerise_data = pr.compute(a['timeprofile'],
                    a['consumption']['summary'], a['location'],
                    working_dir=_get_working_dir(fire))
                a['plumerise'] = plumerise_data['hours']
                # TODO: do anything with plumerise_data['heat'] ?

        return _f

    def _sev(self, config):
        pr = sev.SEVPlumeRise(**config)

        def _f(fire):
            fire_frp = fire.get('meta', {}).get('frp')
            for a in fire.activity:
                if not a.get('localmet'):
                    raise ValueError(
                        "Missing localmet data required for computing SEV plumerise")
                # TODO: if fire_frp is defined but activity's frp isn't,
                #   do we need to multiple by activity's
                #   percentage of the fire's total area?
                a_frp = a.get('frp', fire_frp)
                plumerise_data = pr.compute(a['localmet'],
                    a['location']['area'], frp=a_frp)
                a['plumerise'] = plumerise_data['hours']

        return _f
