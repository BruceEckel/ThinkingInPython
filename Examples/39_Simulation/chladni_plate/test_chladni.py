# chladni_plate/test_chladni.py
from chladni import Plate

def test_noise_settles_grains_onto_quiet_lines() -> None:
    plate = Plate(grains=500, mode=(2, 3), seed=1)
    before = plate.agitation()
    for _ in range(400):
        plate.step()
    assert plate.agitation() < before / 10

def test_kicks_never_knock_grains_off_the_plate() -> None:
    plate = Plate(grains=200, mode=(3, 5), seed=2)
    for _ in range(300):
        plate.step(kick=0.2)
    assert all(0.0 <= g.x <= 1.0 and 0.0 <= g.y <= 1.0
               for g in plate.grains)
