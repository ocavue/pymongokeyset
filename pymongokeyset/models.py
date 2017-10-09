from .utils import itemgetter
from bson.json_util import dumps
from pymongo.cursor import Cursor
from collections import deque


class Paging:
    """
    Paging has three attributes：
    1.  previous_position string
        information for query previous page
    2.  next_position string
        information for query next page
    3.  has_next or has_previous bool
        A Paging instance can only has one of has_next and has_previous
    """

    def __init__(
        self,
        limit: int,  # length of one page
        backwards: bool,  # is searching preview page
        item_0: dict,  # first item of this page
        item_n: dict,  # last item of this page
        item_n_plus_1: dict  # the extra item of this page (the (limit+1)th item)
    ):
        if backwards:
            self.previous_position = dumps({'obj': item_0, 'backwards': True})
            self.next_position = dumps({'obj': item_n, 'backwards': False})
            self.has_previous = bool(item_n_plus_1)
        else:
            self.previous_position = dumps({'obj': item_0, 'backwards': True})
            self.next_position = dumps({'obj': item_n, 'backwards': False})
            self.has_next = bool(item_n_plus_1)


class KeysetCursor(Cursor):
    def __init__(self, collection, filter, projection, sort, limit, backwards):
        if isinstance(limit, int) and limit <= 0:
            raise ValueError('limit must bigger than 0, not {}'.format(limit))

        self.__backwards = backwards
        self.__limit = limit
        self.__item_0, self.__item_n, self.__item_n_plus_1 = {}, {}, {}
        self.__extracter = itemgetter([i[0] for i in sort])
        self.__paging = None
        self.__data = deque()

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
                    self.__limit,
                    self.__backwards,
                    self.__extracter(self.__item_0),
                    self.__extracter(self.__item_n),
                    self.__extracter(self.__item_n_plus_1),
                )
            return self.__paging

    def __get_data(self):
        try:
            while True:
                self.__data.append(super().__next__())
        except StopIteration:
            pass

        # the extra item of this page (the limit+1 th item)
        self.__item_n_plus_1 = self.__data.pop() if len(self.__data) >= self.__limit else {}
        if self.__backwards:
            self.__data.reverse()
        # first item of this page
        self.__item_0 = self.__data[0] if len(self.__data) >= 1 else {}
        # last item of this page
        self.__item_n = self.__data[-1] if len(self.__data) >= self.__limit - 1 else {}

    def __next__(self):
        if not self.__data and super().alive:
            self.__get_data()

        if self.__data:
            return self.__data.popleft()
        else:
            raise StopIteration
