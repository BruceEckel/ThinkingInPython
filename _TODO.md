
Incorporate
https://www.bruceeckel.com/2018/09/16/json-encoding-python-dataclasses/
Into the "Data Classes as Types" chapter

---


Incorporate these articles into the "Decorators" chapter:
https://www.artima.com/weblogs/viewpost.jsp?thread=240808
https://www.artima.com/weblogs/viewpost.jsp?thread=240845
https://www.artima.com/weblogs/viewpost.jsp?thread=241209

---

Incorporate https://github.com/BruceEckel/LazyGuide, but not as a single chapter. Distribute the information appropriately into existing chapters, making new chapters only if it makes sense.

----

GIL presentation?

---

More testing?

---

Ask for suggestions

---

Look for other places where code is duplicated and could be lifted into a file to be imported.

---

In 02, This is confusing because I don't see an import in that listing.

However, if this file is imported as a module into another program, __name__ will not be __main__, so the __main__ code is not executed:

# import_module.py

If you run python import_module.py, you should only see 'module' imported as the result.

---
