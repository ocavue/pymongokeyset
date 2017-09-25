def get_value(d, key):
    """
    >>> get_value({'a': {'b': {'c': 1}}}, 'a.b.c')
    1
    """

    result = d
    for k in key.split('.'):
        if isinstance(result, dict):
            result = result.get(k, None)
        else:
            result = None
    return result


if __name__ == '__main__':
    import doctest
    doctest.testmod()
