# chladni_plate/chladni_demo.py
from chladni import Plate

plate = Plate(grains=2000, mode=(2, 3), seed=42)
steps = 0
for target in (0, 100, 400, 1200):
    for _ in range(target - steps):
        plate.step()
    steps = target
    print(f"steps {target:4}: "
          f"agitation {plate.agitation():.3f}")
print(plate.render())
#: steps    0: agitation 0.585
#: steps  100: agitation 0.073
#: steps  400: agitation 0.005
#: steps 1200: agitation 0.000
#:  *.                     #                       #
#:  :##                    #                       #
#:     ##                  ##                      #
#:       ##                 ##.                    #
#:         ##                 ###                  .#
#:           ##                  ######              ##########
#:             ##                      ########
#:               ##                           ###
#:                 ##                           ##
#:                   ##                          #*
#:                     ##                         #
#:                       ##                       #
#: #######                 ##                      #
#:       *##                 ##                    #:
#:         ##                  ##                   #
#:           #                   ##                  #:
#:           ##                    ##                 ##*
#:            #                      ##                 #######
#:             #                       ##
#:             #                         ##
#:             :#                          ##
#:              ##                           ##
#:               ##*                           ##
#:                 ########                      ##
#: ######*###              ######                  ##
#:           ##                  ###                 ##
#:            #                    .##                 ##
#:            #                      ##                  ##.
#:            #                       #                    ##.
#:            #                       #                    .:##
