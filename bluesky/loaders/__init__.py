"""bluesky.loaders

The loader packages and classes should be organized and named such that, given
the source name (e.g. 'Smartfire2'), format (e.g. 'CSV'), and 'type' (e.g.
'file'), bluesky.modules.load can dynamically import the module with:

    >>> loader_module importlib.import_module(
        'bluesky.loaders.<source_name_to_lower_case>.<format_to_lower_case>')'

and then get the loading class with:

    >>> getattr(loader_module, '<source_type_capitalized>Loader')

For example, the smartfire csv file loader is in module
bluesky.loaders.smartfire.csv and is called FileLoader
"""

import datetime
import logging
import os

from pyairfire.datetime.parsing import parse as parse_dt
from pyairfire.io import CSV2JSON

from bluesky import datetimeutils, fileutils

__author__ = "Joel Dubowy"
__copyright__ = "Copyright 2016, AirFire, PNW, USFS"

class BaseLoader(object):

    def __init__(self, **config):
        # TODO: use local times instead of UTC?
        if config.get('date_time'):
            if isinstance(config['date_time'], datetime.date):
                self._date_time = config['date_time']
            elif hasattr(config['date_time'], 'lower'):
                if config['date_time'] == 'today':
                    self._date_time = datetimeutils.today_utc()
                elif config['date_time'] == 'yesterday':
                    self._date_time = datetimeutils.yesterday_utc()
                else:
                    self._date_time = parse_dt(config['date_time'])
            else:
                raise ValueError("Invalid value for load source's date_time: "
                    "{}".format(config['date_time']))
        else:
            self._date_time = datetimeutils.today_utc()
        logging.debug('Load date_time = %s', self._date_time)

class BaseFileLoader(BaseLoader):

    def __init__(self, **config):
        super(BaseFileLoader, self).__init__(**config)
        self._filename = fileutils.find_with_datetime(
            config.get('file'), self._date_time)

        self._events_filename = None
        if config.get('events_file'):
            self._events_filename = fileutils.find_with_datetime(
                config['events_file'], self._date_time)

    ##
    ## File IO
    ##

    def _load_csv_file(self, filename):
        csv_loader = CSV2JSON(input_file=filename)
        return csv_loader._load()

    # TODO: provide other file reading functionality as needed
