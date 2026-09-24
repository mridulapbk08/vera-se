from format_utils import clean_label


def test_preserves_multiple_internal_spaces():
    assert clean_label(
        "  Hello  World  "
    ) == "hello  world"


def test_preserves_periods():
    assert clean_label(
        "  Version 2.0  "
    ) == "version 2.0"


def test_preserves_colon():
    assert clean_label(
        "  Name: Alice  "
    ) == "name: alice"


def test_preserves_slash():
    assert clean_label(
        "  Input/Output  "
    ) == "input/output"


def test_already_clean():
    assert clean_label(
        "hello"
    ) == "hello"