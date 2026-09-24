from pathlib import Path

from click.testing import CliRunner

import black


def test_missing_config_returns_usage_error(tmp_path):
    runner = CliRunner()

    source = tmp_path / "sample.py"
    source.write_text("x=1\n")

    missing_config = (
        tmp_path
        / "missing.toml"
    )

    result = runner.invoke(
        black.main,
        [
            "--config",
            str(missing_config),
            str(source),
        ],
    )

    assert result.exit_code == 2


def test_existing_config_file_is_accepted(tmp_path):
    runner = CliRunner()

    source = tmp_path / "sample.py"
    source.write_text("x=1\n")

    config = tmp_path / "pyproject.toml"

    config.write_text(
        """
[tool.black]
line-length = 88
""".strip()
    )

    result = runner.invoke(
        black.main,
        [
            "--config",
            str(config),
            str(source),
        ],
    )

    assert result.exit_code == 0


def test_normal_formatting_without_config_still_works(
    tmp_path,
):
    runner = CliRunner()

    source = tmp_path / "sample.py"

    source.write_text(
        "x=1\n"
    )

    result = runner.invoke(
        black.main,
        [
            str(source),
        ],
    )

    assert result.exit_code == 0

    assert (
        source.read_text()
        == "x = 1\n"
    )