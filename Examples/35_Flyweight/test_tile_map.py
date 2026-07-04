# test_tile_map.py
import pytest
from tile_map import parse_map, tile

def test_same_symbol_same_object() -> None:
    assert tile(".") is tile(".")
    assert tile(".") is not tile("#")

def test_map_shares_tiles() -> None:
    field = parse_map("..\n~~")
    assert field[0][0] is field[0][1]
    assert field[1][0] is field[1][1]
    assert not field[1][0].walkable

def test_unknown_symbol_raises() -> None:
    with pytest.raises(KeyError):
        tile("?")
