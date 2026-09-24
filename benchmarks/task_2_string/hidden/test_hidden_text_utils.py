from text_utils import normalize_name


def test_normalize_name_upper():
    assert normalize_name("BOB") == "bob"


def test_normalize_name_spaces():
    assert normalize_name("  Charlie") == "charlie"


def test_normalize_name_trailing():
    assert normalize_name("David   ") == "david"


def test_preserves_internal_space():
    assert normalize_name(
        "  Mary Jane  "
    ) == "mary jane"


def test_preserves_hyphen():
    assert normalize_name(
        "  Anne-Marie  "
    ) == "anne-marie"


def test_preserves_apostrophe():
    assert normalize_name(
        "  O'Connor  "
    ) == "o'connor"