"""Unit tests for bluesky.modules.ingestion"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import copy

from py.test import raises

from bluesky.modules import ingestion

class TestIngester(object):

    def setup(self):
        self.ingester = ingestion.FireIngester()

    ##
    ## Tests For ingest
    ##

    def test_fire_missing_required_fields(self):
        with raises(ValueError) as e:
            self.ingester.ingest({})

        # location must have perimeter or lat+lng+area
        with raises(ValueError) as e:
            self.ingester.ingest({"location": {}})

    def test_fire_with_invalid_growth(self):
        # If growth is specified, each object in the array must have
        # 'start', 'end', and 'pct' defined
        with raises(ValueError) as e:
            self.ingester.ingest(
                {
                    "location": {
                        "perimeter": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [-121.4522115, 47.4316976],
                                        [-121.3990506, 47.4316976],
                                        [-121.3990506, 47.4099293],
                                        [-121.4522115, 47.4099293],
                                        [-121.4522115, 47.4316976]
                                    ]
                                ]
                            ]
                        },
                        "ecoregion": "southern"
                    },
                    "growth": [
                        {
                            "sdf": 1
                        }
                    ]
                }
            )

    def test_fire_was_aready_ingested(self):
        with raises(RuntimeError) as e:
            self.ingester.ingest({'input':{}})

    def test_fire_with_minimum_fields(self):
        f = {
            "location": {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                }
            }
        }
        expected = {
            'input': copy.deepcopy(f),
            'location': copy.deepcopy(f['location'])
        }
        self.ingester.ingest(f)
        assert expected == f

    def test_fire_with_maximum_optional_fields(self):
        f = {
            "id": "SF11C14225236095807750",
            "event_of": {
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            "location": {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                },
                "ecoregion": "southern"
            },
            "growth": [{
                "start": "20150120",
                "end": "20150120",
                "pct": 100.0
            }]
        }
        expected = {
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            'input': copy.deepcopy(f),
            'location': copy.deepcopy(f['location']),
            'growth': copy.deepcopy(f['growth'])
        }
        self.ingester.ingest(f)
        assert expected == f

    def test_flat_fire(self):
        f = {
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            "perimeter": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-121.4522115, 47.4316976],
                            [-121.3990506, 47.4316976],
                            [-121.3990506, 47.4099293],
                            [-121.4522115, 47.4099293],
                            [-121.4522115, 47.4316976]
                        ]
                    ]
                ]
            },
            "ecoregion": "southern",
            "start": "20150120",
            "end": "20150120",
            "timezone": "-07:00"
        }
        expected = {
            'input': copy.deepcopy(f),
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            'location': {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                },
                "ecoregion": "southern",
                "timezone": "-07:00"
            },
            'growth': [
                {
                    "pct": 100.0,
                    "start": "20150120",
                    "end": "20150120"
                }
            ]
        }
        self.ingester.ingest(f)
        assert expected == f

    def test_flat_and_nested_fire(self):
        f = {
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            "location": {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                }
            },
            "ecoregion": "southern",
            "growth": [
                {
                    "start": "20150120",
                    "end": "20150120",
                    "pct": 100.0
                }
            ],
            "timezone": "-07:00"
        }
        expected = {
            'input': copy.deepcopy(f),
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            'location': {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                },
                "ecoregion": "southern",
                "timezone": "-07:00"
            },
            "growth": [
                {
                    "start": "20150120",
                    "end": "20150120",
                    "pct": 100.0
                }
            ]
        }
        self.ingester.ingest(f)
        assert expected == f


    def test_fire_with_ignored_fields(self):
        f = {
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            "location": {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                },
                "ecoregion": "southern",
                "foo": "bar"
            },
            "growth": [
                {
                    "start": "20150120",
                    "end": "20150120",
                    "pct": 100.0
                }
            ],
            "bar": "baz"
        }
        expected = {
            'input': copy.deepcopy(f),
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            'location': copy.deepcopy(f['location']),
            'growth': copy.deepcopy(f['growth'])
        }
        expected['location'].pop('foo')
        self.ingester.ingest(f)
        assert expected == f

    def test_fire_with_perimeter_and_lat_lng(self):
        f = {
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            "location": {
                "perimeter": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [-121.4522115, 47.4316976],
                                [-121.3990506, 47.4316976],
                                [-121.3990506, 47.4099293],
                                [-121.4522115, 47.4099293],
                                [-121.4522115, 47.4316976]
                            ]
                        ]
                    ]
                },
                "longitude": -77.379,
                "latitude": 25.041,
                "area": 200
            }
        }
        expected = {
            'input': copy.deepcopy(f),
            "id": "SF11C14225236095807750",
            "event_of":{
                "id": "SF11E826544",
                "name": "Natural Fire near Snoqualmie Pass, WA"
            },
            'location': {
                'perimeter': copy.deepcopy(f['location']['perimeter'])
            }
        }
        self.ingester.ingest(f)
        assert expected == f
