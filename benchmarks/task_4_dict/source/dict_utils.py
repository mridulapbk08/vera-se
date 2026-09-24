def get_value(data: dict, key: str, default=None):
    return data.pop(key, default)