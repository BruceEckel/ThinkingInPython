"""Tests for tools/target_times.py: the cache, the tier baseline, and
what the listing shows from them."""
from pathlib import Path

from tools.target_times import (
    Timing, baseline, cached, record, short, tier, timings, write_baseline)


def test_tier_thresholds():
    assert tier(0.3) == "quick"
    assert tier(4.99) == "quick"
    assert tier(5.0) == "normal"
    assert tier(29.9) == "normal"
    assert tier(30.0) == "long"
    assert tier(119.9) == "long"
    assert tier(120.0) == "very long"
    assert tier(3600) == "very long"


def test_short_labels():
    assert short(0.83) == "0.8s"
    assert short(9.96) == "10.0s"
    assert short(55.8) == "56s"
    assert short(92.4) == "1m 32s"


def test_record_replaces_the_last_run_and_creates_the_file(tmp_path: Path):
    cache = tmp_path / "build" / "target_times.json"
    assert cached(cache) == {}
    record("verify", 55.84, cache)
    record("sweep", 40.0, cache)
    record("verify", 60.0, cache)
    assert cached(cache) == {"verify": 60.0, "sweep": 40.0}


def test_a_corrupt_cache_reads_as_empty_and_is_overwritten(tmp_path: Path):
    cache = tmp_path / "t.json"
    cache.write_text("not json", encoding="utf-8")
    assert cached(cache) == {}
    record("ty", 3.0, cache)
    assert cached(cache) == {"ty": 3.0}


def test_write_baseline_merges_over_existing_lines(tmp_path: Path):
    path = tmp_path / "target_tiers.txt"
    assert baseline(path) == {}
    write_baseline({"verify": 20.0, "ty": 3.0}, path)
    write_baseline({"ty": 40.0}, path)
    assert baseline(path) == {"ty": "long", "verify": "normal"}
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#")
    assert text.index("ty\tlong") < text.index("verify\tnormal")


def test_timings_prefer_this_machines_seconds_over_the_tier(tmp_path: Path):
    cache, base = tmp_path / "c.json", tmp_path / "b.txt"
    write_baseline({"verify": 56.0, "gate": 40.0}, base)
    record("verify", 61.5, cache)
    shown = timings(cache, base)
    assert shown["verify"] == Timing("1m 02s", "long")
    assert shown["gate"] == Timing("long", "long")
    assert "sweep" not in shown
