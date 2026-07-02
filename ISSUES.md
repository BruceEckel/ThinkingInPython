<!-- loop progress: complete. Chapters 02-35 all reviewed; make verify passes. -->
<!-- A chapter with no heading below had only obvious issues, which were fixed directly in the Markdown. -->
# Issues

## Chapter 02: Tour

- [ ] "Indenting can nest to any level, just like curly braces in C++ or Java, but unlike those languages there is no option (and no argument) about where the braces are placed; the compiler forces everyone's code to be formatted the same way." The sentence talks about brace placement in a language with no braces, and calls Python's enforcement "the compiler." Suggested fix: "Indenting can nest to any level. Unlike the brace-placement debates of C++ or Java, there is no option about formatting. The language forces everyone's code to be indented the same way, which is one of the main reasons for Python's consistent readability."

## Chapter 03: Containers

- [ ] Opening line: "Both lists and associative arrays (dictionaries and sets) are fundamental data types." A set is not an associative array, and "Both" introduces three things. Suggested fix: "Lists, dictionaries, and sets are fundamental data types."
- [ ] "Lists and Iteration" opens with two near-duplicate sentences, each saying `for` "automatically" iterates. Suggested fix: merge into one: "The `for` statement iterates through a list directly rather than counting through a sequence of numbers."
- [ ] "There are no type declarations in this example; Python infers types from the way you use them." In dynamic typing the objects carry their types; nothing is inferred at this point (inference is a type-checker activity, covered in Static Typing). Suggested fix: "There are no type declarations in this example. Each object carries its own type."
- [ ] "A set ensures only one of each item is contained in the set." Circular wording (set ... in the set). Suggested fix: delete the sentence; the next one ("It is an unordered collection of unique items") already says it.

## Chapter 04: Control Flow

- [ ] The conditional expression (`"pass" if x >= 3 else "fail"`) appears in `chaining.py` with only a code comment, and is then used in `while_loop.py`, but the prose never introduces it. Suggested fix: add a sentence after the first example: "The example also shows a *conditional expression*: a one-line `if`/`else` that produces a value."
- [ ] The paragraph "With `print()`, the default `end` (printed after the value) is a newline. You can use `sep` to change the separator between values." sits after the walrus example, which uses neither. It explains `end=" "` from the earlier `break_continue.py`/`looping.py` examples. Suggested fix: move the paragraph directly after the `looping.py` example.

## Chapter 06: Modules and Packages

- [ ] "To make something a package, you put a special file named `__init__.py` in that directory." Since PEP 420, a directory without `__init__.py` is a namespace package, so imports work without the file. The chapter presents `__init__.py` as required. Suggested fix: keep the recommendation but acknowledge the exception, e.g. add: "A directory without `__init__.py` can still be imported as a *namespace package*, but an explicit `__init__.py` makes the package's identity and boundary clear, so this book always uses one."
- [ ] The `PYTHONPATH` section calls it "semi-deprecated" and says it "has been effectively superseded by the *virtual environment*." A virtual environment by itself does not make your own modules importable; installing the package into the environment does. Also, project memory says the book avoids virtual-environment/tooling explanations. Suggested fix: "`PYTHONPATH` still works, but the modern practice is to install your package into the environment you are working in, which puts it on the search path without any environment variable."

## Chapter 09: Class Attributes

- [ ] The chapter opens with "How class-level attributes behave surprises programmers coming from C++ or Java," and nine lines later repeats "This trips up programmers coming from C++ or Java." Suggested fix: reword the second occurrence to "In C++ or Java, storage for such a field is allocated per object before the constructor runs, which makes this behavior a surprise."

## Chapter 13: Pattern Matching

- [ ] "A `switch` cannot do this; neither can a chain of `if`/`isinstance()`." The second half is not accurate: type checkers narrow `isinstance()` chains, so an `if`/`elif` chain ending in `else: assert_never(shape)` gets the same exhaustiveness guarantee. Suggested fix: "A `switch` in other languages cannot do this. An `if`/`isinstance()` chain can, but only if you remember to end it with `assert_never()`; `match` makes the shape of the dispatch explicit."

## Chapter 17: Comprehensions

- [ ] The two paragraphs introducing the set comprehension say the same thing twice: "We are only interested in names longer than one character and wish to represent all names in the same format: the first letter should be capitalized..." followed immediately by "The following set comprehension normalizes each name (capital first letter, the rest lower case), keeps the names longer than one character...". Suggested fix: delete the first paragraph ("Consider a list of names... lower case.") and let the second carry the setup.

## Chapter 18: Metaprogramming

- [ ] `greenhouse.py` uses list comprehensions for side effects: `[create_mc(dsc) for dsc in descriptions]` and `[create_exec(dsc) for dsc in descriptions]` build throwaway lists of `None`. Suggested fix: replace both with plain `for` loops (`for dsc in descriptions: create_mc(dsc)`), which also matches the advice elsewhere in the book that a comprehension describes a result, not a procedure.

## Chapter 19: Performance

