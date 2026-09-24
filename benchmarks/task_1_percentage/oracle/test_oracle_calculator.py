import pytest

from calculator import percentage


def test_percentage_non_integer():
    assert percentage(2, 3) == pytest.approx(
        66.6666666667
    )


def test_percentage_small_value():
    assert percentage(1, 200) == pytest.approx(
        0.5
    )


def test_percentage_above_100():
    assert percentage(150, 100) == pytest.approx(
        150.0
    )


def test_percentage_negative():
    assert percentage(-5, 20) == pytest.approx(
        -25.0
    )


def test_percentage_precision():
    assert percentage(7, 9) == pytest.approx(
        77.7777777778
    )