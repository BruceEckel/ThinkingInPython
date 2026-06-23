# Review: Chapter 06 (Classes)

Good coverage: classes, inheritance, `@override`, properties (with setter),
`__str__`/`__repr__`, static and class methods, and the `import`-as-composition
trick. All eight scripts run and match their inline output comments.

## Should fix

1. **Parameter `str` shadows the builtin (lines 11, 13; also simple2.py line 70).**
   `def __init__(self, str):` then `self.s = str` uses `str` as a parameter name,
   hiding the builtin inside the constructor. It is the first class example, so it
   sets a poor pattern. Rename to `s` or `text`. ruff does not flag this (the
   builtin-shadow rules are not in the active set).

2. **"The `f()` method" is a function, not a method (lines 109, 112).**
   `f` is the nested function defined in `__main__` (the code comment on line 92
   correctly calls it "Local/nested function"). The prose calls it "The `f()`
   method". Change "method" to "function" in both places.

## Nits / optional

3. **`__init__` called "the constructor" (lines 40-42, 98, 260).**
   Strictly, `__init__()` is the initializer; `__new__()` is the constructor, a
   distinction the Metaprogramming chapter draws explicitly. "Constructor" is the
   common informal usage, but it reads as slightly inconsistent with chapter 15.
   Optional: call it the initializer, or add a one-line aside that Python people
   usually say "constructor" for `__init__`.

4. **One-line `def` (line 92).**
   `def f(obj): obj.show()` puts the body on the `def` line. ruff allows it (E704
   is off), but the rest of the book writes the body on its own line. Consider
   expanding it for consistency and readability.

5. **Informal aside (line 34).**
   "(if you do not use `self` you will probably confuse people)" is fine; just
   noting it is the chattiest line in the chapter if you want a uniform tone.

## Verified

- Ran `simple_class`, `simple2`, `override_intro`, `properties`,
  `property_setter`, `representation`, `class_methods`, `compose`. All outputs
  match, including the five "Overridden show() method" lines in `simple2`
  (display + show + show_twice x2 + f(x)) and `c.area` = 314.159,
  `from_fahrenheit(212)` -> 100.
- ruff passes; it does not flag the `str` parameter or the one-line `def`.
- `@override` section is accurate (runtime no-op, type-checker validation, skip on
  constructors). Function-paren convention applied throughout (`__init__()`,
  `show()`, `super()`, `__repr__()`, `display()`).
