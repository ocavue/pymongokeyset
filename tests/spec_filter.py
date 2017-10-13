from base import BaseTestCase
from pymongokeyset import get_keyset_cursor
import unittest
from pymongo import DESCENDING, ASCENDING


class SpecTestCase(BaseTestCase):
    objs = [{
        'a': {
            'b': i
        },
    } for i in range(100)]

    def test_next(self):
        params = dict(collection=self.collect, sort=[['a.b', 1]], limit=20)

        cursor1 = get_keyset_cursor(**params)
        self.assertEqual([i['a']['b'] for i in cursor1], list(range(0, 20)))

        cursor2 = get_keyset_cursor(**params, position=cursor1.paging.position)
        self.assertEqual([i['a']['b'] for i in cursor2], list(range(20, 40)))

        cursor1 = get_keyset_cursor(**params, position=cursor2.paging.position, backwards=True)
        self.assertEqual([i['a']['b'] for i in cursor1], list(range(0, 20)))


class SortTestCase(BaseTestCase):
    objs = [{'a': i} for i in range(10)]

    def test_asc_num(self):
        cursor = get_keyset_cursor(sort=[['a', 1]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in cursor], [0, 1, 2])

    def test_desc_num(self):
        cursor = get_keyset_cursor(sort=[['a', -1]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in cursor], [9, 8, 7])

    def test_asc_arg(self):
        cursor = get_keyset_cursor(sort=[['a', ASCENDING]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in cursor], [0, 1, 2])

    def test_desc_arg(self):
        cursor = get_keyset_cursor(sort=[['a', DESCENDING]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in cursor], [9, 8, 7])


class FilterTestCase(BaseTestCase):
    objs = [{'_id': i, 'a': i, 'b': i % 2} for i in range(10)]

    def test_single_filter(self):
        params = dict(filter={'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)

        cursor1 = get_keyset_cursor(**params)
        self.assertEqual([i['a'] for i in cursor1], [0, 2])

        cursor2 = get_keyset_cursor(**params, position=cursor1.paging.position)
        self.assertEqual([i['a'] for i in cursor2], [4, 6])

    def test_mulit_filter(self):
        params = dict(filter={'a': {'$gt': 0}, 'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)

        cursor1 = get_keyset_cursor(**params)
        self.assertEqual([i['a'] for i in cursor1], [2, 4])

        cursor2 = get_keyset_cursor(**params, position=cursor1.paging.position)
        self.assertEqual([i['a'] for i in cursor2], [6, 8])


class ProjectionTestCase(BaseTestCase):
    objs = [{'a': i, 'b': i} for i in range(10)]

    def test_default_projection(self):
        cursor1 = get_keyset_cursor(filter={'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)
        self.assertEqual(cursor1[0].get('b'), 0)

    def test_inclusion_projection(self):
        condictions = dict(limit=2, sort=[['a', 1]], collection=self.collect)

        for projection in [{'b': 1}, {'b': 1, '_id': 1}, {'b': 1, '_id': 0}]:
            with self.assertRaises(ValueError):
                get_keyset_cursor(**condictions, projection=projection)

    def test_exclusion_projection(self):
        condictions = dict(limit=2, sort=[['a', 1], ['b', 1]], collection=self.collect)

        for projection in [{'b': 0}, {'b': 0, '_id': 1}, {'b': 0, '_id': 0}]:
            with self.assertRaises(ValueError):
                get_keyset_cursor(**condictions, projection=projection)


if __name__ == '__main__':
    unittest.main()
