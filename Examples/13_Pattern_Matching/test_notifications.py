# test_notifications.py
import notifications_match as nm
import notifications_oo as no

def test_oo_and_match_agree() -> None:
    assert (no.Email("Hi").render("Dana")
            == nm.render(nm.Email("Hi"), "Dana"))
    assert no.Sms("Hi").cost() == nm.cost(nm.Sms("Hi"))
