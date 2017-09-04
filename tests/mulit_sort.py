from base import BaseTestCase
from pymongokeyset import get_page
from copy import deepcopy
import unittest


class MuiltSortTestCase(BaseTestCase):
    objs = [
        {'m': 0, 'n': 0, '_id': 1},
        {'m': 0, 'n': 0, '_id': 2},
        {'m': 0, 'n': 1, '_id': 3},
        {'m': 0, 'n': 1, '_id': 4},
        {'m': 1, 'n': 0, '_id': 5},
        {'m': 1, 'n': 0, '_id': 6},
        {'m': 1, 'n': 1, '_id': 7},
        {'m': 1, 'n': 1, '_id': 8},
    ]  # yapf: disable

    def test_set_up(self):
        self.assertEqual(list(self.collect.find({}).sort([
            ('m', 1),
            ('n', 1),
            ('_id', 1),
        ])), self.objs)

    def test_paging(self):
        cursor = self.collect.find({}).sort([
            ('m', 1),
            ('n', 1),
            ('_id', 1),
        ])

        page1 = get_page(deepcopy(cursor), 3)
        self.assertEqual([i for i in page1], self.objs[:3])

        page2 = get_page(deepcopy(cursor), 3, position=page1.paging.next_position)
        self.assertEqual([i for i in page2], self.objs[3:6])

        page3 = get_page(deepcopy(cursor), 3, position=page2.paging.next_position)
        self.assertEqual([i for i in page3], self.objs[6:9])

        page2 = get_page(deepcopy(cursor), 3, position=page3.paging.previous_position)
        self.assertEqual([i for i in page2], self.objs[3:6])

        page1 = get_page(deepcopy(cursor), 3, position=page2.paging.previous_position)
        self.assertEqual([i for i in page1], self.objs[:3])


if __name__ == '__main__':
    unittest.main()
