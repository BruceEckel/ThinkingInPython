# methods_demo.py
from arena import all_pairs, duel
from paper_scissors_rock import Item

for player, opponent in all_pairs(Item):
    duel(player, opponent)
#: Paper <--> Paper : draw
#: Paper <--> Scissors : lose
#: Paper <--> Rock : win
#: Scissors <--> Paper : win
#: Scissors <--> Scissors : draw
#: Scissors <--> Rock : lose
#: Rock <--> Paper : lose
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
