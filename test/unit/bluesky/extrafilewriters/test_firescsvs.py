"""Unit tests for bluesky.extrafilewriters.firescsvs"""

__author__ = "Joel Dubowy"

from py.test import raises

from bluesky.models.fires import Fire
from bluesky.extrafilewriters import firescsvs

class TestFiresCsvsPickRepresentativeFuelbed(object):

    def test_invalid_fuelbed(self):
        g = {
            "fuelbeds": 'sdf'
        }
        with raises(AttributeError) as e_info:
            firescsvs._pick_representative_fuelbed({}, g)
        # TODO: assert e_info.value.args[0] == '...''

    def test_no_fuelbeds(self):
        g = {}
        assert None == firescsvs._pick_representative_fuelbed({}, g)
        g = {
            "activity": []
        }
        assert None == firescsvs._pick_representative_fuelbed({}, g)

    def test_one_fuelbed_no_fccs_id(self):
        g = {
            "fuelbeds": [
                {"pct": 100.0}
            ]
        }
        assert None == firescsvs._pick_representative_fuelbed({}, g)

        g["fuelbeds"][0]["sdf_fccs_id"] = "46"
        assert None == firescsvs._pick_representative_fuelbed({}, g)

    def test_one_fuelbed_no_pct(self):
        g = {
            "fuelbeds": [
                {"fccs_id": "46"}
            ]
        }
        assert "46" == firescsvs._pick_representative_fuelbed({}, g)

    def test_two_fuelbeds_one_with_no_pct(self):
        g = {
            "fuelbeds": [
                {"fccs_id": "46"},
                {"fccs_id": "44","pct": 100.0}
            ]
        }
        assert "44" == firescsvs._pick_representative_fuelbed({}, g)


    def test_one_fuelbed(self):
        g = {
            "fuelbeds": [
                {"fccs_id": "46","pct": 100.0}
            ]
        }
        assert "46" == firescsvs._pick_representative_fuelbed({}, g)

    def test_three_fuelbed(self):
        g = {
            "fuelbeds": [
                {"fccs_id": "46","pct": 10.0},
                {"fccs_id": "47","pct": 60.0},
                {"fccs_id": "48","pct": 30.0}
            ]
        }
        assert "47" == firescsvs._pick_representative_fuelbed({}, g)

    def test_two_equal_size_fuelbeds(self):
        g = {
            "fuelbeds": [
                {"fccs_id": "46","pct": 100.0},
                {"fccs_id": "44","pct": 100.0}
            ]
        }
        assert "46" == firescsvs._pick_representative_fuelbed({}, g)


