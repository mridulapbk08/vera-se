from format_utils import clean_label


def test_uppercase():
    assert clean_label(
        "  TEST  "
    ) == "test"


def test_leading_space():
    assert clean_label(
        "  example"
    ) == "example"


def test_trailing_space():
    assert clean_label(
        "example   "
    ) == "example"


def test_hyphen():
    assert clean_label(
        "  Hello-World  "
    ) == "hello-world"