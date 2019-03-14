"""Unit tests for bluesky.modules.emissions"""

__author__ = "Joel Dubowy"

import copy
#from unittest import mock

from numpy import array
from numpy.testing import assert_approx_equal
from py.test import raises

import afconfig

from bluesky.config import Config
from bluesky.models.fires import Fire
from bluesky.modules import emissions

FIRES = [
    {
        'source': 'GOES-16',
        'type': "wf",
        "growth":  [
            {
                # timeprofile should be ignored and replcaced when running
                # FRP emissions
                "timeprofile": {
                    "2018-06-27T17:00:00": {
                        'area_fraction': 0.75,
                        'flaming': 0.75,
                        'smoldering': 0.3,
                        'residual': 0.0
                    },
                    "2018-06-27T20:00:00": {
                        'area_fraction': 0.25,
                        'flaming': 0.25,
                        'smoldering': 0.7,
                        'residual': 1.0
                    }
                },
                # Hourly FRP is used for FRP emissions
                "hourly_frp": {
                    "2018-06-27T10:00:00": 55.4,
                    "2018-06-27T11:00:00": 66,
                    "2018-06-27T12:00:00": 78,
                    "2018-06-27T13:00:00": 83,
                    "2018-06-27T18:00:00": 82,
                    "2018-06-27T19:00:00": 66,
                    "2018-06-27T20:00:00": 52.5
                },
                #55.4 + 66 + 78 + 83 + 82 + 66 + 52.5 = 482.9
                "frp": 482.9,
                "location": {
                    'area': 47.20000000000001,
                    "geojson": {
                        "type": "Point",
                        "coordinates": [-71.362, 50.632],
                    },
                    "utc_offset": "-04:00"
                },
                "start": "2018-06-27T00:00:00",
                "end": "2018-06-28T00:00:00"
            }
        ]
    },
    {
        'type': "rx",
        "growth":  [
            {
                "location": {
                    'area': 50.4,
                    "geojson": {
                        "type": "MultiPoint",
                        "coordinates": [
                            [-120.362, 45.632],
                            [-120.3, 45.22]
                        ]
                    },
                    "utc_offset": "-07:00",
                    "ecoregion": "western" # needed by CONSUME
                },
                "start": "2018-06-27T00:00:00",
                "end": "2018-06-28T00:00:00",
                "fuelbeds": [
                    {
                        "fccs_id": "52",
                        "pct": 100.0,
                        "consumption": {
                            "foo": {
                                "bar": {
                                    "smoldering": [0.0],
                                    "residual": [200.4],
                                    "flaming": [0.0]
                                },
                                "baz": {
                                    "smoldering": [900.5],
                                    "residual": [800.0],
                                    "flaming": [100.2]
                                }
                            },
                            "boo": {
                                "blem": {
                                    "smoldering": [0.0],
                                    "residual": [0.0],
                                    "flaming": [200]
                                }
                            }
                        },
                        # heat required by CONSUME
                        "heat": {
                            "flaming": [
                                159765789.2311308
                            ],
                            "residual": [
                                0.0
                            ],
                            "smoldering": [
                                13157759.100788476
                            ],
                            "total": [
                                172923548.3319193
                            ]
                        }
                    }
                ]
            }
        ]
    }
]

class fire_failure_manager(object):
    def __init__(self, fire):
        self._fire = fire

    def __enter__(self):
        pass

    def __exit__(self, e_type, value, tb):
        if e_type:
            self._fire['error'] = str(value)
        return True # return true even if there's an error

class BaseEmissionsTest(object):

    def setup(self):
        self.fires = copy.deepcopy(FIRES)

    def _check_emissions(self, expected, actual):
        assert set(expected.keys()) == set(actual.keys())
        for p in expected:
            assert set(expected[p].keys()) == set(actual[p].keys())
            for s in expected[p]:
                assert_approx_equal(expected[p][s][0], actual[p][s][0])

