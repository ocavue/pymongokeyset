from base import BaseTestCase, unittest
from pymongokeyset import get_keyset_cursor as get_page


def log(*args, **kwargs):
    print(*args, **kwargs)
    pass


class NormalTestCase(BaseTestCase):
    objs = [
        {'m': 0, 'n': 0, '_id': 0},
        {'m': 0, 'n': 0, '_id': 1},
        {'m': 0, 'n': 1, '_id': 2},
        {'m': 0, 'n': 1, '_id': 3},
        {'m': 1, 'n': 0, '_id': 4},
        {'m': 1, 'n': 0, '_id': 5},
        {'m': 1, 'n': 1, '_id': 6},
        {'m': 1, 'n': 1, '_id': 7},
    ]  # yapf: disable

    def test_single_sort_case(self):
        cursor1 = get_page(self.collect, limit=3, sort=[('_id', 1)])
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertTrue(cursor1.paging.has_next)
        self.assertFalse(hasattr(cursor1.paging, 'has_previous'))

        cursor2 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor1.paging.next_position)
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_next)
        self.assertFalse(hasattr(cursor2.paging, 'has_previous'))

        cursor3 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor2.paging.next_position)
        self.assertEqual(list(cursor3), self.objs[6:])
        self.assertFalse(cursor3.paging.has_next)
        self.assertFalse(hasattr(cursor3.paging, 'has_previous'))

        cursor2 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor3.paging.previous_position)
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_previous)
        self.assertFalse(hasattr(cursor2.paging, 'has_next'))

        cursor1 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor2.paging.previous_position)
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertFalse(cursor1.paging.has_previous)
        self.assertFalse(hasattr(cursor1.paging, 'has_next'))

    def test_mulit_sort_case(self):
        search_condictions = {
            'collection': self.collect,
            'limit': 3,
            'sort': [('m', 1), ('n', 1), ('_id', 1)],
        }

        cursor1 = get_page(**search_condictions)
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertTrue(cursor1.paging.has_next)
        self.assertFalse(hasattr(cursor1.paging, 'has_previous'))

        cursor2 = get_page(**search_condictions, position=cursor1.paging.next_position)
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_next)
        self.assertFalse(hasattr(cursor2.paging, 'has_previous'))

        cursor3 = get_page(**search_condictions, position=cursor2.paging.next_position)
        self.assertEqual(list(cursor3), self.objs[6:])
        self.assertFalse(cursor3.paging.has_next)
        self.assertFalse(hasattr(cursor3.paging, 'has_previous'))

        cursor2 = get_page(**search_condictions, position=cursor3.paging.previous_position)
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_previous)
        self.assertFalse(hasattr(cursor2.paging, 'has_next'))

        cursor1 = get_page(**search_condictions, position=cursor2.paging.previous_position)
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertFalse(cursor1.paging.has_previous)
        self.assertFalse(hasattr(cursor1.paging, 'has_next'))


if __name__ == '__main__':
    unittest.main()
