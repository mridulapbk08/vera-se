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


def test_import_with_trailing_comments_places_comma_before_comments():
    source = (
        "from package import (\n"
        "    first,\n"
        "    second\n"
        "    # keep this comment\n"
        ")\n"
    )

    result = format_code(source)

    assert "second," in result
    assert "# keep this comment" in result
    assert "\n    ,\n" not in result


def test_import_already_with_comma_is_not_given_extra_comma():
    source = (
        "from package import (\n"
        "    first,\n"
        "    second,\n"
        "    # comment\n"
        ")\n"
    )

    result = format_code(source)

    assert "second," in result
    assert "# comment" in result
    assert "\n    ,\n" not in result


def test_normal_import_without_comments_still_works():
    source = (
        "from package import (\n"
        "    first,\n"
        "    second\n"
        ")\n"
    )

    result = format_code(source)

    assert "first" in result
    assert "second" in result
    assert "\n    ,\n" not in result
