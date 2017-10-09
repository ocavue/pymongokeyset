from base import BaseTestCase, unittest
from pymongokeyset import get_keyset_cursor


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

    def assert_cursor(self, cursor, objs, has_next=None, has_previous=None):
        self.assertEqual(list(cursor), objs)
        if has_next is not None:
            self.assertEqual(cursor.paging.has_next, has_next)
            self.assertFalse(hasattr(cursor.paging, 'has_previous'))
        else:
            self.assertEqual(cursor.paging.has_previous, has_previous)
            self.assertFalse(hasattr(cursor.paging, 'has_next'))

    def test_single_sort_case(self):
        search_condictions = {
            'collection': self.collect,
            'limit': 3,
            'sort': [('_id', 1)],
        }

        cursor1 = get_keyset_cursor(**search_condictions)
        self.assert_cursor(cursor1, self.objs[:3], has_next=True)

        cursor2 = get_keyset_cursor(**search_condictions, position=cursor1.paging.next_position)
        self.assert_cursor(cursor2, self.objs[3:6], has_next=True)

        cursor3 = get_keyset_cursor(**search_condictions, position=cursor2.paging.next_position)
        self.assert_cursor(cursor3, self.objs[6:], has_next=False)

        cursor2 = get_keyset_cursor(**search_condictions, position=cursor3.paging.previous_position)
        self.assert_cursor(cursor2, self.objs[3:6], has_previous=True)

        cursor1 = get_keyset_cursor(**search_condictions, position=cursor2.paging.previous_position)
        self.assert_cursor(cursor1, self.objs[:3], has_previous=False)

    def test_mutil_sort_cast(self):
        search_condictions = {
            'collection': self.collect,
            'limit': 3,
            'sort': [('m', 1), ('n', 1), ('_id', 1)],
            # TODO test some edge index cases
        }

        cursor1 = get_keyset_cursor(**search_condictions)
        self.assert_cursor(cursor1, self.objs[:3], has_next=True)

        cursor2 = get_keyset_cursor(**search_condictions, position=cursor1.paging.next_position)
        self.assert_cursor(cursor2, self.objs[3:6], has_next=True)

        cursor3 = get_keyset_cursor(**search_condictions, position=cursor2.paging.next_position)
        self.assert_cursor(cursor3, self.objs[6:], has_next=False)

        cursor2 = get_keyset_cursor(**search_condictions, position=cursor3.paging.previous_position)
        self.assert_cursor(cursor2, self.objs[3:6], has_previous=True)

        cursor1 = get_keyset_cursor(**search_condictions, position=cursor2.paging.previous_position)
        self.assert_cursor(cursor1, self.objs[:3], has_previous=False)


if __name__ == '__main__':
    unittest.main()
