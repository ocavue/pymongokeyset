from .cursor import get_keyset_cursor
from .utils import get_key
from bson.json_util import dumps, loads


class Paging:
    def __init__(self, limit, backwards, obj_list, obj_formuler):
        '''
        TODO
        '''

        item_0 = obj_formuler(obj_list[0]) if len(obj_list) >= 1 else {}
        item_n = obj_formuler(obj_list[limit - 1]) if len(obj_list) >= limit else {}
        item_n_plus_1 = obj_formuler(obj_list[limit]) if len(obj_list) > limit else {}

        if backwards:
            self.previous_position = dumps({'obj': item_n, 'backwards': True})
            self.next_position = dumps({'obj': item_0, 'backwards': False})
            self.has_previous = bool(item_n_plus_1)
        else:
            self.previous_position = dumps({'obj': item_0, 'backwards': True})
            self.next_position = dumps({'obj': item_n, 'backwards': False})
            self.has_next = bool(item_n_plus_1)


class Page(list):
    def __init__(self, cursor, limit, backwards):
        def obj_formuler(obj):
            result = {}
            for key in ordering:
                result[key] = get_key(obj, key)
            return result

        ordering = {i: j for i, j in cursor._Cursor__ordering.items()}

        obj_list = list(cursor)
        obj_return_list = obj_list[:limit]
        if backwards:
            obj_return_list.reverse()
        super().__init__(obj_return_list)
        self.paging = Paging(limit, backwards, obj_list, obj_formuler)


def get_page(cursor, limit=10, position=''):
    # 把 position 由 str 转为 dict
    if position:
        position = loads(position)
    else:
        position = {}

    backwards = position.get('backwards', False)
    cursor = get_keyset_cursor(cursor, limit, position)
    page = Page(cursor, limit, backwards)
    return page
