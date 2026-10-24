# Effect programs for Thinking in Python

The [Effect Management](../Chapters/44_Effects--Effect_Management.md)
chapter writes one greeting program in four languages besides Python:
[Koka](https://koka-lang.github.io/) and [Flix](https://flix.dev/), two
languages with native Effects, and Scala with [ZIO](https://zio.dev/)
and TypeScript with [Effect](https://effect.website/), two library
Effect systems. This directory holds a complete, buildable copy of each,
extracted from the chapter, and the project files each one needs.

It is deliberately separate from the rest of the book's tooling, the
way `rust/` is. Only the `effects-*` tasks enter this directory or need
any of the four toolchains: `tip verify`, `tip gate`, and `tip ci` all
work with none installed. The one thing the gate does here is compare
the four source files with the chapter (`tools/extract_effects.py` in
check mode), which needs no compiler. Building and running them is an
extra, opt-in step for a reader or maintainer who wants to see the four
programs do the same thing, or to check that the chapter's listings
still compile against current releases.

## Layout

```
effects/
  expected.txt        what every program prints when told the name "Bruce"
  koka/greet.kk       extracted from the chapter
  flix/Greet.flix     extracted from the chapter
  zio/Greet.scala     extracted from the chapter
  zio/project.scala   scala-cli directives: the Scala and ZIO versions
  ts/greet.ts         extracted from the chapter
  ts/package.json     the effect and typescript versions
  ts/package-lock.json  the lockfile `npm ci` installs from
  ts/tsconfig.json    strict type checking of the listing
```

The four extracted files are never edited here: the chapter is the
source, and `tip effects-sync` regenerates them. Everything else is a
real, hand-maintained project file.

## Setup

Each program needs its own toolchain, and the runner skips any that is
missing, so you can install one and run that alone.

- **Koka**: the `koka` compiler on PATH (the release tarball or
  `install.sh` from [its releases](https://github.com/koka-lang/koka/releases);
  checked with 3.2.9) and a C compiler. On Windows the C compiler is
  MSVC, and the runner finds the Visual Studio Build Tools through
  `vswhere` so no developer shell is needed. `KOKA=path/to/koka`
  in the environment names a compiler that is not on PATH.
- **Flix**: a Java 21 runtime on PATH. The compiler is one jar,
  `flix/flix.jar`, which `tip effects-fetch` downloads at the pinned
  version (`FLIX_VERSION` in `tools/effects_run.py`, 0.79.0) and git
  ignores. `FLIX_JAR=path` names one elsewhere.
- **Scala / ZIO**: [scala-cli](https://scala-cli.virtuslab.org/) on PATH
  (checked with 1.18.0) and a Java runtime. The first run downloads
  Scala 3.3 and ZIO, as `zio/project.scala` pins them.
  `SCALA_CLI=path` names a launcher that is not on PATH.
- **TypeScript / Effect**: Node 22.18 or later (the first release that runs `.ts` files without a flag) and npm on PATH. `tip
  effects-fetch` runs `npm ci` against the committed lockfile into
  `ts/node_modules/`, which git ignores.

### Installing Koka and scala-cli

Java, Node, and npm are common enough that their own installers do.
The other two are less so, and each has a one-line install.

Koka, release 3.2.9 (the release's own install script pins it):

```
# Linux or macOS: installs to /usr/local (asks for sudo) and needs clang or gcc
curl -sSL https://github.com/koka-lang/koka/releases/download/v3.2.9/install.sh | sh

# Windows, in cmd: installs to %LOCALAPPDATA%\koka and adds it to PATH;
# installs clang if no C compiler is found, and offers the Visual Studio
# Build Tools (already present if you build the Rust crates)
curl -sSL -o %TEMP%\install.bat https://github.com/koka-lang/koka/releases/download/v3.2.9/install.bat && %TEMP%\install.bat

# Windows, in PowerShell: the same installer
curl.exe -sSL -o $env:TEMP\install.bat https://github.com/koka-lang/koka/releases/download/v3.2.9/install.bat; & $env:TEMP\install.bat
```

Or unpack the `koka-v3.2.9-<os>-<arch>.tar.gz` release tarball anywhere
and run with `KOKA=<that dir>/bin/koka`, which is how this machine's
first run was made. Open a new shell after the installer, so PATH is
current.

scala-cli, any 1.x (checked with 1.18.0):

```
winget install virtuslab.scalacli                 # Windows
brew install Virtuslab/scala-cli/scala-cli        # macOS
curl -sSLf https://scala-cli.virtuslab.org/get | sh   # Linux
```

Or unpack `scala-cli-x86_64-pc-win32.zip` (or the matching archive for
another platform) from [its releases](https://github.com/VirtusLab/scala-cli/releases)
anywhere and run with `SCALA_CLI=<that dir>/scala-cli`.

`tip effects-test` names, in its table, whichever of the four it did
not find, so run it after each install to see what is left.

## Running it

From anywhere in the repository:

```
tip effects-all      # sync from the book, fetch, then build and run each program
```

`effects-all` runs `effects-sync`, `effects-fetch`, and `effects-test`;
each is also available on its own:

```
tip effects-sync     # regenerate the four source files from Chapters/
tip effects-fetch    # download flix.jar and install ts/node_modules (both gitignored)
tip effects-test     # build and run every program whose toolchain is present
tip effects-test ONLY=flix,ts   # a subset
tip effects-test REQUIRE=1      # a missing toolchain fails instead of skipping
tip effects-clean    # remove the fetched pieces and every build directory
```

Without `tip` on PATH, `uv run tip effects-all` does the same from
inside the repository.

`effects-test` feeds every program the name in `tools/effects_run.py`
(`NAME`) on stdin and compares its stdout with `expected.txt`, so the
four programs are held to one transcript. The compile step is the test
that matters: the chapter's claims about these listings are claims about
their signatures (Koka's Effect row, ZIO's three type parameters, the
service types in the TypeScript version), and a compiler checks the
signatures as written. The run ends with one line per program and a count:

```
  koka  ok       4.2s
  flix  ok       6.8s
  zio   skip           scala-cli not on PATH (install it, or set SCALA_CLI=path)
  ts    ok       2.1s

3 program(s) ran, 0 failed, 1 skipped.
```

## In CI

The `effects` job in `.github/workflows/ci.yml` installs all four
toolchains on Ubuntu and runs `effects-test` with `REQUIRE=1`. It is
opt-in like the full gates: run the workflow from the Actions tab with
`run_effects` checked, or put `[effects-ci]` in a push commit message.

## Upgrading a toolchain

A new release of any of the four can change what a listing means or
whether it compiles, so an upgrade is a chapter 44 event:

1. Bump the pin: `FLIX_VERSION` in `tools/effects_run.py`, the
   directives in `zio/project.scala`, the versions in `ts/package.json`
   (then `npm install` to refresh the lockfile), or the installed Koka.
2. `tip effects-clean effects-all`.
3. Reread the chapter's prose about any listing whose compile changed:
   the text describes specific signatures and specific library calls.
4. Update the checked-with versions in this file.
