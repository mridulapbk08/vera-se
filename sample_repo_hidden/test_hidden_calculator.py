from calculator import percentage


def test_percentage_half():
    assert percentage(50, 100) == 50


def test_percentage_fraction():
    assert percentage(1, 4) == 25


def test_percentage_large_total():
    assert percentage(250, 1000) == 25