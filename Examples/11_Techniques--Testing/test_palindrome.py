# test_palindrome.py
from palindrome import is_palindrome

def test_empty_string_is_a_palindrome() -> None:
    assert is_palindrome("")

def test_racecar_is_a_palindrome() -> None:
    assert is_palindrome("racecar")

def test_hello_is_not_a_palindrome() -> None:
    assert not is_palindrome("hello")
