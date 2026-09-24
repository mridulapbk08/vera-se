from format_utils import clean_label


def test_clean_label():
    assert clean_label(
        "  Hello World  "
    ) == "hello world"