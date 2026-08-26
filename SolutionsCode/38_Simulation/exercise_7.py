# exercise_7.py
from chladni import Plate, membrane

plate = Plate(grains=2000, mode=(2, 3), seed=42,
              field=membrane)
steps = 0
for target in (0, 100, 400, 1200):
    for _ in range(target - steps):
        plate.step()
    steps = target
    print(f"steps {target:4}: "
          f"agitation {plate.agitation():.3f}")
#: steps    0: agitation 0.406
#: steps  100: agitation 0.100
#: steps  400: agitation 0.014
#: steps 1200: agitation 0.002
print(plate.render(width=40, height=20))
#: #:**# ######:#####..#:##*###############
#: #                  ##                  #
#: #                  ##                 .#
#: #    .             ##                  #
#: #                  ##                  #
#: #                  #*                  #
#: ######################*#################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: *                 .##   .             .#
#: ########################################
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #                  ##                  #
#: #               .  ##                  #
#: ##############**##:##.#:##############.#
