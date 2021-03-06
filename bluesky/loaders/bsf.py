"""bluesky.loaders.bsf

BSF csv structure

id,event_id,latitude,longitude,type,area,date_time,slope,state,county,country,fips,scc,fuel_1hr,fuel_10hr,fuel_100hr,fuel_1khr,fuel_10khr,fuel_gt10khr,shrub,grass,rot,duff,litter,moisture_1hr,moisture_10hr,moisture_100hr,moisture_1khr,moisture_live,moisture_duff,consumption_flaming,consumption_smoldering,consumption_residual,consumption_duff,min_wind,max_wind,min_wind_aloft,max_wind_aloft,min_humid,max_humid,min_temp,max_temp,min_temp_hour,max_temp_hour,sunrise_hour,sunset_hour,snow_month,rain_days,heat,pm25,pm10,co,co2,ch4,nox,nh3,so2,voc,VEG,canopy,event_url,fccs_number,owner,sf_event_guid,sf_server,sf_stream_name,timezone
SF11C77574457421602580,SF11E4146026,27.188,-81.113,RX,67.999999831,201905280000-04:00,10.0,FL,,USA,12043,2810015000,0.5,0.25,0.25,0.0,0.0,0.0,2.2,0.0,1.0,0.0,1.0,10.0,12.0,12.0,22.0,130.0,150.0,4.48236738577,0.430136575756,0.332945533864,0.0,6.0,6.0,6.0,6.0,40.0,80.0,13.0,30.0,4,14,6,19,5,8,710946484.545042,3.0819790000000005,3.6367379999999994,32.78775999999999,575.1165699999999,1.676383,0.784719,0.5446900000000001,0.349551,7.829838999999999,Default Unknown Fuel Type,0.0,http://128.208.123.111/smartfire/events/f037f5b4-01c3-4223-bee4-8dfc0e7b9967,0,,f037f5b4-01c3-4223-bee4-8dfc0e7b9967,128.208.123.111,realtime,-5.0

"""

__author__ = "Joel Dubowy"

import datetime
import logging
import re
import traceback
import uuid
from collections import defaultdict

from bluesky.models.fires import Fire
from . import BaseCsvFileLoader
from bluesky.datetimeutils import parse_datetime, parse_utc_offset

__all__ = [
    'CsvFileLoader'
]


##
## Loader Classes
##

ONE_DAY = datetime.timedelta(days=1)

def get_optional_float(val):
    # CSV2JSON should have already converted floats, but this is just
    # in case it didn't
    if val not in ('', None):
        return float(val)
    # else return None

LOCATION_FIELDS = [
    # structure:  (csv_key, location_attr, conversion_func)
    # string fields
    ("state", "state", lambda val: val),
    ("county", "county", lambda val: val),
    ("country", "country", lambda val: val),
    # required float fields
    ("latitude", "lat", lambda val: float(val)),
    ("longitude", "lng", lambda val: float(val)),
    # optional float fields
    ("area", "area", get_optional_float),
    ("slope", "slope", get_optional_float),
    ("fuel_1hr", "fuel_1hr", get_optional_float),
    ("fuel_10hr", "fuel_10hr", get_optional_float),
    ("fuel_100hr", "fuel_100hr", get_optional_float),
    ("fuel_1khr", "fuel_1khr", get_optional_float),
    ("fuel_10khr", "fuel_10khr", get_optional_float),
    ("fuel_gt10khr", "fuel_gt10khr", get_optional_float),
    ("moisture_1hr", "moisture_1hr", get_optional_float),
    ("moisture_10hr", "moisture_10hr", get_optional_float),
    ("moisture_100hr", "moisture_100hr", get_optional_float),
    ("moisture_1khr", "moisture_1khr", get_optional_float),
    ("moisture_live", "moisture_live", get_optional_float),
    ("moisture_duff", "moisture_duff", get_optional_float),
    ("min_wind", "min_wind", get_optional_float),
    ("max_wind", "max_wind", get_optional_float),
    ("min_wind_aloft", "min_wind_aloft", get_optional_float),
    ("max_wind_aloft", "max_wind_aloft", get_optional_float),
    ("min_humid", "min_humid", get_optional_float),
    ("max_humid", "max_humid", get_optional_float),
    ("min_temp", "min_temp", get_optional_float),
    ("max_temp", "max_temp", get_optional_float),
    ("min_temp_hour", "min_temp_hour", get_optional_float),
    ("max_temp_hour", "max_temp_hour", get_optional_float),
    ("sunrise_hour", "sunrise_hour", get_optional_float),
    ("sunset_hour", "sunset_hour", get_optional_float),
    ("snow_month", "snow_month", get_optional_float),
    ("rain_days", "rain_days", get_optional_float)
]
# ignored fields: fips, scc, fuel_1hr, fuel_10hr, fuel_100hr, fuel_1khr,
#   fuel_10khr, fuel_gt10khr, shrub, grass, rot, duff, litter,
#   consumption_flaming, consumption_smoldering,
#   consumption_residual, consumption_duff
#   heat, pm25, pm10, co, co2, ch4, nox, nh3, so2, voc, VEG,
#   canopy, fccs_number, owner, sf_event_guid, sf_server,
#   sf_stream_name, timezone

