from math_utils import average


def test_average_positive():
    assert average(
        20,
        40,
    ) == 30


def test_average_equal():
    assert average(
        5,
        5,
    ) == 5


def test_average_zero():
    assert average(
        0,
        10,
    ) == 5