class TestFiresCsvsWriterCollectCsvFields(object):

    def test_one_fire_no_event(self):
        fire = Fire({
            "fuel_type": "natural",
            "id": "SF11C14225236095807750",
            "type": "wildfire",
            "activity": [
                {
                    "active_areas": [
                        {
                            "start": "2015-08-04T18:00:00",
                            "end": "2015-08-05T18:00:00",
                            "utc_offset": "-06:00",
                            "specified_points": [
                                {
                                    "lat": 35.0,
                                    "lng": -96.2,
                                    "area": 99
                                }
                            ]
                        },
                        {
                            "start": "2015-08-04T17:00:00",
                            "end": "2015-08-05T17:00:00",
                            "utc_offset": "-07:00",
                            "canopy_consumption_pct": 23.3,
                            "min_wind": 34,
                            "specified_points": [
                                {
                                    "lat": 30.0,
                                    "lng": -116.2,
                                    "area": 102
                                },
                                {
                                    "area": 120.0,
                                    "rain_days": 8,
                                    "slope": 20.0,
                                    "snow_month": 5,
                                    "sunrise_hour": 4,
                                    "sunset_hour": 19,
                                    "consumption": {
                                        "summary": {
                                            "flaming": 1311.2071801109494,
                                            "residual": 1449.3962581338644,
                                            "smoldering": 1267.0712004277434,
                                            "total": 4027.6746386725567
                                        }
                                    },
                                    "fuelbeds": [
                                        {
                                            "emissions": {
                                                "flaming": {
                                                    "PM2.5": [9.545588271207714]
                                                },
                                                "residual": {
                                                    "PM2.5": [24.10635856528243]
                                                },
                                                "smoldering": {
                                                    "PM2.5": [21.073928205514225]
                                                },
                                                "total": {
                                                    "PM2.5": [54.725875042004375]
                                                }
                                            },
                                            "fccs_id": "9",
                                            "heat": {
                                                "flaming": [20979314881.77519],
                                                "residual": [23190340130.141827],
                                                "smoldering": [20273139206.843895],
                                                "total": [64442794218.7609]
                                            },
                                            "pct": 100.0
                                        }
                                    ],
                                    "lat": 47.41,
                                    "lng": -121.41
                                }
                            ],
                            "state": "WA"
                        }
                    ],
                }
            ]
        })

        writer = firescsvs.FiresCsvsWriter('/foo')
        fires_fields, events_fields = writer._collect_csv_fields([fire])

        expected_fires_fields = [
            {
                "area": 99,
                "canopy_consumption_pct": '',
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': '',
                'consumption_residual': '',
                'consumption_smoldering': '',
                'consumption_total': '',
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': '',
                'event_name': '',
                'fccs_number': '',
                'heat': '',
                'id': 'SF11C14225236095807750',
                "latitude": 35.0,
                "longitude": -96.2,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                'min_wind': '',
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': '',
                'rain_days': '',
                'slope': '',
                'snow_month': '',
                'so2': '',
                'state': '',
                'sunrise_hour': '',
                'sunset_hour': '',
                'type': 'WF',
                "utc_offset": "-06:00",
                'voc': ''
            },
            {
                "area": 102,
                "canopy_consumption_pct": 23.3,
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': '',
                'consumption_residual': '',
                'consumption_smoldering': '',
                'consumption_total': '',
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': '',
                'event_name': '',
                'fccs_number': '',
                'heat': '',
                'id': 'SF11C14225236095807750',
                "latitude": 30.0,
                "longitude": -116.2,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                "min_wind": 34,
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': '',
                'rain_days': '',
                'slope': '',
                'snow_month': '',
                'so2': '',
                'state': 'WA',
                'sunrise_hour': '',
                'sunset_hour': '',
                'type': 'WF',
                "utc_offset": "-07:00",
                'voc': ''
            },
            {
                'area': 120.0,
                "canopy_consumption_pct": 23.3,
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': 1311.2071801109494,
                'consumption_residual': 1449.3962581338644,
                'consumption_smoldering': 1267.0712004277434,
                'consumption_total': 4027.6746386725567,
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': '',
                'event_name': '',
                'fccs_number': '9',
                'heat': 64442794218.7609,
                'id': 'SF11C14225236095807750',
                'latitude': 47.41,
                'longitude': -121.41,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                'min_wind': 34,
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': 54.725875042004375,
                'rain_days': 8.0,
                'slope': 20.0,
                'snow_month': 5.0,
                'so2': '',
                'state': 'WA',
                'sunrise_hour': 4.0,
                'sunset_hour': 19.0,
                'type': 'WF',
                'utc_offset': '-07:00',
                'voc': ''
            }
        ]

        assert len(fires_fields) == len(expected_fires_fields)
        for i in range(len(fires_fields)):
            assert fires_fields[i].keys() == expected_fires_fields[i].keys()
            for k in fires_fields[i]:
                assert fires_fields[i][k] == expected_fires_fields[i][k], "{} differs".format(k)

        expected_events_fields = {}
        assert events_fields == expected_events_fields


    def test_two_fires_one_event(self):
        fires = [
            Fire({
                "fuel_type": "natural",
                "id": "SF11C14225236095807750",
                "event_of": {
                    "id": "bigeventid"
                    # porposely missing 'name'
                },
                "type": "wildfire",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": "2015-08-04T18:00:00",
                                "end": "2015-08-05T18:00:00",
                                "utc_offset": "-06:00",
                                "specified_points": [
                                    {
                                        "lat": 35.0,
                                        "lng": -96.2,
                                        "area": 99,
                                        "fuelbeds": [
                                            {
                                                "emissions": {
                                                    "total": {
                                                        "PM2.5": [10]
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            },
                        ]
                    }
                ]
            }),
            Fire({
                "fuel_type": "natural",
                "id": "SF11C14225236095807750-B",
                "event_of": {
                    "id": "bigeventid",
                    "name": "big event name"
                },
                "type": "wildfire",
                "activity": [
                    {
                        "active_areas": [
                            {
                                "start": "2015-08-04T17:00:00",
                                "end": "2015-08-05T17:00:00",
                                "utc_offset": "-07:00",
                                "canopy_consumption_pct": 23.3,
                                "min_wind": 34,
                                "specified_points": [
                                    {
                                        "lat": 30.0,
                                        "lng": -116.2,
                                        "area": 102
                                    },
                                    {
                                        "area": 120.0,
                                        "rain_days": 8,
                                        "slope": 20.0,
                                        "snow_month": 5,
                                        "sunrise_hour": 4,
                                        "sunset_hour": 19,
                                        "consumption": {
                                            "summary": {
                                                "flaming": 1311.2071801109494,
                                                "residual": 1449.3962581338644,
                                                "smoldering": 1267.0712004277434,
                                                "total": 4027.6746386725567
                                            }
                                        },
                                        "fuelbeds": [
                                            {
                                                "emissions": {
                                                    "flaming": {
                                                        "PM2.5": [9.545588271207714]
                                                    },
                                                    "residual": {
                                                        "PM2.5": [24.10635856528243]
                                                    },
                                                    "smoldering": {
                                                        "PM2.5": [21.073928205514225]
                                                    },
                                                    "total": {
                                                        "PM2.5": [54.725875042004375]
                                                    }
                                                },
                                                "fccs_id": "9",
                                                "heat": {
                                                    "flaming": [20979314881.77519],
                                                    "residual": [23190340130.141827],
                                                    "smoldering": [20273139206.843895],
                                                    "total": [64442794218.7609]
                                                },
                                                "pct": 100.0
                                            }
                                        ],
                                        "lat": 47.41,
                                        "lng": -121.41
                                    }
                                ],
                                "state": "WA"
                            }
                        ],
                    }
                ]
            })
        ]


        writer = firescsvs.FiresCsvsWriter('/foo')
        fires_fields, events_fields = writer._collect_csv_fields(fires)

        expected_fires_fields = [
            {
                "area": 99,
                "canopy_consumption_pct": '',
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': '',
                'consumption_residual': '',
                'consumption_smoldering': '',
                'consumption_total': '',
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': 'bigeventid',
                'event_name': '',
                'fccs_number': '',
                'heat': '',
                'id': 'SF11C14225236095807750',
                "latitude": 35.0,
                "longitude": -96.2,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                'min_wind': '',
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': 10.0,
                'rain_days': '',
                'slope': '',
                'snow_month': '',
                'so2': '',
                'state': '',
                'sunrise_hour': '',
                'sunset_hour': '',
                'type': 'WF',
                "utc_offset": "-06:00",
                'voc': ''
            },
            {
                "area": 102,
                "canopy_consumption_pct": 23.3,
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': '',
                'consumption_residual': '',
                'consumption_smoldering': '',
                'consumption_total': '',
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': 'bigeventid',
                'event_name': 'big event name',
                'fccs_number': '',
                'heat': '',
                'id': 'SF11C14225236095807750-B',
                "latitude": 30.0,
                "longitude": -116.2,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                "min_wind": 34,
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': '',
                'rain_days': '',
                'slope': '',
                'snow_month': '',
                'so2': '',
                'state': 'WA',
                'sunrise_hour': '',
                'sunset_hour': '',
                'type': 'WF',
                "utc_offset": "-07:00",
                'voc': ''
            },
            {
                'area': 120.0,
                "canopy_consumption_pct": 23.3,
                'ch4': '',
                'co': '',
                'co2': '',
                'consumption_flaming': 1311.2071801109494,
                'consumption_residual': 1449.3962581338644,
                'consumption_smoldering': 1267.0712004277434,
                'consumption_total': 4027.6746386725567,
                'country': '',
                'county': '',
                'date_time': '20150804',
                'elevation': '',
                'event_id': 'bigeventid',
                'event_name': 'big event name',
                'fccs_number': '9',
                'heat': 64442794218.7609,
                'id': 'SF11C14225236095807750-B',
                'latitude': 47.41,
                'longitude': -121.41,
                'max_humid': '',
                'max_temp': '',
                'max_temp_hour': '',
                'max_wind': '',
                'max_wind_aloft': '',
                'min_humid': '',
                'min_temp': '',
                'min_temp_hour': '',
                'min_wind': 34,
                'min_wind_aloft': '',
                'moisture_100hr': '',
                'moisture_10hr': '',
                'moisture_1hr': '',
                'moisture_1khr': '',
                'moisture_duff': '',
                'moisture_live': '',
                'nh3': '',
                'nox': '',
                'pm10': '',
                'pm2.5': 54.725875042004375,
                'rain_days': 8.0,
                'slope': 20.0,
                'snow_month': 5.0,
                'so2': '',
                'state': 'WA',
                'sunrise_hour': 4.0,
                'sunset_hour': 19.0,
                'type': 'WF',
                'utc_offset': '-07:00',
                'voc': ''
            }
        ]

        assert len(fires_fields) == len(expected_fires_fields)
        for i in range(len(fires_fields)):
            assert fires_fields[i].keys() == expected_fires_fields[i].keys()
            for k in fires_fields[i]:
                assert fires_fields[i][k] == expected_fires_fields[i][k], "{} differs".format(k)

        expected_events_fields = {
            'bigeventid': {
                'name':'big event name',
                'total_area': 321.0,
                'total_ch4': None,
                'total_co': None,
                'total_co2': None,
                'total_heat': None,
                'total_nh3': None,
                'total_nmhc': None,
                'total_nox': None,
                'total_pm10': None,
                'total_pm2.5': 64.725875042004375,
                'total_so2': None,
                'total_voc': None
            }
        }
        assert events_fields == expected_events_fields
