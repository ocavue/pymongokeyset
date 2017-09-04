from .cursor import get_keyset_cursor
from .utils import get_key


class paging:
    def __init__(self, obj_list, limit, backwards, get_position):
        '''
        paging has 2 attributes:
        '''

        item_0 = get_position(obj_list[0]) if len(obj_list) >= 1 else {}
        item_n = get_position(obj_list[limit - 1]) if len(obj_list) >= limit else {}
        item_n_plus_1 = get_position(obj_list[limit]) if len(obj_list) > limit else {}

        if backwards:
            self.previous_position = {'obj': item_n, 'backwards': True}
            self.next_position = {'obj': item_0, 'backwards': False}
            self.has_previous = bool(item_n_plus_1)
        else:
            self.previous_position = {'obj': item_0, 'backwards': True}
            self.next_position = {'obj': item_n, 'backwards': False}
            self.has_next = bool(item_n_plus_1)


class Page(list):
    def __init__(self, cursor, limit, backwards):
        ordering = {i: j for i, j in cursor._Cursor__ordering.items()}
        get_position = tmp_get_position(ordering)

        obj_list = list(cursor)
        obj_return_list = obj_list[:limit]
        if backwards:
            obj_return_list.reverse()
        super().__init__(obj_return_list)
        self.paging = paging(obj_list, limit, backwards, get_position)


def tmp_get_position(ordering):
    def get_position(obj):
        result = {}
        for key in ordering:
            result[key] = get_key(obj, key)
        return result

    return get_position


def get_page(cursor, limit=10, position={}):
    backwards = position.get('backwards', False)
    cursor = get_keyset_cursor(cursor, limit, position)
    page = Page(cursor, limit, backwards)
    return page