class CsvFileLoader(BaseCsvFileLoader):

    def __init__(self, **config):
        super().__init__(**config)
        self._skip_failures = config.get('skip_failures')

    def _marshal(self, data):
        self._fires = {}

        for row in data:
            try:
                self._process_row(row)

            except Exception as e:
                if not self._skip_failures:
                    logging.debug(traceback.format_exc())
                    raise ValueError(str(e))
                # else, just log str(e) (which is detailed enough)
                logging.warning(str(e))

        self._post_process_activity()

        return list(self._fires.values())

    def _process_row(self, row):
        fire_id = row.get("id") or str(uuid.uuid4())
        if fire_id not in self._fires:
            self._fires[fire_id] = Fire({
                "id": fire_id,
                "event_of": {},
                "specified_points_by_date": defaultdict(lambda: [])
            })

        start, utc_offset = self._parse_date_time(row["date_time"])
        if not start:
            raise ValueError("Fire location missing time information")

        sp = {loc_attr: f(row.get(csv_key))
            for csv_key, loc_attr, f in LOCATION_FIELDS}
        if utc_offset:
            sp['utc_offset'] = utc_offset
        self._fires[fire_id]['specified_points_by_date'][start].append(sp)

        # event and type could have been set when the Fire object was
        # instantiated, but checking amd setting here allow the fields to
        # be set even if only subsequent rows for the fire have them defined
        if row.get("event_id"):
            self._fires[fire_id]["event_of"]["id"] = row["event_id"]
        if row.get("event_url"):
            self._fires[fire_id]["event_of"]["url"] = row["event_url"]

        if row.get("type"):
            self._fires[fire_id]["type"] = row["type"].lower()

        # TODO: other marshaling

    def _post_process_activity(self):
        for fire in self._fires.values():
            fire["activity"] = []
            sorted_items = sorted(fire.pop("specified_points_by_date").items(),
                key=lambda a: a[0])
            for start, specified_points in sorted_items:
                fire['activity'].append({
                    "active_areas": [
                        {
                            "start": start,
                            "end": start + ONE_DAY,
                            "specified_points": specified_points
                        }
                    ]
                })

    # Note: Although 'timezone' (a numberical value) is defined alongsite
    #   date_time (which may include utc_offset), utc_offset, if defined, reflects
    #   daylight savings and thus is the true offset from UTC, whereas timezone
    #   does not change; e.g. an august 5th fire in Florida is listed with timezone
    #   -5.0 and utc_offset (embedded in the 'date_time' field) '-04:00'

    ## 'date_time'
    OLD_DATE_TIME_MATCHER = re.compile('^(\d{12})(\d{2})?Z$')
    DATE_TIME_MATCHER = re.compile('^(\d{12})(\d{2})?([+-]\d{2}\:\d{2})$')
    DATE_TIME_FMT = "%Y%m%d%H%M"

    def _parse_date_time(self, date_time):
        """Parses 'date_time' field, found in BSF fire data

        Note: older BSF fire data formatted the date_time field without
        local timezone information, mis-representing everything as
        UTC.  E.g.:

            '201405290000Z'

        Newer (and current) SF2 fire data formats date_time like so:

            '201508040000-04:00'

        With true utc offset embedded in the string.
        """
        start = None
        utc_offset = None
        if date_time:
            try:
                m = self.DATE_TIME_MATCHER.match(date_time)
                if m:
                    start = datetime.datetime.strptime(
                        m.group(1), self.DATE_TIME_FMT)
                    utc_offset = parse_utc_offset(m.group(3))
                else:
                    m = self.OLD_DATE_TIME_MATCHER.match(date_time)
                    if m:
                        start = datetime.datetime.strptime(
                            m.group(1), self.DATE_TIME_FMT)
                        # Note: we don't know utc offset; don't set

            except Exception as e:
                logging.warn("Failed to parse 'date_time' value %s",
                    date_time)
                logging.debug(traceback.format_exc())

        return start, utc_offset
