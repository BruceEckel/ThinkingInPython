<!-- outside review of Chapters/11_Techniques--Testing.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `11_Techniques--Testing.md` chapter:

**1. Filesystem and Environment: Path Expansion (Contradiction)**

* **Target Text:** `return Path(os.environ.get("APP_DATA", "."))`
* **Issue:** The prose explicitly warns that "a variable that may hold `~/data` needs `.expanduser()` on the result," but the `storage.py` listing does not apply it. The code should demonstrate the practice the prose requires.
* **Instruction:** Change the return statement to: `return Path(os.environ.get("APP_DATA", ".")).expanduser()`

**2. White-Box and Black-Box Tests: Type Checker Behavior (Technical accuracy)**

* **Target Text:** "ty does not model this rewriting, so its report on the code below disagrees with what runs:"
* **Issue:** The type checker (`ty`/Pyright) actually *does* model name mangling. It marks `v._Vault__pin` as an unresolved attribute outside the class because it enforces the privacy the mangling implies, deliberately hiding the name from public access. The text mischaracterizes this deliberate access control as an inability to model the rewriting.
* **Instruction:** Change the sentence to: "ty models this rewriting but enforces the intended privacy, deliberately hiding the mangled name from outside access, so its report disagrees with what runs:"

**3. Random Numbers: RNG Instantiation (Caveat)**

* **Target Text:** "Because the function takes its source of randomness as an argument, production code hands it a fresh `random.Random()` while the test hands it a seeded one."
* **Issue:** Instantiating a "fresh" `random.Random()` on every call in production code is inefficient, as it repeatedly requests entropy from the operating system to seed itself. It is better to state that production hands it a standard instance, leaving its reuse up to the caller.
* **Instruction:** Change the wording to: "Because the function takes its source of randomness as an argument, production code hands it a standard `random.Random()` instance while the test hands it a seeded one."

## Verdicts

Applied in commit 1cf4de05, after each item was tested against the chapter and run under `uv run` with `ty` 0.0.84.

1. Rejected. Both tests set `APP_DATA` to `str(tmp_path)`, an absolute path, so a `~` is a value the listing never receives; the sentence after the listing is a caveat about such a value, and the listing is not required to act on a case it does not run. (`Path("~/data").expanduser()` does expand it, as the sentence says.)
2. Rejected. A probe with `self.__pin` set inside `Vault` and two reads outside the class gave the opposite of the reviewer's account: `ty` reported `v._Vault__pin` as `unresolved-attribute` and accepted `v.__pin` with no diagnostic, although at runtime the first read succeeds and the second raises an `AttributeError`. A checker that modeled the rewriting and enforced privacy would flag the second read, so "does not model this rewriting" is the accurate description and the sentence stands.
3. Applied, with a different fix. "Fresh" could be read as a new generator on every call, which the sentence does not mean; "a standard instance" says less than the original. The sentence now says production hands `roll()` "a `random.Random()` seeded from the operating system, while the test hands it `Random(0)`", naming where an unseeded generator's seed comes from (the `random` docs: operating-system randomness when available) and the test's actual argument.
