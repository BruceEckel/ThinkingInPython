# test_person.py
import pytest
from person import EmailAddress, FullName, Person
from validation import TypeFailure

def test_person_composes_validated_parts() -> None:
    person = Person(FullName("Grace Hopper"),
                    EmailAddress("grace@example.com"))
    assert person.name.text == "Grace Hopper"
    assert person.email.text == "grace@example.com"

@pytest.mark.parametrize("bad", ["Grace", "", "   "])
def test_full_name_needs_two_parts(bad: str) -> None:
    with pytest.raises(TypeFailure):
        FullName(bad)

@pytest.mark.parametrize(
    "bad", ["grace", "example.com", ""])
def test_email_needs_at_sign(bad: str) -> None:
    with pytest.raises(TypeFailure):
        EmailAddress(bad)
