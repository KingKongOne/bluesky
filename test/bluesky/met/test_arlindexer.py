"""Unit tests for bluesky.arlindexer"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import datetime
import time
import tempfile

import timecop
from py.test import raises

from bluesky.met import arlindexer

class TestARLIndexer(object):

    def setup(self):
        self.arl_indexer = arlindexer.ArlIndexer('DRI6km', tempfile.mkdtemp())

    def test_filter(self):
        files_per_hour = {
            datetime.datetime(2015,1,1,23,0,0): 'a',
            datetime.datetime(2015,1,2,0,0,0): 'b',
            datetime.datetime(2015,1,2,1,0,0): 'b',
            datetime.datetime(2015,1,2,2,0,0): 'b',
            datetime.datetime(2015,1,2,3,0,0): 'c',
            datetime.datetime(2015,1,2,4,0,0): 'd',
            datetime.datetime(2015,1,2,5,0,0): 'd',
            datetime.datetime(2015,1,2,6,0,0): 'd'
        }

        files = [
            {
                'file': 'a',
                'first_hour': datetime.datetime(2015,1,1,23,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour': datetime.datetime(2015,1,2,6,0,0)
            }
        ]
        n = datetime.datetime.utcnow()
        assert files_per_hour, files == self.arl_indexer._filter(
            files_per_hour, files, None, None)
        assert files_per_hour, files == self.arl_indexer._filter(
            files_per_hour, files, n, None)
        assert files_per_hour, files == self.arl_indexer._filter(
            files_per_hour, files, None, n)

        s = datetime.datetime(2015,1,2,1,0,0)
        e = datetime.datetime(2015,1,2,3,0,0)
        expected_fph = {
            datetime.datetime(2015,1,2,1,0,0): 'b',
            datetime.datetime(2015,1,2,2,0,0): 'b',
            datetime.datetime(2015,1,2,3,0,0): 'c'
        }
        expected_f = [
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            }
        ]
        assert expected_fph, expected_f == self.arl_finder._filter_files(
            files, files_per_hour, s, e)



    def test_fill_in_start_end(self):
        # case where neither start nor end is defined; they are returned
        # as is (as None values)
        s = e = None
        assert (None, None) == self.arl_indexer._fill_in_start_end(s, e)

        # case where end is defined but start isn't (invalid); exception raised
        e = datetime.datetime.utcnow()
        with raises(ValueError) as e_info:
            self.arl_indexer._fill_in_start_end(s, e)
        assert arlindexer.ArlIndexer.END_WITHOUT_START_ERR_MSG == e_info.value.message

        # case where start is after end (invalid); exception raised
        s = e + datetime.timedelta(1)
        with raises(ValueError) as e_info:
            self.arl_indexer._fill_in_start_end(s, e)
        assert arlindexer.ArlIndexer.START_AFTER_END_ERR_MSG == e_info.value.message

        # case where start is before end (valid); they are returned as is
        s = e - datetime.timedelta(1)
        assert s, e == self.arl_indexer._fill_in_start_end(s, e)

        # case where start is defined but not end; end gets set to now
        with timecop.freeze(time.mktime(e.timetuple())):
            assert s, e == self.arl_indexer._fill_in_start_end(s, None)

    def test_analyse(self):
        files_per_hour = {
            datetime.datetime(2015,1,1,23,0,0): 'a',
            datetime.datetime(2015,1,2,0,0,0): 'b',
            datetime.datetime(2015,1,2,1,0,0): 'b',
            datetime.datetime(2015,1,2,2,0,0): 'b',
            datetime.datetime(2015,1,2,3,0,0): 'c',
            datetime.datetime(2015,1,2,4,0,0): 'd',
            datetime.datetime(2015,1,2,5,0,0): 'd',
            datetime.datetime(2015,1,2,6,0,0): 'd',
            datetime.datetime(2015,1,2,7,0,0): 'd',
            datetime.datetime(2015,1,2,8,0,0): 'd',
            datetime.datetime(2015,1,2,9,0,0): 'd',
            datetime.datetime(2015,1,2,10,0,0): 'd',
            datetime.datetime(2015,1,2,11,0,0): 'd',
            datetime.datetime(2015,1,2,12,0,0): 'd',
            datetime.datetime(2015,1,2,13,0,0): 'd',
            datetime.datetime(2015,1,2,14,0,0): 'd',
            datetime.datetime(2015,1,2,15,0,0): 'd',
            datetime.datetime(2015,1,2,16,0,0): 'd',
            datetime.datetime(2015,1,2,17,0,0): 'd',
            datetime.datetime(2015,1,2,18,0,0): 'd',
            datetime.datetime(2015,1,2,19,0,0): 'd',
            datetime.datetime(2015,1,2,20,0,0): 'd',
            datetime.datetime(2015,1,2,21,0,0): 'd',
            datetime.datetime(2015,1,2,22,0,0): 'd',
            datetime.datetime(2015,1,2,23,0,0): 'd'
        }

        files = [
            {
                'file': 'a',
                'first_hour': datetime.datetime(2015,1,1,23,0,0),
                'last_hour': datetime.datetime(2015,1,1,23,0,0)
            },
            {
                'file': 'b',
                'first_hour': datetime.datetime(2015,1,2,0,0,0),
                'last_hour': datetime.datetime(2015,1,2,2,0,0)
            },
            {
                'file': 'c',
                'first_hour': datetime.datetime(2015,1,2,3,0,0),
                'last_hour': datetime.datetime(2015,1,2,3,0,0)
            },
            {
                'file': 'd',
                'first_hour': datetime.datetime(2015,1,2,4,0,0),
                'last_hour': datetime.datetime(2015,1,2,23,0,0)
            }
        ]

        expected = {
            'complete_dates': [datetime.date(2015,1,2)],
            'partial_dates': [datetime.date(2015,1,1)],
            'root_dir': self.arl_indexer._met_root_dir,
            'files': files
        }

    # TODO: test _write
    # TODO: test _write_to_mongodb_url
    # TODO: test _write_to_output_file


class TestArlIndexDB(object):

    def test_parse_mongodb_url(self):
        # aliases to make code less verbose
        call = arlindexer.ArlIndexDB._parse_mongodb_url
        invalid_error_msg = arlindexer.ArlIndexDB.INVALID_MONGODB_URL_ERR_MSG
        default_db = arlindexer.ArlIndexDB.DEFAULT_DB_NAME
        # mongodb url format: "mongodb://[username:password@]host[:port][/[database][?options]]"

        with raises(ValueError) as e_info:
            call("localhost")
        assert e_info.value.message == invalid_error_msg

        with raises(ValueError) as e_info:
            call("sdfmongodb://localhost")
        assert e_info.value.message == invalid_error_msg

        with raises(ValueError) as e_info:
            call("mongodb://:sdf@localhost")
        assert e_info.value.message == invalid_error_msg

        ## using default db name

        e = ("mongodb://localhost/{}".format(default_db), default_db)
        assert e == call("mongodb://localhost")
        assert e == call("mongodb://localhost/")

        e = ("mongodb://foo:bar@localhost/{}".format(default_db), default_db)
        assert e == call("mongodb://foo:bar@localhost")
        assert e == call("mongodb://foo:bar@localhost/")

        e = ("mongodb://localhost:2222/{}".format(default_db), default_db)
        assert e == call("mongodb://localhost:2222")
        assert e == call("mongodb://localhost:2222/")

        e = ("mongodb://localhost/{}?foo=bar".format(default_db), default_db)
        assert e == call("mongodb://localhost?foo=bar")
        assert e == call("mongodb://localhost/?foo=bar")

        e = ("mongodb://u:p@localhost:2323/{}?foo=bar".format(default_db), default_db)
        assert e == call("mongodb://u:p@localhost:2323?foo=bar")
        assert e == call("mongodb://u:p@localhost:2323/?foo=bar")

        ## custom db name

        e = ("mongodb://localhost/sdf", "sdf")
        assert e == call("mongodb://localhost/sdf")
        e = ("mongodb://localhost/sdf/", "sdf")
        assert e == call("mongodb://localhost/sdf/")

        e = ("mongodb://foo:bar@localhost/sdf", "sdf")
        assert e == call("mongodb://foo:bar@localhost/sdf")
        e = ("mongodb://foo:bar@localhost/sdf/", "sdf")
        assert e == call("mongodb://foo:bar@localhost/sdf/")

        e = ("mongodb://localhost:2000/sdf", "sdf")
        assert e == call("mongodb://localhost:2000/sdf")
        e = ("mongodb://localhost:2000/sdf/", "sdf")
        assert e == call("mongodb://localhost:2000/sdf/")

        e = ("mongodb://localhost/sdf?foo=bar", "sdf")
        assert e == call("mongodb://localhost/sdf?foo=bar")
        e = ("mongodb://localhost/sdf/?foo=bar", "sdf")
        assert e == call("mongodb://localhost/sdf/?foo=bar")

        e = ("mongodb://u:p@localhost:34343/sdf?foo=bar", "sdf")
        assert e == call("mongodb://u:p@localhost:34343/sdf?foo=bar")
        e = ("mongodb://u:p@localhost:34343/sdf/?foo=bar", "sdf")
        assert e == call("mongodb://u:p@localhost:34343/sdf/?foo=bar")
