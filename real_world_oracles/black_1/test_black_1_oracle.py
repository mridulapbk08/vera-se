import asyncio
from unittest.mock import patch

import black


def setup_function():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


def teardown_function():
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass


def test_fallback_when_process_pool_unavailable(tmp_path):
    one = (tmp_path / "one.py").resolve()
    two = (tmp_path / "two.py").resolve()

    one.write_text("print('hello')")
    two.write_text("print('hello')")

    mode = black.FileMode()

    black.write_cache(
        {},
        [one],
        mode,
    )

    with patch(
        "black.ProcessPoolExecutor",
        side_effect=OSError(),
    ):
        black.reformat_many(
            {
                one,
                two,
            },
            fast=False,
            write_back=black.WriteBack.YES,
            mode=mode,
            report=black.Report(),
        )

    assert one.read_text() == "print('hello')"

    assert (
        two.read_text()
        == 'print("hello")\n'
    )


def test_normal_executor_path_still_works(
    tmp_path,
):
    source = (
        tmp_path
        / "example.py"
    ).resolve()

    source.write_text(
        "x=1\n"
    )

    mode = black.FileMode()

    black.reformat_many(
        {source},
        fast=False,
        write_back=black.WriteBack.YES,
        mode=mode,
        report=black.Report(),
    )

    assert source.exists()


def test_reformat_many_does_not_crash_on_empty_input():
    mode = black.FileMode()

    black.reformat_many(
        set(),
        fast=False,
        write_back=black.WriteBack.YES,
        mode=mode,
        report=black.Report(),
    )