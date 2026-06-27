# test_distance_protocol.py
import distance_protocol as dp

def test_protocol_and_adapter() -> None:
    assert dp.distance(dp.Point(3, 0), dp.Point(0, 4)) == 5
    assert dp.distance(dp.PairCoord(dp.Pair(3, 0)),
                       dp.PairCoord(dp.Pair(0, 4))) == 5
