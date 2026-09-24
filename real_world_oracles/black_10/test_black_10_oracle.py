import black


def format_code(source: str) -> str:
    return black.format_str(
        source,
        line_length=black.DEFAULT_LINE_LENGTH,
    )


def test_tab_indented_comment_matches_space_indentation():
    source_tab = (
        "if 1:\n"
        "\tif 2:\n"
        "\t\tpass\n"
        "\t\t# comment\n"
        "\tpass\n"
    )

    expected = (
        "if 1:\n"
        "    if 2:\n"
        "        pass\n"
        "        # comment\n"
        "    pass\n"
    )

    result = format_code(source_tab)

    assert result == expected


def test_dedented_comment_with_tabs_is_preserved_correctly():
    source_tab = (
        "if 1:\n"
        "\tif 2:\n"
        "\t\tpass\n"
        "\t# comment\n"
        "\tpass\n"
    )

    expected = (
        "if 1:\n"
        "    if 2:\n"
        "        pass\n"
        "    # comment\n"
        "    pass\n"
    )

    result = format_code(source_tab)

    assert result == expected


def test_space_indented_input_remains_unchanged():
    source = (
        "if 1:\n"
        "    if 2:\n"
        "        pass\n"
        "        # comment\n"
        "    pass\n"
    )

    result = format_code(source)

    assert result == source
