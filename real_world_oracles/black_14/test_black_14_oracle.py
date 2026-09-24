import black


def parse(source: str):
    return black.lib2to3_parse(source)


def test_single_aliased_future_import_is_detected():
    node = parse(
        "from __future__ import unicode_literals as _unicode_literals\n"
    )

    result = black.get_future_imports(node)

    assert result == {"unicode_literals"}


def test_multiple_future_imports_with_alias_are_detected():
    node = parse(
        "from __future__ import unicode_literals as _lol, print_function\n"
    )

    result = black.get_future_imports(node)

    assert result == {"unicode_literals", "print_function"}


def test_normal_future_import_still_works():
    node = parse(
        "from __future__ import absolute_import\n"
    )

    result = black.get_future_imports(node)

    assert result == {"absolute_import"}


def test_non_future_import_is_ignored():
    node = parse(
        "from some.module import thing\n"
    )

    result = black.get_future_imports(node)

    assert result == set()
