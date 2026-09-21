# Heading Proposals

Where a `###` heading would help a reader, from a full read of every
chapter on 2026-09-20 (nine Fable agents, report-only, no file edited).
144 proposals, 48 of them high confidence, plus level changes and lone
subheadings. Fourteen line numbers were spot-checked against the files
and all matched.

**How to mark it up.** Put an `x` in the box of each proposal to apply,
edit the heading text in place, and delete what you reject. Then ask
for the file to be applied.

**H** means the reviewer would add the heading without asking. **M**
means it helps, but you might prefer the unbroken flow. "Before" quotes
the first words of the line the heading goes above. "Reword" is the
new first sentence the heading needs, because the present one opens
with a pointer or connective that leans on the paragraph above.
Proposals marked "set" or "pair" stand or fall together, since one
alone would be a lone subheading.

**When applying.** Work bottom-up within a file so the line numbers
hold. Chapter 30 is mid-edit, so locate its spots by the quote. Many
proposals exist because inbound links land too high; after a heading
lands, retarget those links to the new anchor as a second step. Two
proposals in chapter 27 turn a "previous section" phrase stale. Run
`make verify` afterward for `heading_links`.

## The strongest cases

These rest on evidence outside the section itself.

- **07 Classes.** Chapters 09, 27, 32, and 37 link "MRO" to
  `#inheritance`, 80 lines above the passage. Chapters 18, 39, and 41
  link to `#properties` for `cached_property`, over 100 lines above it.
- **05 Functions.** Chapters 03, 09, and 12 link to
  `#default-arguments` for the mutable-default trap specifically.
- **13 Pattern Matching.** Chapters 20, 34, 37, and Solutions 33 link
  to a section under the words "expression problem". The term appears
  only in that section's last paragraph.
- **17 Metaprogramming.** Both inbound `@dataclass_transform` links
  (chapters 18 and 28) land four paragraphs above the passage.
- **28 Function Objects.** Chapters 17, 31, and 40 cite "the
  late-binding trap" through the `##` anchor.
- **15 Context Managers.** `expected` and `expect()`, which every later
  chapter imports, have no heading of their own.
- **32 Multiple Dispatching.** The chapter opening runs 915 words and
  five listings before the first `##`. Needs two `##` headings.
- **33 Visitor.** "The Pythonic Visitor" has no "The Classic Visitor"
  beside it, unlike chapters 30, 34, and 36.
- **46 Stateless.** "Dependency Injection" is the longest unbroken
  section in the book (833 words) and splits cleanly.
- **19 Concurrency.** Three sections each have a lone `###`, and
  "Are Threads Still Necessary?" sits under a `##` about something
  else.

## Chapters with nothing to add

01, 20 (one lone `####`, below), 22 (one `##` idea, below), 26 (one
level-change idea, below), 39, Appendix A, Appendix B.

---

## 02 Tour

- [ ] **M** L345 `### String Literals`, in "Strings"
  Before: "Single or double quotes create strings."
  The opening stretch is the only one of four sibling topics with no
  heading ("Common String Operations", "f-Strings", "t-Strings").

## 03 Containers

Set of four, in "Lists" (7 listings, no `###`). Only 1 and 4 have
inbound links; 2 and 3 keep the sorting and mixed-type passages from
landing under "Indexing and Slicing".

- [ ] **M** L37 `### Indexing and Slicing`
  Before: "A `list` holds objects, of any kind, in an ordered,"
  Chapter 02 links the word "Slicing" to `#lists`.
- [ ] **M** L61 `### Growing, Shrinking, and Sorting`
  Before: "Lists grow, shrink, and answer questions about themselves:"
- [ ] **M** L108 `### Mixed Element Types`
  Before: "Each slot of a `list` holds a reference to"
- [ ] **M** L131 `### Two List Traps`
  Before: "Two list operations produce surprises."
  Chapter 04 links here through `#lists`, and "Dictionaries" names
  `remove_while_iterating.py`.

Pair, in "Immutability" (426 words, 3 listings):

- [ ] **M** L765 `### `frozendict``
  Before: "A `MappingProxyType` is a window onto a `dict`"
- [ ] **M** L806 `### Shallow Immutability`
  Before: "Immutability is also shallow."
  Reword: "Immutability is shallow."
  Exercise 10 names it.

Level change (optional): `## Choosing a Container` above L836
("Choosing a container comes down to one question"). That paragraph
summarizes the chapter and sits at the end of "Immutability". It is
one paragraph.

## 04 Control Flow

Set of four, in "Loops" (694 words, 9 listings, no `###`):

