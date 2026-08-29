"""Tests for tools/release.py (the pure naming pieces).

The orchestration itself (gate, builds, gh) is deliberately untested
here: it shells out to make and GitHub, and verify_targets.py excludes
the target for the same reason. What is testable is the naming: a bad
tag or title publishes a public release under the wrong name.
"""
from release import VERSION_RE, tag_for, title_for, to_prune, version_key


def test_version_gets_v_prefixed_tag() -> None:
    assert tag_for("1.0") == "v1.0"

def test_already_prefixed_version_is_kept() -> None:
    assert tag_for("v1.0") == "v1.0"

def test_title_uses_the_bare_version() -> None:
    assert title_for("1.0") == "Thinking in Python 1.0"
    assert title_for("v1.0") == "Thinking in Python 1.0"

def test_plausible_versions_are_accepted() -> None:
    for version in ("1.0", "v1.0", "2.0-beta1", "1.0.3", "2026_08"):
        assert VERSION_RE.match(version), version

def test_shell_hostile_versions_are_rejected() -> None:
    for version in ("", "1 0", "1.0;rm", "-1.0", "a/b", "1.0\n"):
        assert not VERSION_RE.match(version), version

def test_version_key_reads_release_tags_only() -> None:
    assert version_key("v0.4.2") == (0, 4, 2)
    assert version_key("1.0") == (1, 0)
    assert version_key("v0.4.2-rc1") is None
    assert version_key("cover-v2") is None

def test_to_prune_keeps_the_newest_two_by_version_number() -> None:
    tags = ["v0.4.2", "v0.10.0", "v0.1.0", "v0.5.1", "v0.5.0", "v0.4.0"]
    assert to_prune(tags) == ["v0.5.0", "v0.4.2", "v0.4.0", "v0.1.0"]
    assert to_prune(tags, keep=1) == [
        "v0.5.1", "v0.5.0", "v0.4.2", "v0.4.0", "v0.1.0"]
    assert to_prune(tags, keep=10) == []

def test_to_prune_never_touches_hand_made_releases() -> None:
    assert to_prune(["v0.2.0", "v0.1.0", "draft", "v0.3.0", "v0.4.0-rc1"]) == [
        "v0.1.0"]
    assert to_prune([]) == []
