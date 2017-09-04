def check_params(cursor):
    # All private attributes of pymongo.cursor.Cursor that used by pymongokeyset
    attrs = ['_Cursor__projection', '_Cursor__ordering']

    for attr in attrs:
        if not hasattr(cursor, attr):
            raise AttributeError(
                'cursor has not attribute {}, make sure that cursor is an object of pymongo.cursor.Cursor'.format(attr)
            )


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


def add__id_to_ordering(cursor):
    '''_id 作为 unique_key 必须是排序条件的最后一个，为了保证 position 的唯一性'''
    son = cursor._Cursor__ordering
    if '_id' not in son:
        son.update({'_id': 1})


def reverse_ordering_direction(cursor, backwards):
    son = cursor._Cursor__ordering
    if backwards:
        for key in son.keys():
            son[key] = -1 * son[key]


def add_projections(cursor):
    '''
    对于所有由于排序的键，这些键都必须在 projection 中，因为这些键对应的 value 会成为下一次查询的时候条件
    '''
    if not cursor._Cursor__projection:
        cursor._Cursor__projection = {}

    ordering = cursor._Cursor__ordering
    projection = cursor._Cursor__projection

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
        for key in ordering.keys():
            projection.pop(key, None)
    else:
        # If direction of projection is 1, mongodb will only reture fields in projection
        # So make sure that all fields in ordering are in projection
        projection.update({key: 1 for key in ordering.keys()})


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
    add__id_to_ordering(cursor)
    reverse_ordering_direction(cursor, backwards=position.get('backwards', False))
    add_projections(cursor)
    add_keyset_specifying(cursor, position)
    add_limit(cursor, limit)

    return cursor