- [ ] **H** L145 `### The Loop `else` Clause`
  Before: "A loop may have an `else` clause."
  The `break_continue.py` paragraph points ahead to it ("shows
  below"), and "Errors and Exceptions" points back.
- [ ] **H** L206 `### `range()`, `enumerate()`, and `zip()``
  Before: "`for` walks any iterable directly."
  Chapter 03 links to `#loops` for `zip()`.
- [ ] **H** L260 `### The Walrus Operator`
  Before: "The *walrus operator* `:=` assigns a value as"
- [ ] **H** L291 `### Mutating a Container While Looping`
  Before: "Changing a container while a `for` loop walks"
  Exercise 9 works from it.

Pair, in "Errors and Exceptions" (672 words, 4 listings):

- [ ] **H** L458 `### Exception Chaining`
  Before: "Raising an exception while handling another attaches the"
- [ ] **H** L534 `### Ask Forgiveness, Not Permission`
  Before: "Python's culture leans on "easier to ask forgiveness"

## 05 Functions

Pair, in "Default Arguments". The section is under 400 words; the
inbound links are the case.

- [ ] **M** L152 `### The Mutable Default Trap`
  Before: "Python evaluates a default value once, when it"
  Chapters 03, 09, and 12 link to `#default-arguments` for this.
- [ ] **M** L224 `### Safe Defaults`
  Before: "`good_append()` builds a fresh list on every call,"
  Reword: "`good_append()` builds a fresh list on every call, and any
  function that mutates a parameter with a default must do the same."

## 06 Modules and Packages

In "Packages" (739 words, 12 listings, one lone `###`):

- [ ] **M** L294 `### Nested Packages`
  Before: "You can put a second package underneath the"
- [ ] **M** L360 `### Circular Imports`
  Before: "Two modules in a package can end up"
  One 230-word paragraph. Split it at L374 ("A cycle is a design
  signal:") so the heading covers two.
- The lone "### Imports Within a Package" (L324) then covers relative
  imports only and could become "Relative Imports".

Set of three, in "Lazy Imports" (694 words, 4 listings):

- [ ] **M** L540 `### Deferring an Import Before 3.15`
  Before: "Before 3.15, deferring a costly import meant moving"
- [ ] **M** L555 `### Watching the Deferral`
  Before: "You can watch `lazy` defer the load by"
  Needs a paragraph break before L555.
- [ ] **M** L610 `### Limits of `lazy``
  Before: "`lazy` works with both `import` and `from ... import`,"
  Chapter 27 links here for the missing-registration failure.

Level change: the opening runs 645 words and 9 listings before the
first `##`, the longest unheaded run in the chapter.

- [ ] `## Importing Names with `from` and `as`` above L88 ("To bring a
  name into the current namespace, use the `from` keyword:")
- [ ] `## The Module Namespace` above L142 ("A module's namespace is an
  ordinary dict you can read and write.")

## 07 Classes

Pair, in "Inheritance":

- [ ] **H** L197 `### Method Resolution Order`
  Before: "`super()` and ordinary attribute lookup both follow one"
- [ ] **M** L229 `### Calling the Base Constructor`
  Before: "The base-class constructor runs because `Derived`'s
  constructor calls"
  Chapter 30 links `super().__init__()` here. The two paragraphs at
  L251-262 explain `demo_subclass.py` and fit better moved up to
  follow L195.

Pair, in "Properties":

- [ ] **M** L354 `### Adding a Setter`
  Before: "A `@property` with a getter alone rejects writes:"
- [ ] **H** L436 `### Caching with `cached_property` {#cached-property}`
  Before: "A `@property` reruns its code on every access."

## 08 Static Types

In "Generic Functions and Classes" (7 listings, 2 existing `###`):

- [ ] **M** L403 `### Type Parameters`
  Before: "Consider a function that returns the first element"
  The opening stretch is a sibling of "Variance" and "Type Parameter
  Defaults".
- [ ] **M** L591 `### `**P` and the Older `TypeVar` Syntax {#paramspec-and-typevar}`
  Before: "A special form, `**P`, captures the types of"
  Two two-sentence paragraphs now under "Type Parameter Defaults".
  The alternative: move both up to follow L472, no heading.

Style note: the eleven `###` headings under "Type Hint Summary" use
sentence case ("Basic types"). The rest of the book uses Title Case.
Pandoc slugs are lowercase, so recasing keeps every inbound anchor.

- [ ] Recase the eleven summary headings.

## 09 Class Attributes

In "Class Attributes Are Not Default Values" (682 words, 4 listings):

- [ ] **M** L41 `### Two Dictionaries, One Lookup`
  Before: "An instance and its class each have their own attribute
  dictionary."
  "Which Dictionary?" points back at this passage.
- [ ] **H** L98 `### The Bug Surfaces Far from Its Cause`
  Before: "A class attribute reads like a default right up until"
- [ ] **H** L129 `### A Shared Mutable Value`
  Before: "The shadowing rule confines a change to one object"
  Exercise 5 and the `default_factory` links build on it.

In "Declaring Shared State with ClassVar":

- [ ] **M** L290 `### A Base Class Declares, a Subclass Supplies`
  Before: "Declaring a `ClassVar` and leaving the value elsewhere is
  deliberate,"

Lone subheading: "### `type(self)` Forks the Counter" (L438). Its
natural sibling is the override passage at L433, which chapter 37
links to, but that is four sentences inside a paragraph. Either
expand it under "### An Override Drops the `ClassVar` Guard" or
accept the lone heading as a named trap.

## 10 Cleanup

In "Reliable Alternatives" (580 words, 5 listings). The section is a
two-item numbered list whose items run about 280 and 300 words, so the
numerals do a heading's job.

- [ ] **H** L215 `### An Explicit `close()` and a `with` Block`
  Before: "1. An explicit cleanup method such as the `close()`"
  Reword: "The first is an explicit cleanup method, such as the
  `close()` that file objects provide, which a `with` block calls."
- [ ] **M** L273 `### A Raising `__init__()` Leaks the Resource {#raising-init-leaks}`
  Before: "`Socket.__init__()` also prints "opened" before"
  Reword: drop "also".
- [ ] **H** L310 `### `weakref.finalize()` as a Backstop`
  Before: "2. `weakref.finalize()`,"
  Reword: "The second is `weakref.finalize()`, which registers a
  cleanup callback for an object without giving that callback a
  reference to the object:"
- [ ] **M** L358 `### The `self.close` Trap` (only with the next one)
  Before: "The `self.close` mistake produces no error, only an object"
  Reword: "Passing `self.close` to `finalize()` produces no error,
  only an object that never goes away:"
- [ ] **M** L395 `### A Slotted Class Needs `__weakref__` {#slotted-class-needs-weakref}`
  Before: "`finalize()` needs a target that supports weak references,"

## 11 Testing

- [ ] **H** L786 `### Stubs and Mocks`, in "Isolating Tests from the
  World"
  Before: "A stand-in like `fake_urlopen()` is a *stub*:"
  "Network Calls" turns here to `unittest.mock`, and a reader looking
  for mocks finds no heading.

## 12 Data Classes as Types

Pair, in "A Type Is a Set of Values" (eight inbound links):

- [ ] **M** L617 `### Normalizing a Frozen Field`
  Before: "`__post_init__()` can check a field but cannot change one."
- [ ] **M** L660 `### Parse, Don't Validate`
  Before: "Validating once, at construction, often goes by the name"
  Solutions 35 cites it by name.

Pair, in "The General Form of `replace()`":

- [ ] **M** L1346 `### `copy()` and `deepcopy()` Skip the Constructor {#copy-skips-the-constructor}`
  Before: "The `copy` module's other two functions copy without calling"
  Reword: "`copy.copy()` and `copy.deepcopy()` copy without calling
  the constructor."
  Chapter 27 links here for exactly this.
- [ ] **M** L1385 `### Defining `__replace__()` {#defining-replace}`
  Before: "`__replace__()` is a dunder like any other,"

Level changes:

- [ ] New `##` at L1203 ("Two data classes in one hierarchy must agree
  about `frozen`."), for example "## Frozen and Plain Data Classes Do
  Not Mix". It sits in "Inheritance and the Generated `__init__`" and
  is not about the generated `__init__`.
- [ ] Optional: `## `check()` and `TypeFailure`` at L18. Low priority.

## 13 Pattern Matching

Pair, in "Class Patterns" (5 listings; chapter 42 and Appendix B link
here):

- [ ] **H** L297 `### Keyword Patterns`
  Before: "Keyword patterns work differently."
  Reword: "A keyword pattern such as `Point(x=0, y=y)` matches by
  attribute name, through attribute access, not through
  `__match_args__`." (absorbs L297-299)
- [ ] **H** L335 `### Builtin Types and Subclasses`
  Before: "The type test is `isinstance()`, so a subclass matches"

Set of three, in "Dynamic Binding vs. Pattern Matching":

- [ ] **M** L713 `### The Inheritance Version`
  Before: "The inheritance answer declares both operations as abstract"
- [ ] **M** L786 `### The `match` Version`
  Before: "A type union with `match` takes the opposite shape."
  Reword: add "from the class hierarchy".
- [ ] **H** L866 `### The Expression Problem`
  Before: "Try growing the system in each direction."

Level change (medium): `## A Bare Name Captures, a Dotted Name
Compares` at L97 ("A bare name always binds."). "Alternatives and
Capture" holds two subjects, and L373 and exercise 6 refer back to
the value-pattern trap.

## 14 Decorators

Pair, in "Maintaining the Wrapped Interface" (six inbound links, five
for `**P`, one for `wraps`):

- [ ] **M** L166 `### `wraps` Keeps the Runtime Interface`
  Before: "`functools.wraps` copies the original function's metadata"
- [ ] **M** L175 `### `**P` and `R` Keep the Static Interface {#p-and-r-keep-the-static-interface}`
  Before: "`wraps` keeps the runtime interface."
  Smoother: "`wraps` keeps the runtime interface, and the type
  parameters keep the static one."

Level change (medium to high): the opening runs 480 words and three
listings before the first `##`.

- [ ] `## What `@` Does {#what-at-does}` at L15 ("To apply a
  decorator,"). Pairs with the later "What `@` Does Not Require".

## 15 Context Managers

Pair, in "The `__exit__()` Arguments" (837 words, 6 listings):

- [ ] **H** L360 `### The `expected` Manager`
  Before: "A fuller version of the same idea takes several"
  Reword: "`expected` is a fuller version of `expected_one`: it takes
  several types at once, and with no argument it catches everything."
- [ ] **H** L483 `### The `expect()` Function`
  Before: "Many listings in this book call something to show"

Set of three, in "An Object Pool" (654 words, 4 listings):

- [ ] **M** L925 `### An Empty Pool Blocks the Caller`
  Before: "The queue does more than store the idle items."
  The *Flyweight* paragraph at L982 would fit poorly under it; move it
  up to follow L923.
- [ ] **H** L989 `### Testing the Lease`
  Before: "Three tests pin down what the lease guarantees:"
- [ ] **M** L1020 `### What the Skeleton Leaves Out`
  Before: "A production pool adds refinements to this skeleton,"
  Reword: "...refinements to the `Pool` skeleton,"

## 16 Comprehensions

Pair, in "List Comprehensions" (7 listings):

- [ ] **M** L55 `### The `map()` and `filter()` Equivalent`
  Before: "The built-in functions `map()` and `filter()` with a"
  Reword: "The built-in functions `map()` and `filter()`, each given
  a `lambda`, produce the same list that `list_comprehension.py`
  builds."
- [ ] **H** L113 `### Scope and the Walrus Operator`
  Before: "A comprehension has a scope of its own:"

Pair, in "Generator Expressions":

- [ ] **M** L602 `### A Generator Expression Runs Once`
  Before: "`genexp_consumers.py` iterates `nums` three times because"
- [ ] **H** L624 `### The Gap Between Creation and Consumption`
  Before: "A generator expression defers everything but one thing."
  L403 promises "[Generator Expressions] returns to that gap". The
  link could land here.

## 17 Metaprogramming

Pair, in "Generating Classes with `type`" (725 words, 5 listings):

- [ ] **H** L169 `### A Family of Generated Classes`
  Before: "Generating classes programmatically with `type` pays off"
- [ ] **H** L236 `### Building Each Class on First Lookup`
  Before: "The dict comprehension builds all seven classes whether"
  Reword: "The dict comprehension in `eager_event_classes.py` builds
  all seven classes whether the schedule uses them or not."

Pair, in "Generating Classes with `exec()`":

- [ ] **M** L450 `### The Injection Risk`
  Before: "That string is also the danger."
  Reword: "The `klass` string is the danger in this approach."
  Exercise 9 sends the reader back here.
- [ ] **M** L464 `### Generated Classes Cannot Be Pickled`
  Before: "Both generators carry a second cost, unrelated to injection."
  Reword: "Both generators, `type()` and `exec()`, have a second
  limitation, unrelated to injection."

Pair, in "Where Enforcement Lives":

- [ ] **M** L679 `### The Four Families`
  Before: "`@final` and `@override` are *markers*."
- [ ] **H** L709 `### `@dataclass_transform` Is a Claim {#dataclass-transform}`
  Before: "How does the checker know what `@dataclass` does?"
  Alternative: make L709-776 its own `##`.

Siblings for lone subheadings:

- [ ] **H** L821 `### A Descriptor That Learns Its Name`
  Before: "A class attribute learning its own name is another"
  Sibling of "A Descriptor That Validates".
- [ ] **M** L1449 `### The Core Functions`
  Before: "`inspect` works on any live object: modules, classes,"
  Sibling of "Sorting Members into Attributes and Methods".

Level changes:

- [ ] Promote "### Multiple Inheritance and Metaclasses" (L1212) to
  `##`. About 480 words, 3 listings, and its subject is not instance
  creation. Both links still resolve. If it stays a `###`, add
  "### A Singleton from `__call__()`" before L1128.
- Chapter 14 links to `#learning-a-name-with-__set_name__` twice under
  the words "the descriptor protocol". A section title that names
  descriptors would match.

## 18 Performance

Pair, in "Profilers":

- [ ] **M** L220 `### Reading a `cProfile` Report`
  Before: "The report is a table, one row per function."
  Reword: "`cProfile`'s report is a table, one row per function."
- [ ] **M** L264 `### The Sampling Profiler`
  Before: "Python 3.15 gathers the profilers into a single `profiling`"

Others:

- [ ] **M** L461 `### Trusting a Measurement`
  Before: "A single measurement includes whatever else the machine is"
  Sibling for the lone "Numbers on Your Machine". Unnecessary if that
  heading is promoted (below).
- [ ] **M** L811 `### Heap Versus Sort`
  Before: "A heap answers a different question than a hash-based"
  "Bisect" has "Comparison" after it; the heap's comparison is
  unmarked. The immutable-containers note at L873 reads better in the
  section opening (L616-621).

Level change:

- [ ] Promote "### Numbers on Your Machine" (L483) to `##`. `report()`
  and `--numbers` serve every measured listing, and four links target
  it by name.

## 19 Concurrency

- [ ] **H** L389 `### Failures as Values with `gather()``
  Before: "When one task's failure should not stop the others,"
  Sibling for the lone "Bounding a Wait". Move the two-sentence
  `tg.cancel()` paragraph (L448) above L389.
- [ ] **H** L574 `### `time.sleep()` Stops the Loop`
  Before: "`asyncio.sleep()` in `io_price` is not `time.sleep()`."
  Four later passages, exercise 4, and a Guidelines bullet point back
  to `blocking_the_loop.py`. Sibling for the lone "A Real Socket".
- [ ] **M** L1006 `### What a Process Pool Requires`
  Before: "Three issues separate a process pool from the in-process"
  Reword: end with "and all three surface in `parallel_cpu.py`:"
  L1627 cites "[Parallelism]'s third point"; chapters 22 and 43 link
  here for pickling.
- [ ] **H** L1038 `### Raw `multiprocessing``
  Before: "The `multiprocessing` module underneath
  `ProcessPoolExecutor`"
- [ ] **H** L1096 `### Measuring the Speedup`
  Before: "You can test the claim that wall-clock time falls toward"
  Direct sibling of the lone "Why Speedup Isn't Linear".
- [ ] **M** L1215 `### Threads Overlap Waits, Not Computing`
  Before: "However, a thread waiting on I/O releases the GIL."
  Reword: drop "However,".
- [ ] **M** L1881 `### One `Executor` Interface, Three Pools`
  Before: "The first is `concurrent.futures.Executor`."
  Reword: "The first point of convergence is
  `concurrent.futures.Executor`."
- [ ] **M** L1942 `### One `await`, Any Backend`
  Before: "The second point of convergence is `await`."

Level change:

- [ ] Promote "### Are Threads Still Necessary?" (L2019) to `##`. With
  "Measuring the Difference" it runs 740 words on threads against
  tasks, not on the `Executor`/`await` convergence its parent names.
  No link targets either anchor. Under the new `##`: rename L2071 to
  "### Measuring the Memory", and add "### Measuring the Time" at
  L2153, first sentence "A thread also takes longer to create than
  a task:".

## 20 Rethinking Objects

Lone `####`: "What the Shape Does Not Say" (L875) under
"### Protocols" (615 words, 5 listings).

- [ ] **M** L806 `#### One Class, Many Protocols`
  Before: "Because membership is structural,"
  Reword: "Because protocol membership is structural, one class can
  satisfy any number of protocols at once,"

## 21 Design Patterns

In "What Is a Pattern?" (698 words, no `###`):

- [ ] **M** L50 `### What an Abstraction Erases` (optional)
  Before: "Isolation has a price."
  Reword: "Isolating what changes discards information."
- [ ] **H** L68 `### The Vector of Change`
  Before: "Often, the most difficult part of developing an elegant"
  Chapter 37 L622 links "*vector of change*" to the `##`.
- [ ] **H** L81 `### Patterns You Have Already Seen`
  Before: "Design patterns isolate changes in your code."
  Needed if the one above lands.

## 22 Data Transfer Objects

- [ ] **M** `## A Hand-Rolled Messenger` at L20 ("A Messenger is an
  object with attributes corresponding to"). The opening runs 420
  words with a listing, and L92 and L314 call it "the hand-rolled"
  version.

## 23 Iterators

Set of three, in "The Costs of Laziness" (543 words, 4 listings):

- [ ] **M** L240 `### The Body Waits for the First `next()``
  Before: "Calling `squares(6)` runs none of its body."
- [ ] **M** L272 `### An Exhausted Generator Is Silently Empty`
  Before: "The second surprise is the second call to `list(sq)`."
  Reword: "The second surprise in `generator_lifecycle.py` is its
  second call to `list(sq)`."
- [ ] **H** L322 `### What `tee()` Buffers`
  Before: "`itertools.tee(it, 2)` splits one iterator into two"
  Chapter 41, L780, L828, and exercise 5 all point back here.

Pair, in "The Pattern That Disappeared":

- [ ] **M** L698 `### `first()` and `current_item()` Rebuild the List`
  Before: "Written in Python, the four GoF *Iterator* methods show"
- [ ] **M** L786 `### Asking Consumes an Item`
  Before: "You can ask a GoF iterator repeatedly whether it has"

## 24 Singleton

In "When You Want a Class, Cache the Instance"; "Tests, Threads, and
Locks" runs 678 words and 3 listings:

- [ ] **M** L218 `### The First-Call Race`
  Before: "The race is easy to see with a wide enough window:"
  Reword: "The first-call race is easy to see..."
  Chapter 35 cites it twice.
- [ ] **M** L308 `### Double-Checked Locking and Eager Creation`
  Before: "Every call now acquires the lock,"
  Reword: "Every call to the locked `settings()` acquires the lock,"
  The Pattern Catalog's *Double-Checked Locking* row means this
  passage.

## 25 Template Method (hand-edited, higher bar)

- [ ] **M** L75 `### Hooks and the Misspelled Override`
  Before: "The step methods default to `...`,"
  590 words and 3 listings sit before the first `###`. The
  `test_template_method.py` passage (L192) would fall under it.

## 26 Surrogate (hand-edited, higher bar)

No `###` proposals.

- [ ] (medium) Promote "### What Proxy Solves" (L469, 529 words, 4
  listings) to `##`, then add "### Virtual Proxy" (L494),
  "### Protection Proxy" (L526), "### Smart Reference" (L573). The
  anchor Solutions 29 uses is unchanged. It would break the chapter's
  Proxy / State / One Surrogate triad of `##` headings.

## 27 Factory (hand-edited, higher bar)

- [ ] **M** L189 `### Hiding the Concrete Classes`
  Before: "The concrete shapes carry a leading underscore because"
  Sibling for the lone "Alternative Constructors Are Factories".
  Alternative: promote that heading to `##`.
- [ ] **M** L382 `### Hazards of Self Registration`
  Before: "`__init_subclass__()` runs as the subclass's `class`
  statement executes."
  The "previous section" at L501 must then name Self Registration.
- [ ] **M** L418 `### Testing the Registry`
  Before: "Testing confirms that every subclass registers itself,"
  The "previous section" at L507 then needs a named link too.

## 28 Function Objects (hand-edited, higher bar)

Set of three, in "Command: Choosing the Operation at Runtime":

- [ ] **M** L108 `### A Bound Method as a Command`
  Before: "Halfway between the function form and the class form,"
- [ ] **M** L146 `### A Callable Object as a Command`
  Before: "An object can be callable too."
  Reword: "An object can be callable."
- [ ] **H** L189 `### The Late-Binding Trap`
  Before: "Building commands in a loop can produce Python's
  best-known"

Level change (medium):

- [ ] New `##` at L672 ("In `event_bus.py`, the events are records,
  the handlers are functions,"), for example "## A Tagged Bus:
  Handlers That Name Their Event". "An Event Bus" runs 751 words and
  a second example starts over there.

## 29 Changing the Interface (hand-edited, higher bar)

In "Adapter" (881 words, one lone `###`):

- [ ] **M** L72 `### Three Places for the Adaptation`
  Before: "The adaptation can live in two other places:"
- [ ] **H** L128 `### What an Override May Change`
  Before: "The `/` in `WhatIUse.op()` makes its parameter
  positional-only."
  270 words on override typing rules, with the quoted `ty`
  diagnostic. This one alone cures the lone subheading.

## 30 Observer (being edited; locate by quote)

- [ ] **H** ~L856 `### The Model`
  Before: "The model reuses `broadcaster.Broadcaster`:"
  "Testing the Model" and "The View" are already headings; the
  470-word stretch that presents `box_observer.py` is their sibling.
- [ ] **M** ~L94 `### Push or Pull`
  Before: "Passing `arg` is the *push* model."
  Sibling for the lone "Why `notify()` Copies the List". Exercise 2
  names the pull model. The section is 421 words, so removing the
  lone heading also works; nothing links to it.

## 31 State Machines

"A Vending Machine" runs 790 words over three listings:

- [ ] **H** L739 `### Testing the Vending Machine`
  Before: "Because the machine is deterministic,"
- [ ] **M** L804 `### A View for the Vending Machine`
  Before: "Because the actions set `vm.message` instead of printing,"

## 32 Multiple Dispatching

Level change first (high). The opening runs L3-277, 915 words and 5
listings, with both complete versions of the example:

- [ ] `## Two Dispatches Through Methods` at L84 ("Here is *Multiple
  Dispatching* in action:")
- [ ] `## One Lookup in a Table` at L187. Reword: "In
  `paper_scissors_rock.py`, each `Item` type encodes the answers for
  its own combinations."

The wording follows the closing section. Chapter 33 L169, chapter 41
L330, and chapter 39 L230 would gain precise targets.

Set of three, in "One Type or Many" (548 words, 3 listings):

- [ ] **M** L295 `### `match` with Class Patterns`
  Before: "A `match` statement with class patterns is a third"
- [ ] **H** L326 `### The `singledispatchmethod` Trap`
  Before: "`functools.singledispatchmethod`"
- [ ] **M** L374 `### Methods or Table`
  Before: "The version most programmers write first is neither of"
  Reword: "...is neither the methods nor the table:"

## 33 Visitor

Level change (high):

- [ ] `## The Classic Visitor` at L13. Reword: "*Visitor*, the final
  pattern in *GoF Design Patterns*, solves the problem of a hierarchy
  you cannot change."

Pair, in "The Pythonic Visitor: singledispatch" (652 words):

- [ ] **M** L298 `### Testing the Operations`
  Before: "Because each operation is a plain function, testing is"
- [ ] **M** L345 `### Where Visitor Still Fits`
  Before: "*Visitor* still has a place:"

## 34 Composite and Interpreter

Pair, in "Interpreter" (816 words, 1 listing):

- [ ] **M** L294 `### The Nodes and the `Operators` Base`
  Before: "The four node classes are the grammar."
- [ ] **M** L312 `### Operators That Build Nodes`
  Before: "Every node inherits `__add__()` and `__mul__()`,"

## 35 Flyweight

- [ ] **H** L201 `### Freezing the Shared Tile`
  Before: "Freezing `Tile` hides the sharing from clients."
  The lone "Typing the Symbol Set" now covers three paragraphs on
  immutability. Chapter 08 links to it, so it cannot be removed.

## 36 Memento

Pair, in "The Classic Memento":

- [ ] **M** L132 `### Why `Memento` Is a Class`
  Before: "You could skip the class and write"
- [ ] **M** L198 `### Testing the Sketch`
  Sits directly on the `test_sketch.py` fence. Add a lead-in such as
  "Three tests pin down the copying:".

Set of three, in "Mementos That Outlive the Process" (698 words, 5
listings):

- [ ] **H** L595 `### A Class That Changes After the Save`
  Before: "Pickle's other limitation is time:"
  Reword: "The class can change between the save and the load."
- [ ] **H** L668 `### A Deleted Field Leaves a Ghost`
  Before: "Drift in the other direction is quieter still."
  Reword: "Deleting a field is quieter than adding one."
- [ ] **M** L706 `### Schema Migrations and Safer Formats`
  Before: "Databases hit the same problem and gave it a name."
  Reword: "Databases hit the same drift and gave its remedy a name."

## 37 Pattern Refactoring

Pair, in "Simulating a Trash Recycler":

- [ ] **M** L31 `### The `Trash` Hierarchy`
  Before: "In the `Trash` hierarchy, each material carries a"
- [ ] **M** L136 `### The Data File and Its Parser`
  Before: "A data file describes the trash to process,"

Pair, in "Adding Operations: Visitor, and Why Python Skips It":

- [ ] **M** L428 `### A Method on Every Material`
  Before: "Here is the requirement that makes the second axis"
- [ ] **M** L509 `### One `singledispatch` Function per Operation`
  Before: "[*Visitor*](33_Patterns--Visitor.md) is the classic escape,"
  Reword: "...is the classic way to add an operation without editing
  the classes, and it is elaborate:"
  Chapters 28 and 33 link to the section for this part.

## 38 Simulation

- [ ] **H** L1037 `### Watching the Robot`
  Before: "That same model drives a graphical view."
  Reword: "The same model drives a graphical view."
  The other two simulations each have "Testing ..." then
  "Watching ...".
- [ ] **M** L257 `### Running the Maze`
  Before: "The maze layout lives in a text file."

## 40 Functional Foundations

Pair, in "Immutability" (581 words, 3 listings):

- [ ] **M** L166 `### Immutability in Annotations`
  Before: "Type annotations can state immutability so a type checker"
- [ ] **M** L206 `### A Stable Hash and Safe Sharing`
  Before: "Immutability also offers two things a mutable value
  cannot."
  Reword: drop "also".

Lone subheading: "### Leaving a Gap with `Placeholder`" (L536). Keep
it. Chapters 28 and 41 link to its anchor, and no sibling exists.

## 41 Functional Toolkits

Pair, in "Case Study: Pairing Rotations" (709 words):

- [ ] **M** L897 `### Groups of Any Size`
  Before: "The trick stops working the moment the groups"
  Reword: "Rotation stops working the moment the groups are threes,
  fours, or any size but two."
- [ ] **M** L1010 `### `history` Is Mutable State`
  Before: "`met()` runs once per candidate per slot,"

## 42 Functional Error Handling

Pair, in "A Result Type" (580 words, 4 listings):

- [ ] **M** L180 `### Reaching the Answer`
  Before: "`Result[int, str]` says this function returns an `int`"
  Reword: "`func_a()`'s return type, `Result[int, str]`, says it
  returns an `int` on success or a `str` on failure."
- [ ] **M** L222 `### Total Functions`
  Before: "A function like this is a *Total Function*,"
  Reword: "A function like `func_a()` is a *Total Function*,"
  Chapter 44 uses the term and can only link to the whole chapter.

## 43 Functional Confidence

In "Property-Based Testing" (628 words, 3 listings):

- [ ] **M** L310 `### The Same Law in Hypothesis`
  Before: "Hypothesis turns the hand-written loop into a declaration."
- [ ] **M** L346 `### Shrinking a Failure`
  Before: "The two listings above both pass, so nothing"
- [ ] **M** L394 `### A Family of Property Shapes`
  Before: "The *roundtrip* law is one member of a small"
  One 130-word paragraph. Works only if it splits at "The trap to
  avoid". Exercise 3 points back to "the family above".

## 44 Effect Management

- [ ] **H** L266 `### Combine the First and Third`
  Before: "All three approaches take the division failure out of
  `slope()`,"
  The comparison now sits under "Make the Bad Value Impossible",
  which names only the third approach.
- [ ] **H** L436 `### What a Full EMS Does`
  Before: "An Effect Management System (EMS) keeps track of Effects"
  The 638-word opening is its own topic. L1047, 46:944, and L841
  link to the `##` for the three-item list, 40 lines below.

Lone subheading:

- [ ] Remove "### Subdividing the Impure Portion" (L381). The section
  is 202 words, the sentence under it leans on the paragraph above,
  and nothing links to it.

## 45 Generators

- [ ] **M** L552 `### `throw()` and `close()` Reach the Innermost Generator`
  Before: "A driver can also `throw()` an exception into a generator"
  Reword: "A driver can `throw()` an exception into a generator or
  `close()` it, and `yield from` relays both:"
  Two edits go with it. L552 is mid-paragraph, so it needs a
  paragraph break. The two closing paragraphs at L623-632 must move
  up to follow L551.

## 46 Stateless

Set of three, in "Supplying an Interface" (660 words; eight inbound
links for three different reasons):

- [ ] **M** L882 `### What the Type Checker Reads`
  Before: "First, the static issue."
  Reword: delete that sentence; open with "`supply()` reads the
  Ability from the declared type of its argument,"
- [ ] **M** L900 `### What `isinstance()` Checks`
  Before: "Second, the runtime issue, which the library decides using"
  Reword: "The library decides the runtime question with
  `isinstance()`."
- [ ] **M** L916 `### An Interface Instead of a Base Class`
  Before: "Stateless's own `Console` pays that cost."
  Reword: "Stateless's own `Console` can only be replaced by a
  subclass."

Pair, in "Dependency Injection" (833 words, no `###`):

- [ ] **H** L1151 `### No Container, Three Consequences`
  Before: "Stateless has no container."
- [ ] **H** L1176 `### Churn in Every Signature`
  Before: "The requirement that callers inherit is also the cost."
  Reword: "A requirement that every caller inherits is also a
  drawback."

Pair, in "Waiting on a Coroutine" (479 words, 5 listings):

- [ ] **M** L1237 `### `sleep()` Carries Two Abilities`
  Before: "You need `wait()` at the boundary where a coroutine"
- [ ] **M** L1302 `### A Clock That Never Waits`
  Before: "Reading a clock is a [side cause]"

In "The Error Channel":

- [ ] **H** L1524 `### Catching Is Not Handling`
  Before: "Because the driver throws the failure back in,"
  Reword: "The driver throws a failure back into the generator, so an
  ordinary `try`/`except` around a `yield from` catches it,"
  Matches its sibling "Declaring Is Not Handling".

Level change and lone subheadings:

- [ ] Promote "### Multiple Errors" (L1685) to `##`. It is the only
  `###` in its section, starts a new example, and nothing links to it.
- [ ] Remove "### A Default Binding" (L403), the only `###` under
  "Layering Handlers" (282 words). Nothing links to it.

## 47 Stateless in Practice

In "Scripting an Unpredictable Source"; "A Clock" runs 694 words and
four listings:

- [ ] **H** L356 `### A Clock That Crosses Midnight`
  Before: "Skipping the wait is the obvious benefit."
  Reword: "Skipping the wait is the obvious benefit of a handled
  clock."
  Exercise 1 refers back to `midnight.py` by name.
- [ ] **M** L412 `### A Source Named in the Type`
  Before: "Compare this to `student_pairs.py` in [Functional Toolkits]"
  Reword: "Compare these handlers to ..."
  The last two paragraphs wrap up the whole `##` but sit inside the
  clock subsection.

Pair, in "Supplying a Whole Cast":

- [ ] **M** L1479 `### The Unmatched Cast`
  Before: "The third mixes the casts, and nothing objects."
  Reword: "The third run mixes the casts, and nothing objects."
  Move the fourth-run paragraph (L1493) up to follow L1477.
- [ ] **M** L1500 `### The Nine-Argument Ceiling`
  Before: "The cast has a ceiling on how wide it can get."

In "Adding Behavior to an Existing Effect":

- [ ] **H** L1524 `### `retry()` and a Flaky Database`
  Before: "`Database` fails a fixed number of times before working,"
  The Pattern Catalog's *Retry* link would gain a landing place.
- [ ] **M** L1599 `### What Retry Cannot Judge`
  Before: "Read the trace before you use this on real code."
  Reword: "Read the trace before you use `retry()` on real code."
  Parallels "What Retry Costs the Signature".

Level change (medium):

- [ ] `## `run()` Builds a Loop per Call` after the tables in "The Toolkit", over
  L1892-1944 (`run_cost.py` and its measurement). First sentence:
  "The rule about where to call `run()` and `run_async()` has a
  reason." Leaving it also works.
