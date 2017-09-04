from base import BaseTestCase
import unittest
from pymongokeyset import get_page

HALF = 5000
ALL = HALF * 2


class SingoSortTestCase(BaseTestCase):
    objs = [{"_id": i} for i in range(ALL)]

    def test_1_first(self):
        cursor = self.collect.find({}).sort([
            ('_id', 1),
        ])
        page1 = get_page(cursor, 20)

        self.assertEqual([i['_id'] for i in page1], list(range(20)))
        self.assertEqual(hasattr(page1.paging, 'has_previous'), False)
        self.assertEqual(page1.paging.has_next, True)
        self.assertEqual(page1.paging.previous_position, {'backwards': True, 'obj': {'_id': 0}})
        self.assertEqual(page1.paging.next_position, {'backwards': False, 'obj': {'_id': 19}})

    def test_2_next(self):
        cursor1 = self.collect.find({}).sort([('_id', 1)])
        page1 = get_page(cursor1, 20)

        cursor2 = self.collect.find({}).sort([('_id', 1)])
        page2 = get_page(cursor2, 20, position=page1.paging.next_position)

        self.assertEqual([i['_id'] for i in page2], list(range(20, 40)))
        self.assertEqual(hasattr(page2.paging, 'has_previous'), False)
        self.assertEqual(page2.paging.has_next, True)
        self.assertEqual(page2.paging.previous_position, {'backwards': True, 'obj': {'_id': 20}})
        self.assertEqual(page2.paging.next_position, {'backwards': False, 'obj': {'_id': 39}})

    def test_3_previous(self):
        cursor1 = self.collect.find({}).sort([('_id', 1)])
        page1 = get_page(cursor1, 20)

        cursor2 = self.collect.find({}).sort([('_id', 1)])
        page2 = get_page(cursor2, 20, position=page1.paging.next_position)

        cursor3 = self.collect.find({}).sort([('_id', 1)])
        page3 = get_page(cursor3, 20, position=page2.paging.next_position)

        cursor2 = self.collect.find({}).sort([('_id', 1)])
        page2 = get_page(cursor2, 20, position=page3.paging.previous_position)

        self.assertEqual([i['_id'] for i in page2], list(range(20, 40)))
        self.assertEqual(hasattr(page2.paging, 'has_next'), False)
        self.assertEqual(page2.paging.has_previous, True)
        self.assertEqual(page2.paging.previous_position, {'backwards': True, 'obj': {'_id': 20}})
        self.assertEqual(page2.paging.next_position, {'backwards': False, 'obj': {'_id': 39}})

    def test_backwards_order(self):
        cursor1 = self.collect.find({}).sort([('_id', -1)])
        page1 = get_page(cursor1, 20)
        self.assertEqual([i['_id'] for i in page1], list(range(ALL - 1, ALL - 1 - 20, -1)))

        cursor2 = self.collect.find({}).sort([('_id', -1)])
        page2 = get_page(cursor2, 20, position=page1.paging.next_position)
        self.assertEqual([i['_id'] for i in page2], list(range(ALL - 1 - 20, ALL - 1 - 40, -1)))

        cursor3 = self.collect.find({}).sort([('_id', -1)])
        page3 = get_page(cursor3, 20, position=page2.paging.next_position)
        self.assertEqual([i['_id'] for i in page3], list(range(ALL - 1 - 40, ALL - 1 - 60, -1)))

        cursor2 = self.collect.find({}).sort([('_id', -1)])
        page2 = get_page(cursor2, 20, position=page3.paging.previous_position)
        self.assertEqual([i['_id'] for i in page2], list(range(ALL - 1 - 20, ALL - 1 - 40, -1)))


if __name__ == '__main__':
    unittest.main()
