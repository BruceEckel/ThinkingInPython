# test_null_logger.py
import null_logger as nl
import optional_logger as ol

def test_versions_agree() -> None:
    prices = [1.0, 2.0, 3.5]
    assert ol.total(prices) == nl.total(prices) == 6.5

def test_list_logger_records_each_step() -> None:
    logger = nl.ListLogger()
    nl.total([1.0, 2.0], logger)
    assert logger.lines == [
        "added 1.0, total 1.0", "added 2.0, total 3.0"]
