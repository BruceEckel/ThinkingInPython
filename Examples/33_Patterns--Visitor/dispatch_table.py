# dispatch_table.py
from visitor_singledispatch import Ranunculus, nectar

print(sorted(cls.__name__ for cls in nectar.registry))
#: ['Chrysanthemum', 'Gladiolus', 'object']
print(nectar.dispatch(Ranunculus)
      is nectar.registry[object])
#: True
