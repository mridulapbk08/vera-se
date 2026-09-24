import black


PY27_MODE = black.FileMode(
    target_versions={black.TargetVersion.PY27}
)

PY36_MODE = black.FileMode(
    target_versions={black.TargetVersion.PY36}
)


def format_code(source: str, mode: black.FileMode) -> str:
    return black.format_str(
        source,
        mode=mode,
    )


def test_python2_future_print_function_is_supported():
    source = (
        "#!/usr/bin/env python2\n"
        "from __future__ import print_function\n"
        "\n"
        "print('hello')\n"
        "print(a, file=sys.stderr)\n"
    )

    result = format_code(source, PY27_MODE)

    assert 'print("hello")' in result
    assert "print(a, file=sys.stderr)" in result


def test_regular_python2_print_statement_still_supported():
    source = (
        "#!/usr/bin/env python2\n"
        "print 'hello'\n"
    )

    result = format_code(source, PY27_MODE)

    assert 'print "hello"' in result


def test_python3_target_still_formats_normally():
    source = "print('hello')\n"

    result = format_code(source, PY36_MODE)

    assert 'print("hello")' in result
