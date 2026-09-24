from list_utils import last_item


def test_last_item_strings():
    assert last_item(
        ["a", "b"]
    ) == "b"


def test_last_item_single():
    assert last_item(
        [10]
    ) == 10


def test_last_item_does_not_modify_input():
    items = [
        1,
        2,
        3,
    ]

    result = last_item(
        items
    )

    assert result == 3

    assert items == [
        1,
        2,
        3,
    ]


def test_last_item_tuple():
    assert last_item(
        ("x", "y", "z")
    ) == "z"