from base import BaseTestCase, unittest
from pymongokeyset import page_query


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

    def assert_cursor(self, cursor, objs, has_more):
        self.assertEqual(list(cursor), objs)
        self.assertEqual(cursor.paging.has_more, has_more)

    def test_single_sort_case(self):
        search_condictions = {
            'collection': self.collect,
            'limit': 3,
            'sort': [('_id', 1)],
        }

        cursor1 = page_query(**search_condictions)
        self.assert_cursor(cursor1, self.objs[:3], has_more=True)

        cursor2 = page_query(**search_condictions, position=cursor1.paging.position)
        self.assert_cursor(cursor2, self.objs[3:6], has_more=True)

        cursor3 = page_query(**search_condictions, position=cursor2.paging.position)
        self.assert_cursor(cursor3, self.objs[6:], has_more=False)

        cursor2 = page_query(**search_condictions, position=cursor3.paging.position, backwards=True)
        self.assert_cursor(cursor2, self.objs[3:6], has_more=True)

        cursor1 = page_query(**search_condictions, position=cursor2.paging.position, backwards=True)
        self.assert_cursor(cursor1, self.objs[:3], has_more=False)

    def test_mutil_sort_cast(self):
        search_condictions = {
            'collection': self.collect,
            'limit': 3,
            'sort': [('m', 1), ('n', 1), ('_id', 1)],
            # TODO test some edge index cases
        }

        cursor1 = page_query(**search_condictions)
        self.assert_cursor(cursor1, self.objs[:3], has_more=True)

        cursor2 = page_query(**search_condictions, position=cursor1.paging.position)
        self.assert_cursor(cursor2, self.objs[3:6], has_more=True)

        cursor3 = page_query(**search_condictions, position=cursor2.paging.position)
        self.assert_cursor(cursor3, self.objs[6:], has_more=False)

        cursor2 = page_query(**search_condictions, position=cursor3.paging.position, backwards=True)
        self.assert_cursor(cursor2, self.objs[3:6], has_more=True)

        cursor1 = page_query(**search_condictions, position=cursor2.paging.position, backwards=True)
        self.assert_cursor(cursor1, self.objs[:3], has_more=False)


if __name__ == '__main__':
    unittest.main()
