# Review: Chapter 07 (Static Typing)

A strong chapter. The duck-typing vs structural-typing framing is clear, and the
Type Hint Summary tables are accurate and genuinely useful. I spot-checked the
tables against current typing and found no errors. The three runnable examples
pass and `ty` is clean on the chapter.

## Should fix

1. **The `area` example is an unchecked fragment (lines 94-99).**
   This block has no `# filename.py` marker, so it extracts as a fragment, not a
   file. That means `ty` never actually runs on it, so the inline claim
   `# ty: argument of type "str" is not assignable to "int"` is not verified by
   the build. The illustration is fine, but since the chapter's whole point is
   that the checker catches this, consider making it a real file so the promised
   error message stays correct as `ty` evolves. (I confirmed only
   `typed_basics.py`, `final_constants.py`, and `protocols.py` extract as files.)

## Nits / optional

2. **Pronoun agreement (line 103).**
   "Bugs surface later, often far from the line that caused it." Plural "Bugs" vs
   singular "it". Either "from the lines that caused them" or recast as "A bug
   surfaces later, often far from the line that caused it."

3. **Slightly circular (lines 13-14).**
   "does not care if your type hints are logically correct as long as they are
   structurally and syntactically valid. The runtime ignores properly-formed type
   hints." The two sentences restate each other. Consider collapsing to one: the
   runtime only requires that hints parse; it ignores whether they are correct.

## Verified

- Ran `typed_basics` (`ababab` / `6`), `final_constants` (`3 hello`), `protocols`
  (`circle` / `square`). All outputs match.
- `ty check` passes on the whole chapter.
- Spot-checked the summary tables: `Final`/`ClassVar`, `Protocol` /
  `@runtime_checkable`, `TypedDict` with `Required`/`NotRequired`/`ReadOnly`, the
  PEP 695 generics (`def f[T]`, `class Box[T]`, bounds), `ParamSpec` /
  `TypeVarTuple` / `Unpack` / `Concatenate`, and `@overload`/`@final`/`cast`/
  `assert_never` are all described correctly. The old spellings
  (`Optional`/`Union`/`List`/`Dict`) are correctly flagged as legacy at the end.
- Function-paren convention applied (`isinstance()`); call forms that show
  arguments in the tables (`cast(T, x)`, `NewType("Id", int)`, `assert_never(x)`)
  are correctly left as written.

Overall this chapter needs the least work of the batch.
