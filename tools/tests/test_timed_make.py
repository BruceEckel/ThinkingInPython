from tools.timed_make import format_seconds, report


def test_format_seconds_under_a_minute() -> None:
    assert format_seconds(0.04) == "0.0s"
    assert format_seconds(12.34) == "12.3s"
    assert format_seconds(59.96) == "60.0s"


def test_format_seconds_minutes_and_hours() -> None:
    assert format_seconds(92.4) == "1m 32s"
    assert format_seconds(600) == "10m 00s"
    assert format_seconds(3725) == "1h 02m 05s"


def test_report_success_and_failure() -> None:
    assert report("verify", 0, 92.4) == "make verify: 1m 32s"
    assert (report("gate", 2, 40.06)
            == "make gate: failed (exit 2) after 40.1s")
