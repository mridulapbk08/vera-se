from dict_utils import get_value


def test_dictionary_not_modified():
    data = {
        "name": "Alice",
        "age": 30,
    }

    original = data.copy()

    result = get_value(
        data,
        "name",
    )

    assert result == "Alice"
    assert data == original


def test_repeated_lookup():
    data = {
        "name": "Alice",
    }

    assert get_value(
        data,
        "name",
    ) == "Alice"

    assert get_value(
        data,
        "name",
    ) == "Alice"


def test_missing_key_does_not_modify_dictionary():
    data = {
        "x": 10,
    }

    original = data.copy()

    result = get_value(
        data,
        "missing",
        5,
    )

    assert result == 5
    assert data == original


def test_object_value_identity():
    obj = object()

    data = {
        "item": obj,
    }

    assert get_value(
        data,
        "item",
    ) is obj