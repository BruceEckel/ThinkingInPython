# Effect programs: effects/, isolated from the main build

Chapter 44's "Effect Management" section shows one greeting program in
Koka, Flix, Scala (ZIO), and TypeScript (Effect). Each is a complete
program, extracted from `Chapters/44_*.md` by `tools/extract_effects.py`
into `effects/<lang>/`, the way chapter 18's crates land under `rust/`.
The marker is a first-line `//` comment naming the file relative to
`effects/` (`// koka/greet.kk`, `// flix/Greet.flix`, `// zio/Greet.scala`,
`// ts/greet.ts`), read by `Block.slash_slug`, the same property the
Rust extractor uses; the fence language (`koka`, `flix`, `scala`,
`typescript`) decides which extractor claims the block. A block in one
of those languages with no path line is a fragment and extracts nothing.

This is deliberate: only the `effects-*` tasks in `tools/tasks.py` build
or run anything here or need any of the four toolchains, so
`verify`/`gate`/`ci` work with none installed. The one read the gate
makes is `extract_effects.py`'s check mode, in `tip check` and the gate
since 2026-10-21: an edit to a chapter 44 listing that leaves `effects/`
stale fails the build, and `tip effects-sync` regenerates the four files.
`tip effects-all` syncs, fetches, builds, and runs them for real;
`tools/effects_run.py` is the runner and `effects/README.md` the setup.

Facts the runner depends on, each checked on 2026-10-21:

- Every program reads one line from stdin and prints the prompt and the
  greeting on one line, so `expected.txt` is one line and the runner
  pipes `NAME` to each. Edit the prompt or the greeting in the chapter
  and all four listings, and `expected.txt`, must change together.
- Flix 0.79's `Console` is an Effect in module `Sys.Console`
  (`use Sys.Console`), its `readln()` returns an `Option`, and a `main`
  whose Effect is `Console` runs under a default handler the compiler
  attaches (`@DefaultHandler` on `Console.runWithIO`). The chapter's
  prose about the Flix listing states each of these.
- Effect 4 (TypeScript) spells a service `Context.Service<Self, Shape>()("Id")`
  and the listing type-checks under TypeScript 7 with `strict`.
- Koka 3.2.9 compiles its C with `cl.exe` on Windows, which needs the
  vcvars environment; the runner builds it through `vswhere`. The type
  check happens before the C step, so a Koka failure that mentions
  `limits.h` or `kklib.h` is the C compiler's environment, not the
  listing.
- scala-cli reads `zio/project.scala` for the Scala and ZIO versions, so
  the listing carries no `//> using` directives. Its first run downloads
  about a hundred megabytes.

A toolchain the machine lacks is a skip in the runner's table, never a
failure, unless `REQUIRE=1` (CI passes it). Do not install a toolchain
to make a skip go away unless Bruce asks: downloading `flix.jar` and
`npm ci` into gitignored paths (`tip effects-fetch`) is fine, a global
install is his call.
