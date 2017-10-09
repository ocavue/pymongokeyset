from collections import OrderedDict
from .models import KeysetCursor
from bson.json_util import loads
from typing import Dict, Iterable, Tuple


def check_params(sort, limit):
    if not isinstance(sort, list):
        raise TypeError('sort must be list')
    if not isinstance(limit, int):
        raise TypeError('limit must be int')
    if limit == 0:
        raise ValueError('limit can not be zero')
    if limit < 0:
        # TODO why does pymongo allow a limit small than zero
        raise ValueError('limit can not smaller than zero')


def generate_spec(key_condictions):
    """get mongo query filter by recursion

    key_condictions is a list of (key, value, direction)

    >>> generate_spec([
    ...     ('a', '10', 1),
    ...     ('b', '20', 0),
    ... ])
    {'$or': [{'$and': [{'a': '10'}, {'b': {'$lt': '20'}}]}, {'a': {'$gt': '10'}}]}
    """

    if not key_condictions:
        return {}

    key, value, direction = key_condictions[0]

    gt_or_lt = '$gt' if direction == 1 else '$lt'

    next_ordering = generate_spec(key_condictions[1:])
    if next_ordering:
        return {'$or': [{'$and': [{key: value}, next_ordering]}, {key: {gt_or_lt: value}}]}
    else:
        return {key: {gt_or_lt: value}}


def update_sort(sort, backwards):
    """update sort

    >>> update_sort([('a', 1), ('b': -1)], True)
    OrderedDict([('a', -1), ('b': -1), ('_id': -1)])
    """

    # change sort to OrderedDict
    sort = OrderedDict(sort)

    # Add _id to sort's keys
    # _id must be the last condiction of sort and ensure that position is unique.
    if '_id' not in sort.keys():
        sort['_id'] = 1

    # Reverse direction of sort if necessary
    if backwards:
        for i in sort:
            sort[i] = -sort[i]

    return sort


def add_projection(projection, sort):
    """Make sure that those keys used to sort must be in projection

    Beacuse those value will be condictions of next query
    """
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
        # So make sure that projection and sort has not intersection
        inter = set(sort.keys()) & set(projection.keys())
        if inter:
            inter_projection = {i: 0 for i in inter}
            raise ValueError('{} is in sort. Please remove {} in projection'.format(inter, inter_projection))
    else:
        # If direction of projection is 1, mongodb will only reture fields in projection
        # So make sure that all fields in sort are in projection
        diff = set(sort.keys()) - set(projection.keys())
        if diff:
            diff_projection = {i: 1 for i in diff}
            raise ValueError('{} is in sort. Please add {} in projection'.format(diff, diff_projection))
    return projection


def add_keyset_specifying(filter, sort, position):
    """在 specifying 中添加 keyset filter"""
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
    """plus 1 to limit

    To know if there is next or preview page, we need to find an extra document which will not be returned to user.
    """
    return abs(limit) + 1


def get_keyset_cursor(
    collection,
    filter: Dict = None,
    projection: Dict[str, int] = None,
    sort: Iterable[Tuple[str, int]] = None,
    limit: int = 10,
    position: str = None
):
    """get a keyset cursor"""

    check_params(sort, limit)

    position = loads(position) if position else {}
    backwards = position.get('backwards', False)

    sort = update_sort(sort, backwards)
    projection = add_projection(projection, sort)
    filter = add_keyset_specifying(filter, sort, position)
    limit = add_limit(limit)

    return KeysetCursor(
        collection=collection,
        filter=filter,
        projection=projection,
        limit=limit,
        sort=list(sort.items()),
        backwards=backwards
    )


if __name__ == '__main__':
    import doctest
    doctest.testmod()