- Chapter is an unfinished draft: `[[...]]` author notes remain at the top and in the "Benchmark Alternatives with `timeit`", "Write Idiomatic Python", "Lazy Evaluation with Generators", "Caching", "Vectorize with NumPy", "JIT Compilation with Numba", "The GIL and Free Threading", and "Choosing a Strategy" sections, and "Converting a Slow Function to Rust" is an empty heading.
- [ ] "For a priority queue shared across threads, `queue.PriorityQueue` wraps `heapq` with locking, covered with concurrency below." Nothing below covers `PriorityQueue`. Suggested fix: drop "covered with concurrency below" (or cover it when the concurrency sections are finished).
- [ ] `bisect_search.py` (`def grade(score):`) and `slots.py` (`def __init__(self, x, y):`) are untyped, unlike the rest of the book's examples. Suggested fix: add type hints (`def grade(score: int) -> str:`, `def __init__(self, x: int, y: int) -> None:`).

## Chapter 20: Rethinking Objects

- [ ] "A getter that returns a mutable object hands the caller a reference to the real internals" appears verbatim twice: in the paragraph before `leaky.py` and again in the paragraph after it. Suggested fix: delete the repetition after the example, keeping "Encapsulation with private fields and getters still leaks. The output shows that the internals changed from outside."

## Chapter 21: The Pattern Concept

- [ ] The "Once and once only" bullet in Design Principles has two unrelated principles appended inside it: "*Make things as immutable as possible*... " and "*Make functions pure whenever you can*" (which also lacks a period). Suggested fix: split those two into their own bullets.
- [ ] Further Reading links to `http://www.catonmat.net/blog/learning-python-design-patterns-through-video-lectures/`, which is likely dead (old catonmat URL scheme, plain http). Suggested fix: verify and either update the URL or drop the entry.

## Chapter 23: Singleton

- [ ] Exercise 1 says "`singleton_pattern.py` always creates an object, even if it's never used. Modify it to use *lazy initialization*." That describes `singleton_eager.py`; `singleton_pattern.py` is already the lazy version (the chapter's "Lazy Creation" section). Suggested fix: "1. `singleton_eager.py` always creates its inner object, even if it is never used. Modify it to use *lazy initialization*, then compare your result with `singleton_pattern.py`."
- [ ] `class_variable_singleton.py` names its class `SingleTone`, which reads as a typo for `Singleton` (and its `#:` output does not display the name, so renaming is cheap). Suggested fix: rename the class (e.g. `SharedInstance` or `Singleton`) in the example and its test.

## Chapter 24: Template Method

- [ ] The first section heading "## Template Method" repeats the chapter title exactly, which reads oddly in the table of contents. Suggested fix: rename the section to something like "## The Fixed Algorithm".

## Chapter 25: Surrogate

- [ ] The *Remote proxy* item says "A remote proxy is created for you automatically by the RMI compiler `rmic` as it creates stubs and skeletons." This is a Java-era leftover: `rmic` is Java's (long-deprecated) RMI tool and means nothing in a Python context. Suggested fix: replace the sentence with a language-neutral note, e.g. "Distributed-object systems generate these for you; in Python, RPC libraries play this role."

## Chapter 26: State Machines

- [ ] `mousetrap2/mouse_trap2.py` (`StateT.next()`) raises a bare `Exception("Input not supported for current state")`. The table-driven engine later in the chapter raises `RuntimeError`. Suggested fix: raise `RuntimeError` here too, for consistency and to avoid a bare `Exception`.
- [ ] `StateT` uses the `transitions: dict[Any, Any] | None = None` plus `assert self.transitions is not None` pattern, which the book elsewhere avoids (replace Optional-plus-assert with a bare declaration or sentinel). The lazy initialization is the point of the example, but the base-class `next()` could use an empty-dict sentinel (`self.transitions: dict[Any, Any] = {}` and `if not self.transitions:` in subclasses works unchanged) and drop the `assert`. Suggested fix: switch to the empty-dict sentinel.

## Chapter 28: Factory

- [ ] The paragraph "The `@staticmethod` decorator marks a method that takes no `self` and so can be called on the class itself." sits stranded between two generator discussions, and `@staticmethod` was already introduced in Classes (chapter 07). Suggested fix: delete the paragraph.
- [ ] In `shapefact1/nested_shape_factory.py`, the function `shape_name_gen()` yields `Shape` objects (`Iterator[Shape]`), not names; the name was copied from `shape_factory1.py` where it yields strings. Suggested fix: rename it to `shape_gen()` in this example.

## Chapter 33: Visitor

- [ ] The flower class `Runuculus` is a misspelling of *Ranunculus*, carried through `flower_visitors.py`, `visitor_singledispatch.py`, `test_visitor.py`, and the `#:` output blocks. Suggested fix: rename to `Ranunculus` everywhere in the chapter and regenerate the output markers.
- [ ] Exercises 3 and 4 ask the reader to "replace the double dispatching with a table lookup," which is exactly what chapter 32 already presents as `paper_scissors_rock_table.py` (and the exercise even points at that file for the answer). Suggested fix: drop exercises 3 and 4, or reshape 3 around its one novel question ("Can you keep the syntactic simplicity of the dispatch while using a table underneath?").

## Chapter 35: Simulation

- [ ] "Other Maze Resources" links to `http://www.mazeworks.com/mazegen/mazegen.htm`, a site that has been offline for years. Suggested fix: drop it or replace with a live maze-generation reference (e.g. Jamis Buck's "Maze Generation" series or Wikipedia's maze-generation-algorithm article). The second link (`red3d.com/cwr/steer/`) still resolves.
