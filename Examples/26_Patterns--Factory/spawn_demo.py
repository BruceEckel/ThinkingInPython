# spawn_demo.py
from prototype_registry import spawn

a = spawn("goblin")
b = spawn("goblin")
b.powers.append("curse")
print(a.powers, b.powers)  # The copies are independent
#: ['bite'] ['bite', 'curse']
print(spawn("troll"))
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
