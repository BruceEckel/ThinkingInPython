# Generating an Index: the Possibilities

A survey, written 2026-09-18.
Nothing here is built.
The one thing tested is the Typst page-number lookup described under
[PDF](#pdf), because every PDF option depends on it.

## What an index must fit into

The book has one source and three outputs,
and each output has a different kind of locator.

| Output | Built by | What a locator can be |
|---|---|---|
| Site | `build_site.py`, one page per chapter | a link to `chapter.html#anchor` |
| EPUB | `build_epub.py`, one merged document | an in-document link, `#ch12-immutability`; a reflowable book has no page numbers |
| PDF | `build_pdf.py`, pandoc to Typst | a page number, which can also be a link |

Three facts about the build narrow the choices:

- **The PDF engine is Typst, not LaTeX.**
  `\index{}` and `makeindex` do not apply.
  Typst can report the page of any label, which is enough (see [PDF](#pdf)).
- **The EPUB and PDF share one assembly,** `build_epub.book_markdown()`.
  It merges the chapters and gives every heading a chapter-namespaced id.
  An index chapter, and any markers an index needs,
  can be added there at build time without touching `Chapters/`.
- **The site has full-text search** over 638 sections (`search_index.py`).
  Search answers "where does `__init_subclass__()` appear".
  An index earns its place with what search cannot do:
  a concept the text names in other words ("mutable default argument"),
  a *see also* from one term to a related one,
  a list a reader can browse,
  and a printed PDF.

The size of the job, measured today:

| | Count |
|---|---|
| Chapters | 47 |
| Prose words | about 171,000 |
| H2 and H3 sections | 593 |
| Extractable listings | 793 |
| Italic spans | 895, of which 419 distinct |
| Inline code spans | 12,416, of which 4,427 distinct |
| Code spans used in three or more chapters | 309 |
| Distinct PEPs cited | 17 |
| Pattern names in `pattern_names.txt` found in italics | 29 |
| PDF pages (the 2026-09-16 build) | 789 |

A professional indexer produces three to five entries per page.
At 789 pages that is 2,400 to 4,000 locators,
so whatever is chosen must be mostly mechanical,
with your judgment spent on the entry list and not on each locator.

## Decision 1: where the entries come from

### A. Markers in the chapter source

You tag each indexable spot in the Markdown.
In pandoc's syntax that is an empty span, `[]{.ix term="closure"}`.
In Leanpub's it is `{i: "closure"}` (see [Leanpub](#leanpub)).

- **For:** the most precise locators, and the author decides every one.
  This is how LaTeX and Leanpub books are indexed.
- **Against:** thousands of tags in prose you edit by hand.
  `Chapters/` has no attribute spans and no fenced divs today,
  so every tool that reads prose would need to learn to skip them:
  `reflow_prose.py`, `banned_phrases.py`, Vale, `heading_links.py`,
  `search_index.py`, and the rewrite passes.
  A tag also moves or dies silently when a sentence is rewritten,
  and the book's prose is still being rewritten.

### B. A term file and a matcher

The index lives in one data file, for example `tools/data/index_terms.yaml`.
Each entry has a heading, the patterns that count as a mention,
optional subentries, and *see* and *see also* targets.
A tool scans the chapters and computes the locators on every build.
[[Can we use toml rather than yaml?]]

```yaml
- term: closure
  match: [closure, closures, "enclosing scope"]
  see_also: [nonlocal]
- term: "mutable default argument"
  match: ["mutable default", "default_factory"]
- term: "__init_subclass__()"
  under: "special methods"
```

- **For:** `Chapters/` stays as it is.
  Locators follow the text through every edit, split, and renumbering.
  The file is small enough to review in one sitting,
  and a gate can check it (see [Gates](#gates)).
- **Against:** a matcher finds mentions, and a mention is not always a discussion.
  The locator rules in Decision 2 reduce that noise;
  they do not remove it.
  A passage that discusses a concept without using any of its words
  needs a manual locator in the file.

### C. Harvest from conventions the book follows

Several indexes fall out of rules the gates enforce today,
with no term list to write:

- **Definitions.**
  Your style rule is "italics only to introduce new elements",
  so an italic span is a defining occurrence.
  After the 29 pattern names are set aside,
  about 390 distinct italic terms remain: *closure*, *invariant*, *covariant*.
  This is the nearest thing to a free general index.
  A few spans are emphasis ("*is*" appears four times) and need a stop list.
- **Pattern names.**
  Every mention is italic and capitalized, and `pattern_names.txt` lists them,
  so each pattern's entry is its own chapter plus every other section that names it.
- **Listings.**
  `listing_links.listing_index()` maps all 793 listing names to their place.
  An index of listings is a sort and a render.
- **Python names.**
  Code spans give modules, functions, decorators, special methods,
  exceptions, and keywords.
  The 4,427 distinct spans are far too many,
  so this needs a filter: a name used in three or more chapters (309 today),
  or a name that appears in a heading,
  or a name matched against the standard library and `builtins`.
  Example-local names such as `greet()` and `Shape` drop out under that last test.
- **PEPs.**
  `PEP \d+` finds all 17.
- **`ty` diagnostic codes,** from the 40 quoted diagnostics.

The trade:

- **For:** a day or two of tooling and none of your time.
  These are also the lookups a programming reader makes most often.
- **Against:** it indexes what the text says verbatim.
  It finds no synonyms, no concepts, and no cross-references,
  which are what separate an index from search.

### D. An agent drafts the entries, chapter by chapter

One agent per chapter reads it as an indexer would and proposes entries:
concepts under the names a reader would look up,
subentries ("data class: frozen", "data class: slots"),
and *see also* links.
The proposals go into the term file of option B for you to prune.
The agent proposes entries and match patterns and leaves locators to the matcher,
so a wrong guess is a line you delete and not a wrong page number.

- **For:** this supplies the conceptual layer C lacks,
  and the repo runs per-chapter agents this way now.
  The book-wide sweeps cost roughly 70,000 to 150,000 tokens per chapter.
- **Against:** 47 drafts use different words for one idea,
  so a merge pass over the whole list is needed,
  and then your review of perhaps 800 to 1,500 entries.
  That review is the real cost of this option.

### E. Commercial or professional indexing

A freelance indexer, or a tool such as Cindex or Index Manager, works from final pages.
The result is tied to one pagination of one PDF.
It cannot serve the site or the EPUB,
and it is stale at the next release.
It fits a book that is finished, and this one is released continuously.

## Decision 2: how fine a locator is

- **Section level.**
  A locator is the H2 or H3 section containing the mention.
  All three outputs carry those anchors today,
  so this needs no markers anywhere.
  The cost: in the PDF the number is the page the section starts on,
  and the mention may be two pages further in.
- **Paragraph level, injected at build time.**
  The assembly adds an empty span, `[]{#ix-417}`, to the matching paragraph
  in the merged stream and in the site's per-chapter text.
  `Chapters/` stays free of it.
  The PDF page number is then the mention's own page.
  This is the better end state, and section level is a working first version of it.
- **Author-placed,** which is option A.

Whichever is chosen, the matcher needs rules that keep an entry short:

- One locator per section, however many times the term appears there.
- A section whose heading contains the term is the principal locator
  and is listed first or set in bold.
- A defining occurrence (the italic span) is principal too.
- An entry with more than about eight locators gets a warning:
  it needs subentries or a tighter pattern.
- Mentions inside listings do not count, except for the Python-names index,
  where a listing that uses `functools.cache` is a fair locator.
- In the PDF, adjacent pages collapse into a range, "212-214".

## Decision 3: one index or several

Programming books often split the index, and the harvest in C splits naturally:

1. **General index:** concepts, definitions, and patterns.
2. **Python names:** modules, functions, decorators, special methods, exceptions, keywords.
3. **Listings,** by filename.
4. **PEPs,** which can fold into the general index at 17 entries.

One merged index is what a print reader expects.
Separate ones are easier to generate and to browse on the site.
A reasonable split is two: a general index with PEPs folded in,
and a Python-names index, with listings as a third page on the site alone,
since the PDF cannot link to a listing (see below).

## Rendering in each output

### Site

A new page written by `build_site.py`,
linked from the contents page and from the fixed header beside Search and Contents.
It cannot be named `index.html`, which is the contents page;
`book-index.html` works.
Each locator reads as chapter and section:
"closure: 40 Foundations, *Closures*; 14 Decorators; 28 Function Objects".
A letter bar at the top and a filter box are small additions.
The index data could also feed `search.js` as synonyms,
so a search for "memoize" offers the "caching" entry.

### EPUB

One more chapter from `book_markdown()`, after the last chapter,
with a list of links to the namespaced ids.
EPUB 3 has `epub:type="index"` for this;
Kindle ignores it and other readers may use it.
Kindle builds no index of its own, so the links are the whole feature.
Long lists of links render slowly on e-ink,
which argues for one section per letter.

### PDF

Typst resolves the page of a label with `counter(page).at(<label>)`,
and pandoc's Typst writer keeps both heading ids and empty-span ids as labels.
Tested today with pandoc 3.11 and typst 0.15.1:

```typst
#let ixp(l) = link(l, context str(counter(page).at(l).first()))
immutability, #ixp(<ch12-immutability>)
```

That printed the correct page for a heading id and for a `[]{#ix-7}` span,
each as a working link.
So the index chapter in the PDF is raw Typst generated by the tool,
about thirty lines of preamble plus one line per entry,
with no Typst package to download.
The `in-dexter` package does the same job with its own `#index[]` markers,
but it fetches from the Typst registry at build time,
and the build has no such dependency now.

Two limits.
Pandoc's Typst writer drops the ids on fenced code blocks
(`listing_links.py` documents this),
so a PDF locator can name the section a listing sits in, not the listing.
And an index set in two columns needs `#columns(2)` around the generated block,
which is untested.

### Leanpub {#leanpub}

Your notes say "Indexing using Leanpub format, before publishing to leanpub."
Leanpub's index syntax is an inline marker placed after the word:

```
Call me Ishmael{i: Ishmael}
a cataract{i: "Niagara!cataract"} of sand
{i: "memoization|see{i:'caching'}"}
```

`!` makes a subentry, and `|see` and `|seealso` make cross-references.
Two facts about it matter here.
Leanpub builds the index into its PDF alone, with page numbers,
and not into its EPUB or web output.
And it requires that Leanpub generate the book from a manuscript;
in Leanpub's upload mode, where you supply your own PDF and EPUB,
the feature is unavailable and the index is whatever your files contain.

That makes Leanpub a question about the whole build, not about indexing:

- **Upload mode** keeps the Typst PDF and the two Kindle-tuned EPUBs as they are.
  The index is the one described above, and Leanpub receives it inside the files.
- **Generated mode** replaces those outputs with Leanpub's renderer.
  The manuscript would be a generated tree,
  since Markua differs from pandoc Markdown in heading ids, links between chapters,
  and attribute syntax.
  A `build_leanpub.py` would write it,
  and it can insert `{i: ...}` at each computed locator while doing so.

Under either mode the `{i:}` markers do not belong in `Chapters/`:
pandoc prints them as literal text in all three current outputs,
and every prose tool would read them as words.
With the index held as data (options B through D),
Leanpub's format becomes one more exporter, written when you need it.

## Gates {#gates}

An index held as data can be checked the way `tip records` checks its exceptions file:

- An entry whose patterns match nothing fails.
  This catches a term the text stopped using.
- A *see* or *see also* that names a missing entry fails.
- Two entries that differ by case or plural are reported.
- An entry with too many locators is reported and does not fail.
- A new italic term with no entry is reported,
  which keeps the definitions index current as chapters change.

None of this belongs in `verify` until the entry list has settled;
a report target, in the manner of `tip claims`, fits the first months.

## The options as packages

| Package | What you get | Tooling | Your time |
|---|---|---|---|
| 1. Mechanical | Python names, listings, PEPs, patterns; site page, EPUB chapter, PDF with page numbers | two to three days | an hour on the filter's stop list |
| 2. Add definitions | package 1 plus the italic-term index | half a day more | an evening pruning about 390 terms |
| 3. Add a curated term file | package 2 plus concepts, subentries, *see also*, drafted by agents and merged | two days more, plus 47 agent runs | several sessions reviewing 800 to 1,500 entries |
| 4. Source markers | hand-placed locators in `Chapters/` | a week, most of it teaching the prose tools to skip markers | weeks, and a permanent editing tax |

## Recommendation

Build package 1 with section-level locators, then 2, then 3,
and move to paragraph-level locators once the entry list is stable.
Each step is useful alone and none is thrown away by the next,
because all of them write the same data and share the three renderers.
Skip package 4.
Keep Leanpub as an exporter from that data,
and decide upload mode against generated mode separately,
since that choice determines whether Leanpub's index feature applies to this book.

## Questions for you

1. Is the PDF meant to be printed?
   If readers use it on screen, section-level locators are nearly as good
   as paragraph-level ones, since each is a link.
2. One index or two (general, and Python names)?
3. For Leanpub, upload mode or generated mode?
4. Should the Solutions files be indexed?
   None of the three outputs includes them today; readers reach them on GitHub.
5. Is the definitions harvest trustworthy enough to gate,
   that is, do you want a new italic term with no index entry to be reported?
