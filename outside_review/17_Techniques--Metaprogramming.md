<!-- outside review of Chapters/17_Techniques--Metaprogramming.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `17_Techniques--Metaprogramming.md` chapter:

**1. Self-Registration of Subclasses (unconsumed kwargs cause `TypeError`)**
* **Target Text:** "Writing `class Blue(Color, shade="cool"):` delivers `shade="cool"` to `__init_subclass__()`, so a subclass can configure its own registration. `super().__init_subclass__(**kwargs)` passes the rest up the chain..."
* **Issue:** Because `object.__init_subclass__()` rejects all keyword arguments, passing unconsumed keywords all the way up raises a `TypeError`. The text and listing imply a class can just pass `**kwargs` along, but if a reader tries the suggested `shade="cool"`, the program will crash when `super()` eventually reaches `object`.
* **Instruction:** Clarify that a class must explicitly remove its own keywords before calling `super()`. Update the text to something like: "A class must consume its own keywords (e.g., `shade = kwargs.pop('shade', None)`) before calling `super().__init_subclass__(**kwargs)`, because passing unrecognized keywords all the way to `object` raises a `TypeError`."

**2. Attributes on a Function (subclasses lose inherited handlers)**
* **Target Text:**
```python
        cls.handlers = {
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        }
```
* **Issue:** Because this replaces `cls.handlers` with a new dictionary containing *only* the methods defined directly in `vars(cls)`, subclasses lose all event handlers inherited from their base classes. A subclass like `SubmitButton(Button)` with no new methods would have an empty `handlers` dictionary and fail to dispatch `"click"`.
* **Instruction:** Change the assignment to copy the parent's handlers before adding the new ones. For example:
```python
        cls.handlers = getattr(cls, "handlers", {}).copy()
        cls.handlers.update({
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        })
```

**3. Generating Classes with `type()` (metaclass resolution)**
* **Target Text:** "A class definition is shorthand for calling `type()`:"
* **Issue:** Calling `type()` directly forces the use of the `type` metaclass, which will raise a `TypeError` if a base class uses a custom metaclass (like `abc.ABC`). The true programmatic equivalent of the `class` statement that correctly calculates the metaclass and runs `__prepare__` is `types.new_class()` from the standard library.
* **Instruction:** Change to "A simple class definition is roughly shorthand for calling `type()`:" and add a sentence noting the robust alternative: "To build a class programmatically that correctly determines the metaclass from its bases, use `types.new_class()` instead."

**4. Building Each Class on First Lookup (comment filtering bug)**
* **Target Text:** `if line.strip() and not line.startswith("#")`
* **Issue:** This only filters out comments that start exactly at the first character of the line. A comment indented with spaces (e.g., `  # a comment`) will pass this check but fail to unpack in `class_name, hour, minute = line.replace(":", " ").split()`, raising a `ValueError`.
* **Instruction:** Apply `.strip()` before checking for the comment character: `if line.strip() and not line.strip().startswith("#")`.

**5. `display_object()` Reference (tool ignores the chapter's own annotation advice)**
* **Target Text:**
```python
    return {**inspect.get_annotations(base)
            for base in reversed(cls.__mro__)}
```
* **Issue:** The chapter correctly advises that tools reading annotations should request `Format.FORWARDREF` or `Format.STRING` to avoid `NameError`s when names are undefined. However, the book's own `display_object()` tool calls `get_annotations` without a format argument, using the default `Format.VALUE`, leaving it vulnerable to the exact crash the text warns against.
* **Instruction:** Update the tool to practice what the chapter preaches by passing a safe format: `return {**inspect.get_annotations(base, format=annotationlib.Format.STRING) for base in reversed(cls.__mro__)}` (and add `import annotationlib` to the file).

## Verdicts

Applied in commit 60d7d2fa, after each item was tested against the chapter and run under `uv run`.

1. Applied. An undeclared keyword reaches `object.__init_subclass__()`: `class Blue(Color, shade="cool")` against the listing raised `TypeError: Blue.__init_subclass__() takes no keyword arguments`. The prose now shows the declared-parameter form and names where a stray keyword fails.
2. Applied. A `SubmitButton(Button)` with one marked method had `handlers == {'submit': ...}` and lost `click`. `Widget` now starts each table from the inherited one, and the listing prints `SubmitButton`'s three events.
3. Rejected. `type("X", (abc.ABC,), {})` returns a class whose metaclass is `ABCMeta`; `type.__new__()` picks the most derived metaclass, so no `TypeError` arises. `types.new_class()` differs in running `__prepare__()`, which the item did not claim.
4. Rejected. `schedule.txt` in the listing has no comment lines, so the filter handles the input the listing defines; an indented comment is a case the listing never sees.
5. Applied. `display_object()` now asks for `Format.FORWARDREF`. The whole-book verify showed no marker change, since every annotation it reads resolves.
