from collections import OrderedDict
from pymongo.cursor import Cursor


class NewCursor(Cursor):
    def __init__(self, collection, filter, projection, sort, limit):
        if limit <= 0:
            raise ValueError('limit must bigger than 0, not {}'.format(limit))

        self.__limit = limit
        self.__passed = 0
        self.__first_obj = 0
        self.__item_0 = None
        self.__item_n = None
        self.__item_n_plus_1 = None

        super().__init__(
            collection=collection,
            filter=filter,
            projection=projection,
            limit=limit,
            sort=sort,
        )

    def __next__(self):
        if self.__passed == 0:
            self.__item_0 = super().__next__()
        elif self.__passed == self.__limit - 2:
            self.__item_n = super().__next__()
        elif self.__passed == self.__limit - 1:
            self.__item_n_plus_1 = super().__next__()
            raise StopIteration

        self.__passed += 1
        return super().__next__()


def check_params(sort, limit):
    if not isinstance(sort, list):
        raise TypeError('sort must be list')
    if not isinstance(limit, int):
        raise TypeError('limit must be int')


def generate_spec(key_condictions):
    '''
    key_condictions 是一个列表，这个列表的每个元素都是一个形如 (key, value, direction) 的 tuple
    这个函数以递归的方式获取 mongo 查询语句

    >>> generate_spec([
    ...     ('a', '10', 1),
    ...     ('b', '20', 0),
    ... ])
    {'$or': [{'$and': [{'a': '10'}, {'b': {'$lt': '20'}}]}, {'a': {'$gt': '10'}}]}
    '''

    if not key_condictions:
        return {}

    item = key_condictions[0]
    key, value, direction = item

    gt_or_lt = '$gt' if direction == 1 else '$lt'

    next_ordering = generate_spec(key_condictions[1:])
    if next_ordering:
        return {'$or': [{'$and': [{key: value}, next_ordering]}, {key: {gt_or_lt: value}}]}
    else:
        return {key: {gt_or_lt: value}}


def change_sort_to_orderdict(sort):
    '''
    >>> change_sort_to_orderdict([('a', 1), ('b', -1)])
    OrderedDict([('a', 1), ('b', -1)])
    >>> change_sort_to_orderdict((['a', 1], ['b', -1]))
    OrderedDict([('a', 1), ('b', -1)])
    '''

    return OrderedDict(sort)


def add__id_to_sort(sort):
    '''_id 作为 unique_key 必须是排序条件的最后一个，为了保证 position 的唯一性

    >>> sort = OrderedDict([('a', 1)])
    >>> add__id_to_sort(sort)
    >>> sort
    OrderedDict([('a', 1), ('_id', 1)])
    '''

    if '_id' not in sort.keys():
        sort['_id'] = 1


def reverse_sort_direction(sort, backwards):
    '''
    >>> sort = OrderedDict([('a', 1), ('_id', 1)])
    >>> reverse_sort_direction(sort, True)
    >>> sort
    OrderedDict([('a', -1), ('_id', -1)])
    '''

    if backwards:
        for i in sort:
            sort[i] = -sort[i]


def add_projection(projection, sort):
    '''对于所有由于排序的键，这些键都必须在 projection 中，因为这些键对应的 value 会成为下一次查询的时候条件'''
    if projection is None:
        return

    # In mongodb, direction of projection(except '_id') is one of 1 and 0. Other case will report an error. For example:
    #     collection.find({}, {a: 1, 'b': 0})
    #     errmsg: Projection cannot have a mix of inclusion and exclusion.
    direction = 0
    for key, item_direction in projection.items():
        if key != '_id':
            direction = item_direction
            break

    if direction == 0:
        # If direction of projection is 0, mongodb will not return fields in projection
        # So make sure that projection and ordering has not intersection
        for key in sort.keys():
            projection.pop(key, None)
    else:
        # If direction of projection is 1, mongodb will only reture fields in projection
        # So make sure that all fields in ordering are in projection
        projection.update({key: 1 for key in sort.keys()})


def add_keyset_specifying(filter, sort, position):
    '''在 specifying 中添加 keyset filter'''
    if position:

        key_condictions = []
        for key, direction in sort.items():
            key_condictions.append((key, position['obj'].get(key), direction))

        keyset_condiction = generate_spec(key_condictions)

        if filter:
            filter = {'$and': [keyset_condiction, filter]}
        else:
            filter = keyset_condiction
    return filter


def add_limit(limit):
    '''为了知道有没有下一页/上一页，需要多查出一个文档。多查出的那个文档不会返回给用户'''
    if limit == 0:
        return 0
    else:
        return abs(limit) + 1


def get_keyset_cursor(collection, filter={}, projection=None, sort=[], limit=0, position={}):
    check_params(sort, limit)

    sort = change_sort_to_orderdict(sort)
    add__id_to_sort(sort)
    reverse_sort_direction(sort, backwards=position.get('backwards', False))
    add_projection(projection, sort)
    filter = add_keyset_specifying(filter, sort, position)
    limit = add_limit(limit)

    return NewCursor(
        collection=collection,
        filter=filter,
        projection=projection,
        limit=limit,
        sort=list(sort.items()),
    )


if __name__ == '__main__':
    import doctest
    doctest.testmod()
