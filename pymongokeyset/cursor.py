from pymongo.cursor import Cursor


def check_params(cursor):
    if not isinstance(cursor, Cursor):
        raise TypeError('cursor must be a pymongo.cursor.Cursor, not {}'.format(type(cursor)))

    if not cursor._Cursor__ordering:
        cursor = cursor.sort([('_id', 1)])
    return cursor


def generate_spec(key_condictions):
    '''
    key_condictions 是一个列表，这个列表的每个元素都是一个形如 (key, value, direction) 的 tuple
    这个函数以递归的方式获取 mongo 查询语句

    >>> generate_spec([
    ...     ('a', '1', 1),
    ...     ('b', '2', -1),
    ... ])
    {'$or': [
        {'$and': [
            {'a': '1'},
            {'b': {'$lt': '2'}}
        ]},
        {'a': {'$gt': '1'}}
    ]}
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


def add__id_to_ordering(cursor, backwards):
    '''_id 作为 unique_key 必须是排序条件的最后一个，为了保证 position 的唯一性'''
    son = cursor._Cursor__ordering
    if '_id' not in son:
        son.update({'_id': 1})
    if backwards:
        for key in son.keys():
            son[key] = -1 * son[key]


def add_projections(cursor):
    '''对于所有由于排序的键，这些键都必须在 projection 中，因为这些键对应的 value 会成为下一次查询的时候条件'''

    if not cursor._Cursor__projection:
        cursor._Cursor__projection = {}

    son = cursor._Cursor__ordering

    projection_type = 0
    for key, direction in cursor._Cursor__projection.items():
        if key != '_id':
            projection_type = direction
            break

    if projection_type == 0:
        cursor._Cursor__projection.pop('_id', None)
        for key in list(son.keys()) + ['_id']:
            if cursor._Cursor__projection.get(key) == 0:
                cursor._Cursor__projection.pop(key)
    else:
        cursor._Cursor__projection['_id'] = 1
        cursor._Cursor__projection.update({key: 1 for key in son.keys()})


def add_keyset_specifying(cursor, position):
    '''TODO'''
    if position:

        key_condictions = []
        for key, direction in cursor._Cursor__ordering.items():
            key_condictions.append((key, position['obj'].get(key), direction))

        keyset_condiction = generate_spec(key_condictions)

        if cursor._Cursor__spec:
            cursor._Cursor__spec = {'$and': [keyset_condiction, cursor._Cursor__spec]}
        else:
            cursor._Cursor__spec = keyset_condiction


def add_limit(cursor, limit):
    '''为了知道有没有下一页/上一页，需要多查出一个文档。多查出的那个文档不会返回给用户'''
    cursor = cursor.limit(limit + 1)


def get_keyset_cursor(cursor, limit=10, position={}):
    '''add condiction for keyset'''

    cursor = check_params(cursor)
    add__id_to_ordering(cursor, backwards=position.get('backwards', False))
    add_projections(cursor)
    add_keyset_specifying(cursor, position)
    add_limit(cursor, limit)

    return cursor
