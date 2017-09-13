from base import BaseTestCase, unittest
from pymongokeyset.cursor import get_page


class SimpleTestCase(BaseTestCase):
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

    def test_first_page(self):
        cursor = get_page(self.collect, limit=3, sort=[('_id', 1)])
        self.assertEqual(list(cursor), self.objs[:3])
        print(cursor.first_end)


if __name__ == '__main__':
    unittest.main()
