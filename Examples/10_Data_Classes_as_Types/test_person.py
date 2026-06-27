# test_person.py
import pytest
from person import EmailAddress, FullName
from validation import TypeFailure

@pytest.mark.parametrize("bad", ["Bruce", "", "   "])
def test_full_name_needs_two_parts(bad: str) -> None:
    with pytest.raises(TypeFailure):
        FullName(bad)

@pytest.mark.parametrize("bad", ["bruce", "example.com", ""])
def test_email_needs_at_sign(bad: str) -> None:
    with pytest.raises(TypeFailure):
        EmailAddress(bad)
