from .cursor import get_keyset_cursor
from .utils import get_key
from bson.json_util import dumps, loads
from functools import partial


def base_obj_formuler(obj, ordering):
    '''
    把一个 obj 中可以用于 keyset 的信息提取出来
    '''
    result = {}
    for key in ordering:
        result[key] = get_key(obj, key)
    return result


class Paging:
    '''
    Paging 有三个属性：
    1.  previous_position 字符串
        保存着查询上一页所需要的信息
    2.  next_position 字符串
        保存着查询下一页所需要的信息
    3.  has_next 或者 has_previous 布尔值
        对于一个 Paging 实例，它只能有 has_next 和 has_previous 两者中的一种
    '''

    def __init__(self, limit, backwards, obj_list, obj_formuler):
        '''
        limit           int         一页的长度
        backwards       bool        查询的是否是上一页
        obj_list        list        一个由 dict 组成的 list，长度为 0 <= len(obj_list) <= limit + 1
        obj_formuler    function
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
        obj_list = list(cursor)
        obj_return_list = obj_list[:limit]
        if backwards:
            obj_return_list.reverse()
        super().__init__(obj_return_list)

        ordering = {i: j for i, j in cursor._Cursor__ordering.items()}
        obj_formuler = partial(base_obj_formuler, ordering=ordering)
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
