Currently >>
/loop In Markdown\14_Singleton.md:

    # config.py
    settings: dict[str, str] = {}

    # anywhere.py
    from config import settings   # the same dict, everywhere

These are named, extractable examples but they are not extracted to Examples\14_Singleton.
Look through the book for similar cases and fix them.
Also if there are code fragments that can be turned into extractable examples fix those.
The goal is to maximize the automatic checking of all code that appears in the book.

---

Could rats_and_mazes be done with async instead of threading?

---

Incorporate https://github.com/BruceEckel/LazyGuide, but not as a single chapter. Distribute the information appropriately into existing chapters, making new chapters only if it makes sense.

---

https://www.bruceeckel.com/2018/09/16/json-encoding-python-dataclasses/

---


Incorporate these articles into the "Decorators" chapter:
https://www.artima.com/weblogs/viewpost.jsp?thread=240808
https://www.artima.com/weblogs/viewpost.jsp?thread=240845
https://www.artima.com/weblogs/viewpost.jsp?thread=241209

----

GIL presentation?
