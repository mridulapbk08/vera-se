import black


def format_code(source: str) -> str:
    return black.format_file_contents(
        source,
        fast=False,
        mode=black.FileMode(),
    )


def test_leading_backslash_does_not_create_blank_lines():
    source = "\\\n\n\nprint('hello')\n"

    result = format_code(source)

    assert not result.startswith("\n")
    assert 'print("hello")' in result


def test_normal_file_does_not_gain_leading_blank_lines():
    source = "x=1\n"

    result = format_code(source)

    assert result == "x = 1\n"


def test_regular_internal_spacing_behavior_preserved():
    source = (
        "x=1\n"
        "\n"
        "\n"
        "def hello():\n"
        "    pass\n"
    )

    result = format_code(source)

    assert "x = 1" in result
    assert "def hello():" in result
    assert not result.startswith("\n")