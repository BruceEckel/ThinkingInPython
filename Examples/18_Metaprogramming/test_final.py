# test_final.py
import final
import final_runtime
import pytest

def test_final_decorator_marks_class() -> None:
    # @final sets __final__ at runtime. Type checkers read it
    assert final.B.__final__ is True  # type: ignore

def test_runtime_final_cannot_be_subclassed() -> None:
    with pytest.raises(TypeError):
        class Sub(final_runtime.B):
            pass

def test_runtime_non_final_base_can_be_subclassed() -> None:
    class Ok(final_runtime.A):
        pass

    assert issubclass(Ok, final_runtime.A)
