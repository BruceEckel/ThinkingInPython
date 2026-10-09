<!-- outside review of Chapters/24_Patterns--Singleton.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `24_Patterns--Singleton.md` chapter:

**1. One Instance in a Class Variable (Crashing constructor)**
* **Target Text:**
```python
class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __new__(cls, arg: str) -> SingletonClassVar:
```
* **Issue:** Because `SingletonClassVar` accepts an argument in `__new__` but does not override `__init__`, Python's default `object.__init__` runs after `__new__` returns the instance. `object.__init__` rejects all arguments, so `SingletonClassVar("sausage")` will crash at runtime with `TypeError: object.__init__() takes exactly one argument (the instance to initialize)`.
* **Instruction:** Add a dummy `__init__` method to absorb the argument so the instantiation succeeds:
```python
class SingletonClassVar:
    val: list[str]
    __instance: ClassVar[SingletonClassVar | None] = None

    def __init__(self, arg: str) -> None:
        pass
```

**2. A Module Is Already a Singleton (Rebinding pitfall)**
* **Target Text:** "To replace the whole value, go through the module: `import config`, then `config.settings = {...}`. Mutate through any name. Rebind only through the module."
* **Issue:** While rebinding through the module successfully updates the module's namespace, it does not update other modules that have already executed `from config import settings`. Those modules will continue holding the old dictionary, causing the shared state to silently fracture.
* **Instruction:** Clarify the danger of rebinding even through the module. Change to: "To replace the whole value, go through the module: `import config`, then `config.settings = {...}`. However, this still fractures the state for any module that has already run `from config import settings`, as they will retain the old object. Prefer mutating the shared object over rebinding."

**3. Lazy Creation (Writes fail to proxy)**
* **Target Text:**
```python
    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)
```
* **Issue:** Because the wrapper defines `__getattr__` but not `__setattr__`, assigning a new attribute (e.g., `x.new_val = 5`) writes to the local `__dict__` of the wrapper instance, not the shared inner object. The singleton wrappers will quietly fail to share newly assigned state, a major caveat for this proxy pattern.
* **Instruction:** Point out this limitation or add `__setattr__` to the wrapper to properly forward writes to the inner singleton:
```python
    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.instance, name, value)
```

**4. Borg: Singleton by Inheritance (Incompatibility with slots)**
* **Target Text:** "The hand-written `__init__()` makes the sharing work, and silently losing the sharing is worse than failing outright."
* **Issue:** The book introduces `@record` as a slotted data class from chapter 18 onward. Because the *Borg* pattern replaces the instance dictionary, it is fundamentally incompatible with slotted classes, which suppress `__dict__`. Applying it to a slotted class will crash with an `AttributeError`.
* **Instruction:** Add a note explaining this limitation: "Because this sharing depends on replacing the instance dictionary, the *Borg* pattern is also fundamentally incompatible with classes that define `__slots__`, including this book's `@record`."

## Verdicts

Applied in commit d7325e56, after each item was tested against the chapter and run under `uv run`.

1. Rejected. `SingletonClassVar("sausage")` runs clean: `object.__init__()` rejects extra arguments only when the class leaves `__new__()` as `object.__new__()`, and this class overrides it. A probe of the listing printed `['sausage', 'eggs'] True`, and the gate runs the listing with its `#:` marker.
2. Applied, with a different fix. A probe that ran `from config import settings` and then `config.settings = {...}` left `settings` holding the old `{}`, so the chapter's "go through the module" advice reaches only code that reads `config.settings`. The paragraph now says so and names `settings.clear()` plus `settings.update()` as the in-place replacement; the reviewer's "However, this still fractures..." wording was not used.
3. Applied, with a different fix. After `a.val = ["mine"]` and `a.extra = 5` on an `OnlyOne`, `vars(a)` held both names and the shared inner list stayed `['x', 'y']`. The prose now says the proxying covers reads, says where an assignment goes, and links chapter 26's Forwarding Writes for the `__setattr__()`; the listing stays as it is, since it never assigns through a wrapper.
4. Rejected. The chapter already says a `Borg` subclass cannot be a `@dataclass`, which covers `@record`. The claim is also wrong as stated: a subclass of `Borg` that declares `__slots__` still gets a `__dict__` from the unslotted base, and a probe showed two such instances sharing one `__dict__`; only a slotted base raised the `AttributeError`.
