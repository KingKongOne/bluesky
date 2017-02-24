"""bluesky.statuslogging"""

__author__ = "Joel Dubowy"

import asyncio
import datetime
import logging

from pyairfire import statuslogging

__all__ = [
    'StatusLogger'
]

class StatusLogger(object):

    def __init__(self, init_time, **config): #, log_level):
        self.enabled = config and config.get('enabled')
        if self.enabled:
            self.init_time = init_time
            # TODO: error handling to catch undefined fields
            self.sl = statuslogging.StatusLogger(
                config.get('api_endpoint'), config.get('api_key'),
                config.get('api_secret'), config.get('process'))
            self.domain = config.get('domain')
            #self.log_level = log_level

    # def __getattr__(self, name):
    #     if name in ('debug', 'info', 'warn', 'error'):

    async def _log_async(self, status, **fields):
        try:
            logging.debug('Submitting status log')
            self.sl.log(status, **fields)
            logging.debug('Submitted status log')
        except Exception as e:
            logging.warn('Failed to submit status log: %s', e)

    def log(self, status, step, action, **extra_fields):
        if self.enabled:
            fields = {
                'initialization_time': self.init_time,
                'status': status,
                'step': step,
                'action': action,
                'timestamp': datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
                'machine':  'DETERMINE MACHINE',
                'domain': self.domain
            }
            fields.update(extra_fields)
            logging.debug('Before submitting status log')
            asyncio.get_event_loop().run_until_complete(self._log_async(**fields))
            logging.debug('After submitting status log')
        else:
            logging.debug('Status logging disabled.')
