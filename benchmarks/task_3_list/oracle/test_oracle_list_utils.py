from list_utils import last_item


def test_does_not_mutate_list():
    items = [4, 5, 6]

    result = last_item(items)

    assert result == 6
    assert items == [4, 5, 6]


def test_tuple():
    assert last_item(
        ("a", "b", "c")
    ) == "c"


def test_mixed_values():
    obj = object()

    items = [
        1,
        "two",
        obj,
    ]

    assert last_item(items) is obj


def test_repeated_call_same_input():
    items = [10, 20, 30]

    assert last_item(items) == 30
    assert last_item(items) == 30

    assert items == [
        10,
        20,
        30,
    ]