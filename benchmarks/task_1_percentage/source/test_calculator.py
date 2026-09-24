from calculator import divide, percentage


def test_divide():
    assert divide(10, 2) == 5


def test_percentage():
    assert percentage(25, 100) == 25