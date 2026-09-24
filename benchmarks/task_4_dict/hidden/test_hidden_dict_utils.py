from dict_utils import get_value


def test_existing_number():
    data = {
        "score": 95,
    }

    assert get_value(
        data,
        "score",
    ) == 95


def test_missing_key_default():
    data = {
        "name": "Bob",
    }

    assert get_value(
        data,
        "age",
        0,
    ) == 0


def test_missing_key_none():
    data = {
        "name": "Bob",
    }

    assert get_value(
        data,
        "age",
    ) is None