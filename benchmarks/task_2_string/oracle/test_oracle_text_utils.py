from text_utils import normalize_name


def test_preserves_middle_spacing():
    assert normalize_name(
        "  Mary  Jane  "
    ) == "mary  jane"


def test_preserves_period():
    assert normalize_name(
        "  Dr. Smith  "
    ) == "dr. smith"


def test_preserves_hyphen():
    assert normalize_name(
        "  Jean-Luc  "
    ) == "jean-luc"


def test_preserves_apostrophe():
    assert normalize_name(
        "  D'Angelo  "
    ) == "d'angelo"


def test_already_normalized():
    assert normalize_name(
        "alice"
    ) == "alice"