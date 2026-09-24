import pytest

from math_utils import average


def test_decimal_average():
    result = average(1, 2)

    assert result == pytest.approx(1.5)
    assert isinstance(result, float)


def test_negative_numbers():
    assert average(
        -10,
        -20,
    ) == pytest.approx(-15.0)


def test_mixed_signs():
    assert average(
        -5,
        15,
    ) == pytest.approx(5.0)


def test_fractional_inputs():
    assert average(
        1.2,
        2.8,
    ) == pytest.approx(2.0)


def test_precision():
    assert average(
        1,
        3,
    ) == pytest.approx(2.0)


def test_equal_values():
    assert average(
        5,
        5,
    ) == pytest.approx(5.0)


def test_equal_negative_values():
    assert average(
        -4,
        -4,
    ) == pytest.approx(-4.0)


def test_return_type():
    result = average(
        10,
        20,
    )

    assert isinstance(
        result,
        float,
    )