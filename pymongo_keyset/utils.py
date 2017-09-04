
def get_key(d, key):
    result = d
    for k in key.split('.'):
        if isinstance(result, dict):
            result = result.get(k, None)
        else:
            result = None
    return result
