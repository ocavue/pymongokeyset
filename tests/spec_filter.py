from base import BaseTestCase
from pymongo_keyset import get_page
from copy import deepcopy
import unittest
from pymongo import DESCENDING, ASCENDING


class SpecTestCase(BaseTestCase):
    objs = [{
        'a': {
            'b': i
        },
    } for i in range(100)]

    def test_next(self):
        cursor = self.collect.find({}).sort([['a.b', 1]])
        page1 = get_page(deepcopy(cursor), limit=20)
        self.assertEqual([i['a']['b'] for i in page1], list(range(0, 20)))

        page2 = get_page(deepcopy(cursor), limit=20, position=page1.paging.next_position)
        self.assertEqual([i['a']['b'] for i in page2], list(range(20, 40)))

    def test_previous(self):
        cursor = self.collect.find({}).sort([['a.b', 1]])
        page1 = get_page(deepcopy(cursor), limit=20)
        page2 = get_page(deepcopy(cursor), limit=20, position=page1.paging.next_position)
        page1 = get_page(deepcopy(cursor), limit=20, position=page2.paging.previous_position)

        self.assertEqual([i['a']['b'] for i in page1], list(range(0, 20)))

    def test_end(self):
        cursor = self.collect.find({}).sort([['a.b', 1]])
        page1 = get_page(deepcopy(cursor), limit=30)
        page2 = get_page(deepcopy(cursor), limit=30, position=page1.paging.next_position)
        page3 = get_page(deepcopy(cursor), limit=30, position=page2.paging.next_position)
        page4 = get_page(deepcopy(cursor), limit=30, position=page3.paging.next_position)

        self.assertEqual([i['a']['b'] for i in page4], list(range(90, 100)))
        self.assertEqual(page4.paging.has_next, False)


class SortTestCase(BaseTestCase):
    objs = [{'a': i} for i in range(10)]

    def test_asc_num(self):
        page1 = get_page(self.collect.find({}).sort([['a', 1]]), limit=3)
        self.assertEqual([i['a'] for i in page1], [0, 1, 2])

    def test_desc_num(self):
        page1 = get_page(self.collect.find({}).sort([['a', -1]]), limit=3)
        self.assertEqual([i['a'] for i in page1], [9, 8, 7])

    def test_asc_arg(self):
        page1 = get_page(self.collect.find({}).sort([['a', ASCENDING]]), limit=3)
        self.assertEqual([i['a'] for i in page1], [0, 1, 2])

    def test_desc_arg(self):
        page1 = get_page(self.collect.find({}).sort([['a', DESCENDING]]), limit=3)
        self.assertEqual([i['a'] for i in page1], [9, 8, 7])


class FilterTestCase(BaseTestCase):
    objs = [{'_id': i, 'a': i, 'b': i % 2} for i in range(10)]

    def test_single_filter(self):
        cursor = self.collect.find({'b': 0}).sort([['a', 1]])

        page1 = get_page(deepcopy(cursor), limit=2)
        self.assertEqual([i['a'] for i in page1], [0, 2])

        page2 = get_page(deepcopy(cursor), limit=2, position=page1.paging.next_position)
        self.assertEqual([i['a'] for i in page2], [4, 6])

    def test_mulit_filter(self):
        cursor = self.collect.find({'a': {'$gt': 0}, 'b': 0}).sort([['a', 1]])

        page1 = get_page(deepcopy(cursor), limit=2)
        self.assertEqual([i['a'] for i in page1], [2, 4])

        page2 = get_page(deepcopy(cursor), limit=2, position=page1.paging.next_position)
        self.assertEqual([i['a'] for i in page2], [6, 8])


class ProjectionTestCase(BaseTestCase):
    objs = [{'a': i, 'b': i} for i in range(10)]

    def test_default_projection(self):
        page1 = get_page(self.collect.find({}).sort([['a', 1]]), limit=2)
        self.assertEqual(page1[0].get('b'), 0)

    def test_inclusion_projection(self):
        for projection in [{'b': 1}, {'b': 1, '_id': 1}, {'b': 1, '_id': 0}]:
            page1 = get_page(self.collect.find({}, projection).sort([['a', 1]]), limit=2)
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)

            page2 = get_page(
                self.collect.find({}, projection).sort([['a', 1]]), limit=2, position=page1.paging.next_position
            )
            self.assertEqual(page2[0].get('b'), 2)
            self.assertEqual(page2[0].get('a'), 2)

            page1 = get_page(
                self.collect.find({}, projection).sort([['a', 1]]),
                limit=2,
                position=page2.paging.previous_position
            )
            self.assertEqual(page1[0].get('b'), 0)
            self.assertEqual(page1[0].get('a'), 0)

    def test_exclusion_projection(self):
        for projection in [{'b': 0}, {'b': 0, '_id': 1}, {'b': 0, '_id': 0}]:
            page1 = get_page(self.collect.find({}, projection).sort([['a', 1]]), limit=2)
            self.assertEqual(page1[0].get('b'), None)
            self.assertEqual(page1[0].get('a'), 0)

            page2 = get_page(
                self.collect.find({}, projection).sort([['a', 1]]), limit=2, position=page1.paging.next_position
            )
            self.assertEqual(page2[0].get('b'), None)
            self.assertEqual(page2[0].get('a'), 2)

            page1 = get_page(
                self.collect.find({}, projection).sort([['a', 1]]),
                limit=2,
                position=page2.paging.previous_position
            )
            self.assertEqual(page2[0].get('b'), None)
            self.assertEqual(page2[0].get('a'), 2)


if __name__ == '__main__':
    unittest.main()
