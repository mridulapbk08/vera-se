import pytest

from calculator import percentage


def test_percentage_half():
    assert percentage(50, 100) == 50


def test_percentage_fraction():
    assert percentage(1, 4) == 25


def test_percentage_large_total():
    assert percentage(250, 1000) == 25


def test_percentage_decimal_result():
    assert percentage(1, 3) == pytest.approx(
        33.3333333333
    )


def test_percentage_small_decimal():
    assert percentage(1, 8) == pytest.approx(
        12.5
    )