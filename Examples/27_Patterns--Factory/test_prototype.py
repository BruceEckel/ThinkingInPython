# test_prototype.py
from prototype_registry import PROTOTYPES, spawn

def test_spawn_is_independent() -> None:
    a = spawn("goblin")
    b = spawn("goblin")
    b.powers.append("curse")
    assert a.powers == ["bite"]
    assert b.powers == ["bite", "curse"]

def test_prototype_untouched() -> None:
    spawned = spawn("troll")
    spawned.hp = 1
    spawned.powers.append("bellow")
    assert PROTOTYPES["troll"].hp == 40
    assert spawned.powers is not PROTOTYPES["troll"].powers
    assert PROTOTYPES["troll"].powers == ["smash", "regen"]
