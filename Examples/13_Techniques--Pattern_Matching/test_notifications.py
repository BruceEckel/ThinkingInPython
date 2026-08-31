# test_notifications.py
import notifications_match as nm
import notifications_oo as no
import pytest

@pytest.mark.parametrize("oo, data", [
    (no.Email("Hi"), nm.Email("Hi")),
    (no.Sms("Hi"), nm.Sms("Hi")),
    (no.Push("Hi"), nm.Push("Hi")),
])
def test_oo_and_match_agree(
    oo: no.Notification, data: nm.Notification
) -> None:
    assert oo.render("Dana") == nm.render(data, "Dana")
    assert oo.cost() == nm.cost(data)
