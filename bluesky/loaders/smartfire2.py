"""bluesky.loaders.smartfire
"""

__author__ = "Joel Dubowy"

import os

from . import BaseFileLoader

__all__ = [
    'FileLoader'
]

class CsvFileLoader(BaseFileLoader):
    """Loads csv formatted SF2 fire and events data from filename
    """

    def __init__(self, **config):
        super(CsvFileLoader, self).__init__(**config)

    def load(self):
        fires = self._load_csv_file(self._filename)
        if self._events_filename:
            events_by_id = self._load_events_file(self._events_filename)
            for f in fires:
                if f.get('event_id') and f['event_id'] in events_by_id:
                    name = events_by_id[f['event_id']].get('event_name')
                    if name:
                        f["name"] = name
                    # TODO: set any other fields
        return fires

    def _load_events_file(self, events_filename):
        # Note: events_filename's existence was already verified by
        #  self._get_filename
        events = self._load_csv_file(events_filename)
        return { e.pop('id'): e for e in events}