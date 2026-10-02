# test_case_mapping.py
import unicodedata

MICRO = "µ"

def test_upper_leaves_the_micro_sign_in_the_greek_block(
) -> None:
    assert unicodedata.name(MICRO) == "MICRO SIGN"
    assert (unicodedata.name(MICRO.upper())
            == "GREEK CAPITAL LETTER MU")
    assert (unicodedata.name(MICRO.upper().lower())
            == "GREEK SMALL LETTER MU")
    # Already lowercase, so unchanged
    assert MICRO.lower() == MICRO
    assert MICRO.upper().lower() != MICRO.lower()
