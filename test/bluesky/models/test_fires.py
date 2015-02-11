import io
import json
import sys
import StringIO

from py.test import raises

try:
    from bluesky.models import fires
except:
    import os

    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../../'))
    sys.path.insert(0, root_dir)
    from bluesky.models import fires

class TestFireDataFormats:
    def test_formats(self):
        assert set(['json', 'csv']) == set(fires.FireDataFormats.formats)

    def test_format_ids(self):
        assert set([1,2]) == set(fires.FireDataFormats.format_ids)

    def test_get_item(self):
        # id to format key
        assert 'json' == fires.FireDataFormats[1]
        assert 'csv' == fires.FireDataFormats[2]
        with raises(fires.FireDataFormatNotSupported) as e:
            fires.FireDataFormats[3]
        # format key to id
        assert 1 == fires.FireDataFormats['JSON']
        assert 1 == fires.FireDataFormats['json']
        assert 2 == fires.FireDataFormats['CSV']
        assert 2 == fires.FireDataFormats['csv']
        with raises(fires.FireDataFormatNotSupported) as e:
            fires.FireDataFormats['sdf']

    def test_format_attrs(self):
        assert 1 == fires.FireDataFormats.json
        assert 1 == fires.FireDataFormats.JSON
        with raises(fires.FireDataFormatNotSupported) as e:
            fires.FireDataFormats.sdf

class TestFire:

    def test_accessing_attributes(self):
        f = fires.Fire({'a': 123, 'b': 'sdf'})
        assert 123 == f['a']
        assert 123 == f.a
        assert 'sdf' == f['b']
        assert 'sdf' == f.b
        with raises(KeyError) as e:
            f['sdfdsf']
        with raises(KeyError) as e:
            f.rifsijsflj

