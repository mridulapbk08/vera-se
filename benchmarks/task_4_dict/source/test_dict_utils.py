from dict_utils import get_value


def test_get_value_existing_key():
    data = {
        "name": "Alice",
        "age": 30,
    }

    assert get_value(
        data,
        "name",
    ) == "Alice"