class TestFepsEmissions(BaseEmissionsTest):

    EXPECTED_FIRE1_EMISSIONS = {
        'flaming': {
            'CH4': [1.146763999999999],
            'CO': [21.554359999999996],
            'CO2': [495.23994],
            'NH3': [0.3621612799999999],
            'NOx': [0.7264840000000004],
            'PM10': [2.5788380799999997],
            'PM2.5': [2.1854560000000007],
            'SO2': [0.294196],
            'VOC': [5.206068399999999]
        },
        'residual': {
            'CH4': [9.871947200000001],
            'CO': [210.20404799999997],
            'CO2': [1393.6372320000003],
            'NH3': [3.4119242240000003],
            'NOx': [0.9083631999999999],
            'PM10': [19.633610303999998],
            'PM2.5': [16.6386528],
            'SO2': [0.980392],
            'VOC': [49.04641072000001]
        },
        'smoldering': {
            'CH4': [8.886134000000002],
            'CO': [189.21305999999998],
            'CO2': [1254.46854],
            'NH3': [3.07120928],
            'NOx': [0.817654],
            'PM10': [17.67299688],
            'PM2.5': [14.977116],
            'SO2': [0.88249],
            'VOC': [44.14863340000001]
        },
        'total': {
            'CH4': [19.9048452],
            'CO': [420.97146799999996],
            'CO2': [3143.3457120000003],
            'NH3': [6.845294784],
            'NOx': [2.4525012000000004],
            'PM10': [39.885445264],
            'PM2.5': [33.8012248],
            'SO2': [2.157078],
            'VOC': [98.40111252000001]
        }
    }

    EXPECTED_FIRE1_EMISSIONS_PM_ONLY = {
        'flaming': {
            'PM10': [2.5788380799999997],
            'PM2.5': [2.1854560000000007]
        },
        'residual': {
            'PM10': [19.633610303999998],
            'PM2.5': [16.6386528]
        },
        'smoldering': {
            'PM10': [17.67299688],
            'PM2.5': [14.977116]
        },
        'total': {
            'PM10': [39.885445264],
            'PM2.5': [33.8012248]
        }
    }

    def test_wo_details(self):
        Config.set("feps", 'emissions', "model")
        Config.set(False, 'emissions', "include_emissions_details")

        emissions.Feps(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' not in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_with_details(self):
        Config.set("feps", 'emissions', "model")
        Config.set(True, 'emissions', "include_emissions_details")
        emissions.Feps(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_wo_details_PM_only(self):
        Config.set("feps", 'emissions', "model")
        Config.set(False, 'emissions', "include_emissions_details")
        Config.set(['PM2.5', 'PM10'], 'emissions', "species")
        emissions.Feps(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' not in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS_PM_ONLY,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_with_details_PM_only(self):
        Config.set("feps", 'emissions', "model")
        Config.set(True, 'emissions', "include_emissions_details")
        Config.set(['PM2.5', 'PM10'], 'emissions', "species")
        emissions.Feps(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS_PM_ONLY,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

class TestPrichardOneillEmissions(BaseEmissionsTest):

    EXPECTED_FIRE1_EMISSIONS = {
        'flaming': {
            'CH4': [0.7294860000000001],
            'CO': [15.7605],
            'CO2': [239.8598],
            'NH3': [0.22965300000000002],
            'NOx': [0.30920600000000004],
            'PM10': [3.1119632600000005],
            'PM2.5': [2.637257],
            'SO2': [0.159106]
        },
        'residual': {
            'CH4': [0.0],
            'CO': [0.0],
            'CO2': [0.0],
            'NH3': [0.0],
            'NOx': [0.0],
            'PM10': [0.0],
            'PM2.5': [0.0],
            'SO2': [0.0]
        },
        'smoldering': {
            'CH4': [2.188215],
            'CO': [47.27625],
            'CO2': [719.4995],
            'NH3': [0.6888825000000001],
            'NOx': [0.927515],
            'PM10': [9.33485315],
            'PM2.5': [7.9108925],
            'SO2': [0.47726500000000005]
        },
        'total': {
            'CH4': [2.917701],
            'CO': [63.03675],
            'CO2': [959.3593000000001],
            'NH3': [0.9185355000000001],
            'NOx': [1.236721],
            'PM10': [12.446816410000002],
            'PM2.5': [10.5481495],
            'SO2': [0.6363710000000001]
        }
    }

    SPECIES = ['CH4','CO','CO2','NH3','NOx','PM10','PM2.5','SO2','VOC']

    # Note: no tests with all emissions species, since that would be
    # a huge set

    def test_wo_details_PM_only(self):
        Config.set("prichard-oneill", 'emissions', "model")
        Config.set(False, 'emissions', "include_emissions_details")
        Config.set(self.SPECIES, 'emissions', "species")
        emissions.PrichardOneill(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' not in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_with_details_PM_only(self):
        Config.set("prichard-oneill", 'emissions', "model")
        Config.set(True, 'emissions', "include_emissions_details")
        Config.set(self.SPECIES, 'emissions', "species")
        emissions.PrichardOneill(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

class TestConsumeEmissions(BaseEmissionsTest):

    EXPECTED_FIRE1_EMISSIONS = {
        'flaming': {
            'PM': array([ 77.0587785]),
            'PM2.5': array([ 40.98871197]),
            'NMHC': array([ 14.75593631]),
            'PM10': array([ 47.13701877]),
            'CH4': array([ 12.29661359]),
            'CO': array([ 364.79953653]),
            'CO2': array([ 13940.26094093])
        },
        'residual': {
            'PM': array([ 67.18167148]),
            'PM2.5': array([ 47.27599104]),
            'NMHC': array([ 13.27045363]),
            'PM10': array([ 50.73183834]),
            'CH4': array([ 20.18214822]),
            'CO': array([ 393.96659204]),
            'CO2': array([ 4106.9289296])
        },
        'smoldering': {
            'PM': array([ 105.52324034]),
            'PM2.5': array([ 74.25709505]),
            'NMHC': array([ 20.84409686]),
            'PM10': array([ 79.68524528]),
            'CH4': array([ 31.7003973]),
            'CO': array([ 618.80912543]),
            'CO2': array([ 6450.81372514])
        },
        'total': {
            'PM': array([ 249.76369032]),
            'PM2.5': array([ 162.52179807]),
            'NMHC': array([ 48.87048679]),
            'PM10': array([ 177.55410238]),
            'CH4': array([ 64.17915912]),
            'CO': array([ 1377.575254]),
            'CO2': array([ 24498.00359567])
        }
    }

    EXPECTED_FIRE1_EMISSIONS_PM_ONLY = {
        'flaming': {
            'PM2.5': array([ 40.98871197]),
            'PM10': array([ 47.13701877])
        },
        'residual': {
            'PM2.5': array([ 47.27599104]),
            'PM10': array([ 50.73183834])
        },
        'smoldering': {
            'PM2.5': array([ 74.25709505]),
            'PM10': array([ 79.68524528])
        },
        'total': {
            'PM2.5': array([ 162.52179807]),
            'PM10': array([ 177.55410238])
        }
    }

    def test_wo_details(self):
        Config.set("consume", 'emissions', "model")
        Config.set(False, 'emissions', "include_emissions_details")
        emissions.Consume(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' not in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_with_details(self):
        Config.set("consume", 'emissions', "model")
        Config.set(True, 'emissions', "include_emissions_details")
        emissions.Consume(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_wo_details_PM_only(self):
        Config.set("consume", 'emissions', "model")
        Config.set(False, 'emissions', "include_emissions_details")
        Config.set(['PM2.5', 'PM10'], 'emissions', "species")
        emissions.Consume(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' not in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS_PM_ONLY,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])

    def test_with_details_PM_only(self):
        Config.set("consume", 'emissions', "model")
        Config.set(True, 'emissions', "include_emissions_details")
        Config.set(['PM2.5', 'PM10'], 'emissions', "species")
        emissions.Consume(fire_failure_manager).run(self.fires)

        assert self.fires[0]['error'] == (
            'Missing fuelbed data required for computing emissions')

        assert 'emissions_details' in self.fires[1]['growth'][0]['fuelbeds'][0]
        self._check_emissions(self.EXPECTED_FIRE1_EMISSIONS_PM_ONLY,
            self.fires[1]['growth'][0]['fuelbeds'][0]['emissions'])