class TestFiresImporter:

    def test_from_json_invalid_data(self):
        fires_importer = fires.FiresImporter()
        with raises(ValueError):
            fires_importer._from_json(io.StringIO(u''))
        with raises(ValueError):
            fires_importer._from_json(io.StringIO(u'""'))
        with raises(ValueError):
            fires_importer._from_json(io.StringIO(u'"sdf"'))
        with raises(ValueError):
            fires_importer._from_json(io.StringIO(u'null'))

    def test_from_json_no_fires(self):
        fires_importer = fires.FiresImporter()
        expected = []
        fires_importer._from_json(io.StringIO(u'[]'))
        assert expected == fires_importer.fires

    def test_from_json_one_fire_single_object(self):
        fires_importer = fires.FiresImporter()
        expected = [
            fires.Fire({'foo':'a', 'bar':123, 'baz':12.32, 'bee': "12.12"})
        ]
        fires_importer._from_json(io.StringIO(
            u'{"foo":"a","bar":123,"baz":12.32,"bee":"12.12"}'))
        assert expected == fires_importer.fires

    def test_from_json_one_fire_array(self):
        fires_importer = fires.FiresImporter()
        expected = [
            fires.Fire({'foo':'a', 'bar':123, 'baz':12.32, 'bee': "12.12"})
        ]
        fires_importer._from_json(io.StringIO(
            u'[{"foo":"a","bar":123,"baz":12.32,"bee":"12.12"}]'))
        assert expected == fires_importer.fires

    def test_from_json_multiple_fires(self):
        fires_importer = fires.FiresImporter()
        expected = [
            fires.Fire({'foo':'a', 'bar':123, 'baz':12.32, 'bee': "12.12"}),
            fires.Fire({'foo':'b', 'bar':2, 'baz': 1.1, 'bee': '24.34'})
        ]
        fires_importer._from_json(io.StringIO(
            u'[{"foo":"a","bar":123,"baz":12.32,"bee":"12.12"},'
              '{"foo":"b","bar":2, "baz": 1.1, "bee":"24.34"}]'))
        assert expected == fires_importer.fires

    def test_from_csv_no_fires(self):
        fires_importer = fires.FiresImporter()
        fires_importer._from_csv(io.StringIO(u'foo,bar, baz, bee '))
        expected = []
        assert expected == fires_importer.fires

    def test_from_csv_one_fire(self):
        fires_importer = fires.FiresImporter()
        expected = [{'foo':'a', 'bar':123, 'baz': 23.23, 'bee': 23.23 }]
        fires_importer._from_csv(io.StringIO(
            u'foo,bar, baz, bee \n a, 123, 23.23,"23.23"'))
        assert expected == fires_importer.fires

    def test_from_csv_multiple_fires(self):
        fires_importer = fires.FiresImporter()
        expected = [
            fires.Fire({'foo':'a', 'bar':123, 'baz': 23.23, 'bee': 23.23 }),
            fires.Fire({'foo':'b', 'bar':2, 'baz':1.2, "bee": 12.23})
        ]
        fires_importer._from_csv(io.StringIO(
            u'foo,bar, baz, bee \n a, 123, 23.23,"23.23"\nb,2, 1.2,"12.23"'))
        assert expected == fires_importer.fires

    def test_to_json(self):
        pass

    def test_to_csv(self):
        pass

    def test_full_cycle(self, monkeypatch):
        fires_importer = fires.FiresImporter()
        def _stream(self, file_name, flag):
            if flag == 'r':
                self._calls = getattr(self, '_calls', 0) + 1
                return StringIO.StringIO(
                    u'foo%d,bar%d,baz \n'
                     ' %d, a%d,baz%d\n'
                     'b%d,%d,baz%d' % (
                        self._calls, self._calls, self._calls, self._calls,
                        self._calls, self._calls, self._calls, self._calls)
                )
            else:
                self._output = getattr(self, 'output', StringIO.StringIO())
                return self._output
        monkeypatch.setattr(fires.FiresImporter, '_stream', _stream)

        fires_importer.loads(format=fires.FireDataFormats.csv)
        expected = [
            fires.Fire({'foo1':1, 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'foo1': 'b1', 'bar1': 1 , 'baz':'baz1'})
        ]
        assert expected == fires_importer.fires

        fires_importer.loads(format=fires.FireDataFormats.csv)
        expected = [
            fires.Fire({'foo1':1, 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'foo1': 'b1', 'bar1': 1 , 'baz':'baz1'}),
            fires.Fire({'foo2':2, 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'foo2': 'b2', 'bar2': 2 , 'baz':'baz2'})
        ]
        assert expected == fires_importer.fires

        expected = "foo1,bar1,baz,foo2,bar2\n1,a1,baz1,,\nb1,1,baz1,,\n,,baz2,2,a2\n,,baz2,b2,2\n"
        fires_importer.dumps(format=fires.FireDataFormats.csv)
        assert expected == fires_importer._output.getvalue()

        fires_importer._output = StringIO.StringIO()
        fires_importer.dumps()
        expected = [
            {'foo1':1, 'bar1':'a1', 'baz':'baz1'},
            {'foo1': 'b1', 'bar1': 1 , 'baz':'baz1'},
            {'foo2':2, 'bar2':'a2', 'baz':'baz2'},
            {'foo2': 'b2', 'bar2': 2 , 'baz':'baz2'}
        ]
        assert expected == json.loads(fires_importer._output.getvalue())

        def _new_json_stream(self, file_name, flag):
            if flag == 'r':
                return StringIO.StringIO(
                    u'{"fooj":"j","barj":"jj","baz":99}'
                 )
            else:
                self._output = getattr(self, 'output', StringIO.StringIO())
                return self._output
        monkeypatch.setattr(fires.FiresImporter, '_stream', _new_json_stream)

        fires_importer.loads(format=fires.FireDataFormats.json)
        expected = [
            fires.Fire({'foo1':1, 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'foo1': 'b1', 'bar1': 1 , 'baz':'baz1'}),
            fires.Fire({'foo2':2, 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'foo2': 'b2', 'bar2': 2 , 'baz':'baz2'}),
            fires.Fire({"fooj": "j", "barj": "jj", "baz": 99})
        ]
        assert expected == fires_importer.fires

        expected = "foo1,bar1,baz,foo2,bar2,barj,fooj\n1,a1,baz1,,,,\nb1,1,baz1,,,,\n,,baz2,2,a2,,\n,,baz2,b2,2,,\n,,99,,,jj,j\n"
        fires_importer._output = StringIO.StringIO()
        fires_importer.dumps(format=fires.FireDataFormats.csv)
        assert expected == fires_importer._output.getvalue()

    def test_filter(self):
        fires_importer = fires.FiresImporter()
        fires_importer._fires = [
            fires.Fire({'dfd':'a1', 'baz':'baz1'}),
            fires.Fire({'bar':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "ZZ", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "USA", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': '', 'bar1': 1 , 'baz':'baz1'}),
            fires.Fire({'country': "CA", 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'country': "CA", 'bar2':'adfsdf', 'baz':'baz2'}),
            fires.Fire({'country': 'Unknown', 'bar2': 2 , 'baz':'baz2'}),
            fires.Fire({"country": "USA", "barj": "jj", "baz": 99}),
            fires.Fire({"country": "BZ", "barj": "jj", "baz": 99})
        ]

        fires_importer.filter('country', blacklist=["ZZ"])
        expected = [
            fires.Fire({'dfd':'a1', 'baz':'baz1'}),
            fires.Fire({'bar':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "USA", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': '', 'bar1': 1 , 'baz':'baz1'}),
            fires.Fire({'country': "CA", 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'country': "CA", 'bar2':'adfsdf', 'baz':'baz2'}),
            fires.Fire({'country': 'Unknown', 'bar2': 2 , 'baz':'baz2'}),
            fires.Fire({"country": "USA", "barj": "jj", "baz": 99}),
            fires.Fire({"country": "BZ", "barj": "jj", "baz": 99})
        ]
        assert expected == fires_importer.fires

        fires_importer.filter('country', whitelist=["USA", "CA", "UK", "BZ"])
        expected = [
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "USA", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "CA", 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'country': "CA", 'bar2':'adfsdf', 'baz':'baz2'}),
            fires.Fire({"country": "USA", "barj": "jj", "baz": 99}),
            fires.Fire({"country": "BZ", "barj": "jj", "baz": 99})
        ]
        assert expected == fires_importer.fires

        fires_importer.filter('country', blacklist=["USA"])
        expected = [
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "CA", 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'country': "CA", 'bar2':'adfsdf', 'baz':'baz2'}),
            fires.Fire({"country": "BZ", "barj": "jj", "baz": 99})
        ]
        assert expected == fires_importer.fires

        fires_importer.filter('country', whitelist=["USA", "CA", "UK"])
        expected = [
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
            fires.Fire({'country': "CA", 'bar2':'a2', 'baz':'baz2'}),
            fires.Fire({'country': "CA", 'bar2':'adfsdf', 'baz':'baz2'})
        ]
        assert expected == fires_importer.fires

        fires_importer.filter('country', blacklist=["USA", "CA"])
        expected = [
            fires.Fire({'country': "UK", 'bar1':'a1', 'baz':'baz1'}),
        ]
        assert expected == fires_importer.fires
