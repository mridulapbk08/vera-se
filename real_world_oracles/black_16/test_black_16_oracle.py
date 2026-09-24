import re
from pathlib import Path
from unittest.mock import MagicMock

import black


def test_symlink_outside_root_is_ignored():
    root = Path("/tmp/root").resolve()

    path = MagicMock()
    child = MagicMock()

    path.iterdir.return_value = [child]
    child.resolve.return_value = Path("/outside/project/file.py")
    child.is_symlink.return_value = True

    include = re.compile(black.DEFAULT_INCLUDES)
    exclude = re.compile(black.DEFAULT_EXCLUDES)
    report = black.Report()

    result = list(
        black.gen_python_files_in_dir(
            path,
            root,
            include,
            exclude,
            report,
        )
    )

    assert result == []


def test_non_symlink_outside_root_still_raises():
    root = Path("/tmp/root").resolve()

    path = MagicMock()
    child = MagicMock()

    path.iterdir.return_value = [child]
    child.resolve.return_value = Path("/outside/project/file.py")
    child.is_symlink.return_value = False

    include = re.compile(black.DEFAULT_INCLUDES)
    exclude = re.compile(black.DEFAULT_EXCLUDES)
    report = black.Report()

    try:
        list(
            black.gen_python_files_in_dir(
                path,
                root,
                include,
                exclude,
                report,
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for non-symlink path outside root")


def test_normal_file_inside_root_is_discovered():
    root = Path("/tmp/root").resolve()

    path = MagicMock()
    child = MagicMock()

    path.iterdir.return_value = [child]

    child.resolve.return_value = root / "example.py"
    child.is_dir.return_value = False
    child.is_symlink.return_value = False

    include = re.compile(black.DEFAULT_INCLUDES)
    exclude = re.compile(black.DEFAULT_EXCLUDES)
    report = black.Report()

    result = list(
        black.gen_python_files_in_dir(
            path,
            root,
            include,
            exclude,
            report,
        )
    )

    assert len(result) == 1
