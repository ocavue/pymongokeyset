from .utils import get_key
# from bson.json_util import dumps, loads
from functools import partial
from pymongo.cursor import Cursor
from collections import deque


def dumps(dict):
    return dict


def base_obj_formuler(obj, sort_keys):
    '''
    把一个 obj 中可以用于 keyset 的信息提取出来
    '''
    result = {}
    for key in sort_keys:
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

    def __init__(self, limit, backwards, obj_formuler, spec_items):
        '''
        limit           int         一页的长度
        backwards       bool        查询的是否是上一页
        obj_list        list        一个由 dict 组成的 list，长度为 0 <= len(obj_list) <= limit + 1
        obj_formuler    function
        '''

        item_0 = obj_formuler(spec_items[0]) if spec_items[0] else {}
        item_n = obj_formuler(spec_items[1]) if spec_items[1] else {}
        item_n_plus_1 = obj_formuler(spec_items[2]) if spec_items[2] else {}

        if backwards:
            self.previous_position = dumps({'obj': item_0, 'backwards': True})
            self.next_position = dumps({'obj': item_n, 'backwards': False})
            self.has_previous = bool(item_n_plus_1)
        else:
            self.previous_position = dumps({'obj': item_0, 'backwards': True})
            self.next_position = dumps({'obj': item_n, 'backwards': False})
            self.has_next = bool(item_n_plus_1)


class NewCursor(Cursor):
    def __init__(self, collection, filter, projection, sort, limit, backwards):
        if isinstance(limit, int) and limit <= 0:
            raise ValueError('limit must bigger than 0, not {}'.format(limit))

        self.__backwards = backwards
        self.__limit = limit
        self.spec_items = [None, None, None]
        self.__obj_formuler = partial(base_obj_formuler, sort_keys=[i[0] for i in sort])
        self.__paging = None
        self.__data = deque()  # TODO

        super().__init__(
            collection=collection,
            filter=filter,
            projection=projection,
            limit=limit,
            sort=sort,
        )

    @property
    def paging(self):
        if super().alive:
            raise Exception('cound not be alive')
        else:
            if not self.__paging:
                self.__paging = Paging(
                    limit=self.__limit,
                    backwards=self.__backwards,
                    obj_formuler=self.__obj_formuler,
                    spec_items=self.spec_items,
                )
            return self.__paging

    def __get_data(self):
        try:
            while True:
                self.__data.append(super().__next__())
        except StopIteration:
            pass

        self.spec_items[2] = self.__data.pop() if len(self.__data) >= self.__limit else {}
        if self.__backwards:
            self.__data.reverse()
        self.spec_items[0] = self.__data[0] if len(self.__data) >= 1 else {}
        self.spec_items[1] = self.__data[-1] if len(self.__data) >= self.__limit - 1 else {}

    def __next__(self):
        if not self.__data and super().alive:
            self.__get_data()

        if self.__data:
            return self.__data.popleft()
        else:
            raise StopIteration
