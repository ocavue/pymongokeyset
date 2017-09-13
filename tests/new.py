from base import BaseTestCase, unittest
from pymongokeyset import get_keyset_cursor as get_page


def log(*args, **kwargs):
    print(*args, **kwargs)
    pass


class NormalTestCase(BaseTestCase):
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

    def test_forwards_process(self):
        cursor1 = get_page(self.collect, limit=3, sort=[('_id', 1)])
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertTrue(cursor1.paging.has_next)

        cursor2 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor1.paging.next_position)
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_next)

        cursor3 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor2.paging.next_position)
        self.assertEqual(list(cursor3), self.objs[6:])
        self.assertFalse(cursor3.paging.has_next)

        return cursor3

    def test_backwards_process(self):
        cursor3 = self.test_forwards_process()

        cursor2 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor3.paging.previous_position)
        log(list(cursor2))
        log(cursor2.paging.__dict__)
        '''
        self.assertEqual(list(cursor2), self.objs[3:6])
        self.assertTrue(cursor2.paging.has_previous)

        cursor1 = get_page(self.collect, limit=3, sort=[('_id', 1)], position=cursor2.paging.previous_position)
        self.assertEqual(list(cursor1), self.objs[:3])
        self.assertFalse(cursor1.paging.has_next)
        '''

if __name__ == '__main__':
    unittest.main()
