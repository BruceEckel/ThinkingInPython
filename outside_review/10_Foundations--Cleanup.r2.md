<!-- outside review of Chapters/10_Foundations--Cleanup.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `10_Foundations--Cleanup.md` chapter:

**1. Section: Reference Cycles Delay Destruction (clarification of referrer inspection)**

* **Target Text:** "The only referrer is `node`, which confirms the self-reference."
* **Issue:** Inside `self_link()`, the instance is also referenced by the local variable `node` in the active execution frame. Claiming that `node` is the only referrer contradicts the program state and the very next paragraph, which notes that `self_link()` returns and only then does its local `node` disappear. The listing writes `gc.get_referrers(node)[0] is node` precisely because the referrer list contains more than just the self-reference.
* **Instruction:** Change the sentence to acknowledge the local variable reference: "The referrers include `node` itself, confirming the self-reference alongside the local variable in `self_link()`."

**2. Section: The Rule (technical accuracy regarding `io.IOBase` and `ResourceWarning`)**

* **Target Text:** "`io.IOBase` gives every file object a `__del__()` that closes it, and a file from `open()` or a `socket.socket` also reports a `ResourceWarning` there, catching a forgotten `close()` rather than replacing it:"
* **Issue:** `socket.socket` does not inherit from `io.IOBase`, nor does `io.IOBase.__del__()` emit `ResourceWarning` (it merely calls `self.close()`). The `ResourceWarning` demonstrated in `resource_warning.py` is emitted by concrete OS-backed streams (such as `_io.FileIO` and `_io.TextIOWrapper`) and by `socket.socket`'s own deallocator when unclosed instances are finalized.
* **Instruction:** Rephrase to decouple sockets from `io.IOBase` and specify where the warning originates: "`io.IOBase` gives file objects a `__del__()` that calls `close()`, and types wrapping OS resources—such as a file from `open()` or a `socket.socket`—also emit a `ResourceWarning` when reclaimed while still open, catching a forgotten `close()` rather than replacing it:"

**3. Section: Why `__del__()` Is Not Cleanup (stale documentation claim on shutdown order)**

* **Target Text:** "Python guarantees that globals whose name begins with a single underscore are deleted from their module before other globals are deleted; if no other references to such globals exist, this may help in assuring that imported modules are still available at the time when the `__del__()` method is called."
* **Issue:** This quotes an obsolete pre-Python 3.4 documentation passage. PEP 442 overhauled module finalization and interpreter shutdown, removing both the single-underscore deletion ordering guarantee and this statement from the official Python documentation. Quoting it as an active guarantee misleads readers targeting modern Python versions.
* **Instruction:** Delete this sentence from the block quote, ending the bullet point at `set to None.`.

**4. Section: An Explicit `close()` and a `with` Block (technical precision of context manager protocol)**

* **Target Text:** "The `with` protocol calls `close()` for you once."
* **Issue:** The `with` statement protocol invokes `__enter__()` and `__exit__()`, never `close()`. In `closable.py`, `close()` is called solely because the class author explicitly bridged them by calling `self.close()` inside `__exit__()`. Describing `close()` as being called by the protocol risks confusing readers coming from Java, where `try-with-resources` directly invokes `AutoCloseable.close()`.
* **Instruction:** Update the sentence to attribute the call to `__exit__()`: "The context manager's `__exit__()` calls `close()` for you once."

## Verdicts

Second run, on the Flash model. Applied in commit b7f23db4, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. A probe that called `gc.get_referrers(node)` inside the function after `node.me = node` returned a list of length 1 whose one element `is node`; a frame's fast locals are not objects the collector reports as referrers, so the local variable the reviewer names does not appear, and "The only referrer is `node`" is what the call shows. The same probe settled this item in the Pro round.
2. Applied, with a different fix. `socket.socket.__mro__` is `(socket.socket, _socket.socket, object)`, so no `io.IOBase` is involved, and a subclass of `io.IOBase` reclaimed without `close()` had `close()` called by `IOBase.__del__()` with no warning, while an unclosed `open()` file and an unclosed socket each produced `ResourceWarning: unclosed ...` from their own finalizers. The word "there", which tied both warnings to `IOBase.__del__()`, is now "when it is reclaimed still open"; the rest of the sentence, including `io.IOBase` closing every file object, stands.
3. Rejected. The block quote matches the current documentation: the 3.15 `object.__del__()` warning fetched on 2026-10-10 still reads "may already have been deleted or set to None. Python guarantees that globals whose name begins with a single underscore are deleted from their module before other globals are deleted ...". PEP 442 changed finalization order for cyclic garbage; it did not remove this sentence, so the chapter quotes a live warning.
4. Applied. `closable.py`'s `__exit__()` calls `self.close()`, and the paragraph two above already says "`__exit__()` calls `close()`", so "The `with` protocol calls `close()`" named the wrong actor. The sentence now reads "`__exit__()` calls `close()` for you once".
