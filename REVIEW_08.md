# Review: Chapter 08 (Class Attributes and Cleanup)

The class-attribute material is excellent: the shadowing demo, the `vars()` peek,
and the `ClassVar` fix are all accurate and their outputs match. The cleanup
section has one real bug: the `cleanup.py` output and its explanation are
backwards for the CPython version the book targets.

## Must fix

1. **`cleanup.py` output and explanation are reversed (lines 152-164 and 180-184).**
   The chapter states the deletion order is Third, then Second, then First, and
   spends a paragraph explaining a last-in-first-out list teardown ("It releases
   the items from the last index down to the first... The effect is last-in,
   first-out"). On CPython 3.14.0 (the book's target) the actual order is the
   opposite, and it is deterministic (I ran it three times):

   ```
   First deleted
   2 Counter objects remaining
   Second deleted
   1 Counter objects remaining
   Third deleted
   Last Counter object deleted
   ```

   So two things need fixing:
   - The "For CPython, the output is:" block (lines 159-164) should show First,
     Second, Third.
   - The explanation (lines 180-184) currently describes the reverse order and a
     LIFO rationale. It should describe first-in, first-out (First reaches refcount
     zero first), or be reframed.

   Worth noting: this is exactly the kind of version-dependent teardown the chapter
   warns about, so the discrepancy actually reinforces the thesis ("the language
   does not promise when, or in what order, `__del__()` runs"). You could even use
   the surprise as the lesson. Either way the printed output must match what 3.14
   produces, since nothing in the build verifies these output blocks.

## Should fix

2. **Missing possessive (line 114).**
   "Python garbage collector calls an object's `__del__()` method" reads as a
   missing word. Use "Python's garbage collector" (or "The Python garbage
   collector").

3. **Inconsistent bullet punctuation (lines 5-6).**
   "- How class-level attributes behave" (no period) then "- How and when objects
   are cleaned up." (period). Make them consistent.

## Nits / optional

4. **Comment grammar and spacing (line 31).**
   `# 1 9: a instance variable , b class attr` has "a instance variable" (should
   be "an") and a space before the comma. Suggest `# 1 9: an instance variable, b
   the class attr`.

5. **General point tied to one name (line 54).**
   "the "default" value of `x`" attaches a general statement to `inside_objects`'s
   `x`. Fine, but you could phrase it generically since it follows two examples.

## Verified

- `class_attribute_confusion` (`5 5` / `1 5` / `1 9`), `inside_objects`
  (`100` / `{}` / `{'x': 1}` / `100`), `class_var` (`2`), `real_defaults`
  (`-1 100` / `100 7`), and `weak_value` (`3` / `2` / `1` / `0`) all match the
  prose exactly.
- `cleanup.py` deletion order reproduced three times on CPython 3.14.0 (First,
  Second, Third), contradicting the chapter.
- `ClassVar` usage is correct, the `WeakValueDictionary[int, Counter]` self
  forward-reference type-checks, and the function-paren convention is applied
  (`__del__()`, `__repr__()`, `close()`, `live_count()`, `print()`; `vars(A)` and
  `id(self)` correctly left with their arguments).
