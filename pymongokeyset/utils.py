__all__ = ['itemgetter']


def get_value(obj, key):
    """mongodb style get value

    >>> get_value({'a': {'b': {'c': 1}}}, 'a.b.c') == 1
    True
    >>> get_value({'a': {'b': {'c': 1}}}, 'x.y.z') is None
    True
    """
    keys = key.split('.', 1)
    if len(keys) == 2:
        return get_value(obj.get(keys[0], {}), keys[1])
    else:
        return obj.get(keys[0], None)


def itemgetter(items):
    """Return a callable object that fetches item.

    >>> f = itemgetter(['a.aa', 'b'])
    >>> f({'a': {'aa': 1}, 'b': 2, 'c': 3})
    {'a.aa': 1, 'b': 2}
    >>> f({})
    {}
    """

    def f(obj):
        return {key: get_value(obj, key) for key in items if obj}
    return f


if __name__ == '__main__':
    import doctest
    doctest.testmod()
