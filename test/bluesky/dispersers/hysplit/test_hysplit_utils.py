"""Unit tests for hysplit_utils.

Run with py.test:
    > pip install pytest
    > py.test /path/to/hsyplit49/test/test_hysplit_utils.py
"""

import datetime
import time
import timecop

from bluesky.dispersers.hysplit import hysplit_utils

class MockFireLocationData(object):
    def __init__(self, location_id):
        self.id = location_id

    def __repr__(self):
        return "<%s %d, location_id: %d>" % (self.__class__.__name__, id(self), self.id)
    # __str__ = __repr__

class TestHysplitUtils(object):

    def test_create_fire_sets(self):
        fires = [
            MockFireLocationData(1),
            MockFireLocationData(2),
            MockFireLocationData(1),
            MockFireLocationData(4),
            MockFireLocationData(4),
            MockFireLocationData(100),
            MockFireLocationData(3),
            MockFireLocationData(1),
            MockFireLocationData(1)
        ]
        expected_sets = [
            [fires[0], fires[2], fires[7], fires[8]],  # id 1
            [fires[1]],  # id 2
            [fires[6]],  # id 3
            [fires[3], fires[4]],  # id 4
            [fires[5]]  #id 100
        ]
        fire_sets = hysplit_utils.create_fire_sets(fires)
        # Note: The following assumes that, in create_fire_sets,
        # filtered_fires_dict.values() returns sets ordered by the dict keys
        # (i.e. location id)
        assert expected_sets == fire_sets

    def test_create_fire_tranches(self):
        fire_sets = [
            [MockFireLocationData(1), MockFireLocationData(1)],
            [MockFireLocationData(3), MockFireLocationData(3)],
            [MockFireLocationData(7), MockFireLocationData(7)],
            [MockFireLocationData(22), MockFireLocationData(22)]
        ]

        # 4 fires locations, 5 proceses  <-- should assume only 4 processes
        expected_tranches = [
            [fire_sets[0][0], fire_sets[0][1]],
            [fire_sets[1][0], fire_sets[1][1]],
            [fire_sets[2][0], fire_sets[2][1]],
            [fire_sets[3][0], fire_sets[3][1]]
        ]
        fire_tranches = hysplit_utils.create_fire_tranches(fire_sets, 5)
        assert expected_tranches == fire_tranches

        # 4 fires locations, 4 proceses  <-- same expected set as when called with num_processes = 5
        fire_tranches = hysplit_utils.create_fire_tranches(fire_sets, 4)
        assert expected_tranches == fire_tranches

        # 4 fires locations, 3 proceses
        expected_tranches = [
            [fire_sets[0][0], fire_sets[0][1],
             fire_sets[1][0], fire_sets[1][1]],
            [fire_sets[2][0], fire_sets[2][1]],
            [fire_sets[3][0], fire_sets[3][1]]
        ]
        fire_tranches = hysplit_utils.create_fire_tranches(fire_sets, 3)
        assert expected_tranches == fire_tranches

        # 4 fires locations, 2 proceses
        expected_tranches = [
            [fire_sets[0][0], fire_sets[0][1],
             fire_sets[1][0], fire_sets[1][1]],
            [fire_sets[2][0], fire_sets[2][1],
             fire_sets[3][0], fire_sets[3][1]]
        ]
        fire_tranches = hysplit_utils.create_fire_tranches(fire_sets, 2)
        assert expected_tranches == fire_tranches

        # 4 fires locations, 1 proceses
        expected_tranches = [
            [fire_sets[0][0], fire_sets[0][1],
             fire_sets[1][0], fire_sets[1][1],
             fire_sets[2][0], fire_sets[2][1],
             fire_sets[3][0], fire_sets[3][1]]
        ]
        fire_tranches = hysplit_utils.create_fire_tranches(fire_sets, 1)
        assert expected_tranches == fire_tranches

    def test_compute_num_processes(self):
        n = hysplit_utils.compute_num_processes(4)
        assert isinstance(n, int) and n == 1

        n = hysplit_utils.compute_num_processes(4, num_processes=0,
            num_fires_per_process=0, num_processes_max=0)
        assert isinstance(n, int) and n == 1

        n = hysplit_utils.compute_num_processes(4, num_processes=1,
            num_fires_per_process=0, num_processes_max=0)
        assert isinstance(n, int) and n == 1

        n = hysplit_utils.compute_num_processes(4, num_processes=0,
            num_fires_per_process=1, num_processes_max=3)
        assert isinstance(n, int) and n == 3

        n = hysplit_utils.compute_num_processes(6, num_processes=0,
            num_fires_per_process=2, num_processes_max=4)
        assert isinstance(n, int) and n == 3

        n = hysplit_utils.compute_num_processes(4, num_processes=2,
            num_fires_per_process=1, num_processes_max=3)
        assert isinstance(n, int) and n == 2

        n = hysplit_utils.compute_num_processes(4, num_processes=0,
            num_fires_per_process=2, num_processes_max=3)
        assert isinstance(n, int) and n == 2

        n = hysplit_utils.compute_num_processes(4, num_processes=0,
            num_fires_per_process=2, num_processes_max=1)
        assert isinstance(n, int) and n == 1

class TestKmPerLng(self):

    def test_basic(self):
        assert 111.32 == hysplit_utils.km_per_deg_lng(0)
        assert 78.71512688168647 == hysplit_utils.km_per_deg_lng(45)
        assert 0 == hysplit_utils.km_per_deg_lng(90)

class TestSquareGridFromLatLng(object):

    def test_basic(self):
        e = {
            "centerLat": 45.0,
            "centerLon": -118.0,
            "heightLat": 0.9009009009009009,
            "widthLon": 1.2704038469036067,
            "spacingLon": hysplit_utils.DOMAINS['NAM84']['boundary']['spacing_longitude'],
            "spacingLat": hysplit_utils.DOMAINS['NAM84']['boundary']['spacing_latitude']
        }
        assert e == hysplit_utils.square_grid_from_lat_lng(45.0, -118.0, 100, 'NAM84')

    # TODO: test location that could cross pole
    # TODO: test location that could equator
    # TODO: test any invalid cases


if __name__ == '__main__':
    test_main(verbose=True)
