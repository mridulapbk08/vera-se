import black


def format_code(source: str) -> str:
    return black.format_str(
        source,
        line_length=black.DEFAULT_LINE_LENGTH,
    )


def test_async_for_generator_expression_is_supported():
    source = (
        "def f():\n"
        "    return (i*2 async for i in arange(42))\n"
    )

    result = format_code(source)

    assert "i * 2 async for i in arange(42)" in result


def test_normal_for_generator_expression_still_works():
    source = (
        "def f():\n"
        "    return (i*2 for i in range(42))\n"
    )

    result = format_code(source)

    assert "i * 2 for i in range(42)" in result


def test_async_def_still_formats_normally():
    source = (
        "async def f():\n"
        "    return 1\n"
    )

    result = format_code(source)

    assert "async def f():" in result
    assert "return 1" in result
