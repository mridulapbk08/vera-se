import black


def format_code(source: str) -> str:
    try:
        return black.format_file_contents(
            source,
            fast=False,
            mode=black.FileMode(),
        )
    except black.NothingChanged:
        return source


def test_long_tuple_unpacking_wraps_left_side():
    source = (
        "first_really_long_variable_name, "
        "second_really_long_variable_name, "
        "third_really_long_variable_name, "
        "fourth_really_long_variable_name = 1, 2, 3\n"
    )

    result = format_code(source)

    assert result.startswith("(\n")
    assert ") = (1, 2, 3)\n" in result


def test_short_tuple_assignment_remains_compact():
    source = "a, b = 1, 2\n"

    result = format_code(source)

    assert result == "a, b = 1, 2\n"


def test_regular_assignment_behavior_preserved():
    source = "some_really_long_variable_name = [1,2,3]\n"

    result = format_code(source)

    assert "some_really_long_variable_name" in result
    assert "[1, 2, 3]" in result