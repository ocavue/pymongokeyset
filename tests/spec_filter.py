from base import BaseTestCase
from pymongokeyset import get_keyset_cursor as get_page
import unittest
from pymongo import DESCENDING, ASCENDING


class SpecTestCase(BaseTestCase):
    objs = [{
        'a': {
            'b': i
        },
    } for i in range(100)]

    def test_next(self):
        page1 = get_page(collection=self.collect, sort=[['a.b', 1]], limit=20)
        self.assertEqual([i['a']['b'] for i in page1], list(range(0, 20)))

        page2 = get_page(collection=self.collect, sort=[['a.b', 1]], limit=20, position=page1.paging.next_position)
        self.assertEqual([i['a']['b'] for i in page2], list(range(20, 40)))

        page1 = get_page(collection=self.collect, sort=[['a.b', 1]], limit=20, position=page2.paging.previous_position)
        self.assertEqual([i['a']['b'] for i in page1], list(range(0, 20)))


class SortTestCase(BaseTestCase):
    objs = [{'a': i} for i in range(10)]

    def test_asc_num(self):
        page1 = get_page(sort=[['a', 1]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in page1], [0, 1, 2])

    def test_desc_num(self):
        page1 = get_page(sort=[['a', -1]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in page1], [9, 8, 7])

    def test_asc_arg(self):
        page1 = get_page(sort=[['a', ASCENDING]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in page1], [0, 1, 2])

    def test_desc_arg(self):
        page1 = get_page(sort=[['a', DESCENDING]], limit=3, collection=self.collect)
        self.assertEqual([i['a'] for i in page1], [9, 8, 7])


class FilterTestCase(BaseTestCase):
    objs = [{'_id': i, 'a': i, 'b': i % 2} for i in range(10)]

    def test_single_filter(self):
        params = dict(filter={'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)

        page1 = get_page(**params)
        self.assertEqual([i['a'] for i in page1], [0, 2])

        page2 = get_page(**params, position=page1.paging.next_position)
        self.assertEqual([i['a'] for i in page2], [4, 6])

    def test_mulit_filter(self):
        params = dict(filter={'a': {'$gt': 0}, 'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)

        page1 = get_page(**params)
        self.assertEqual([i['a'] for i in page1], [2, 4])

        page2 = get_page(**params, position=page1.paging.next_position)
        self.assertEqual([i['a'] for i in page2], [6, 8])


class ProjectionTestCase(BaseTestCase):
    objs = [{'a': i, 'b': i} for i in range(10)]

    def test_default_projection(self):
        cursor1 = get_page(filter={'b': 0}, limit=2, sort=[['a', 1]], collection=self.collect)
        self.assertEqual(cursor1[0].get('b'), 0)

    def test_inclusion_projection(self):
        condictions = dict(limit=2, sort=[['a', 1]], collection=self.collect)

        for projection in [{'b': 1}, {'b': 1, '_id': 1}, {'b': 1, '_id': 0}]:
            cursor1 = get_page(**condictions, projection=projection)
            page1 = list(cursor1)
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)

            cursor2 = get_page(**condictions, projection=projection, position=cursor1.paging.next_position)
            page2 = list(cursor2)
            self.assertEqual(page2[0].get('b'), 2)
            self.assertEqual(page2[0].get('a'), 2)

            cursor1 = get_page(**condictions, projection=projection, position=cursor2.paging.previous_position)
            page1 = list(cursor1)
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)

    def test_exclusion_projection(self):
        condictions = dict(limit=2, sort=[['a', 1]], collection=self.collect)

        for projection in [{'b': 0}, {'b': 0, '_id': 1}, {'b': 0, '_id': 0}]:
            cursor1 = get_page(**condictions, projection=projection)
            page1 = list(cursor1)
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)

            cursor2 = get_page(**condictions, projection=projection, position=cursor1.paging.next_position)
            page2 = list(cursor2)
            self.assertEqual(page2[0].get('b'), 2)
            self.assertEqual(page2[0].get('a'), 2)

            cursor1 = get_page(**condictions, projection=projection, position=cursor2.paging.previous_position)
            page1 = list(cursor1)
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)


if __name__ == '__main__':
    unittest.main()
