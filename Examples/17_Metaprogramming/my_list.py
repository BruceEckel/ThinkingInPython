# my_list.py
from display import display_object

def howdy(self, you: str) -> None:
    print(f"Howdy, {you}")

MyList = type("MyList", (list,), dict(x=42, howdy=howdy))

display_object(MyList)
#: [Attributes]
#:   • x = 42 [CV]
#: [Methods]
#:   • append(self, object, /)
#:   • clear(self, /)
#:   • copy(self, /)
#:   • count(self, value, /)
#:   • extend(self, iterable, /)
#:   • howdy(self, you: str) -> None
#:   • index(self, value, start=0, stop=9223372036854775807, /)
#:   • insert(self, index, object, /)
#:   • pop(self, index=-1, /)
#:   • remove(self, value, /)
#:   • reverse(self, /)
#:   • sort(self, /, *, key=None, reverse=False)

ml = MyList()
ml.append("Camembert")
print(ml)
#: ['Camembert']
print(ml.x)
#: 42
ml.howdy("John")
#: Howdy, John

print(ml.__class__.__class__)
#: <class 'type'>
