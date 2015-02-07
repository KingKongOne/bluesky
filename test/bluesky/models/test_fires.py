from py.test import raises

try:
    from bluesky.models import fires
except:
    import os
    import sys
    root_dir = os.path.abspath(os.path.join(sys.path[0], '../../../'))
    sys.path.insert(0, root_dir)
    from bluesky.models import fires

class TestFireDataFormats:
    def test_formats(self):
        assert set(['json', 'csv']) == set(fires.FireDataFormats.formats)

    def test_get_format_str(self):
        assert 'json' == fires.FireDataFormats.get_format_str(1)
        assert 'csv' == fires.FireDataFormats.get_format_str(2)
        assert None == fires.FireDataFormats.get_format_str(3)

    def test_format_attrs(self):
        assert 1 == fires.FireDataFormats.json
        assert 1 == fires.FireDataFormats.JSON
        with raises(fires.FireDataFormatNotSupported) as e:
            fires.FireDataFormats.sdf

class TestFires:

    def test_from_json(self):
        with raises(ValueError):
            fires.Fire.from_json('')
        with raises(ValueError):
            fires.Fire.from_json('""')
        with raises(ValueError):
            fires.Fire.from_json('"sdf"')
        with raises(ValueError):
            fires.Fire.from_json('null')

        assert [] == fires.Fire.from_json(['[]'])

        # TODO: test case of single fire object
        # TODO: test case of non-empty array of fire objects

    def test_from_csv(self):
        expected = []
        assert expected == fires.Fire.from_json(['foo, bar'])
        expected.append({'foo':'a', 'bar':123})
        assert expected == fires.Fire.from_json(['foo, bar'],['a',123])
        expected.append({'foo':'b', 'bar':2})
        assert expected == fires.Fire.from_json(['foo, bar'],['a',123], ['b', 2])
