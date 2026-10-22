#!/usr/bin/env python3
"""Build and run chapter 44's four Effect programs, each with its own toolchain.

The Effect Management chapter writes one greeting program in Koka, Flix,
Scala (ZIO), and TypeScript (Effect). ``extract_effects.py`` keeps a copy
of each under ``effects/``; this tool compiles and runs them, feeds each
the same name on stdin, and compares its stdout with
``effects/expected.txt``. One transcript, four programs. The compile step
is the test that matters: every claim the chapter makes about these
listings is a claim about their signatures, and a compiler checks the
signatures as written.

Nothing in the main build calls this. The four toolchains are optional,
so each program is a `Program` whose `locate()` finds its tool or says
what is missing, and a missing tool is a **skip**, reported in the final
table and never a failure, unless ``--require`` turns it into one (the CI
job passes that, since it installs all four). What each program needs:

- **koka**: ``koka`` on PATH, or ``KOKA=path/to/koka`` in the
  environment, plus a C compiler. On Windows the compiler is MSVC, whose
  headers need the vcvars environment; `msvc_env()` finds it through
  ``vswhere`` so the run works from any shell. The build goes under
  ``effects/koka/.koka/`` (gitignored).
- **flix**: ``java`` on PATH and the compiler jar at
  ``effects/flix/flix.jar`` (gitignored; ``--fetch`` downloads the
  pinned ``FLIX_VERSION``) or ``FLIX_JAR=path`` in the environment.
- **zio**: ``scala-cli`` on PATH, or ``SCALA_CLI=path``. The Scala and
  ZIO versions are directives in ``effects/zio/project.scala``, which
  scala-cli reads for every file in that directory, so the book's listing
  carries none. The first run downloads the compiler and the library.
- **ts**: ``node`` and ``npm`` on PATH, and ``effects/ts/node_modules/``
  installed by ``--fetch`` (``npm ci`` against the committed lockfile;
  the ``effect`` and ``typescript`` versions are in ``package.json``).
  The step runs ``tsc --noEmit`` first and then the program under Node's
  own type stripping.

``--fetch`` does the two downloads and exits; ``tip effects-fetch`` runs
it, and ``tip effects-all`` runs sync, fetch, and test in order.
``--only koka,ts`` limits a run. Each program's stdout is compared after
normalizing line endings; on a mismatch the diff is printed and the
program fails. Tool chatter (download progress, "Compiling project")
goes to stderr and is shown only when a step fails.

Usage:
    python -m tools.effects_run                 # build and run what is installed
    python -m tools.effects_run --require       # a missing toolchain fails
    python -m tools.effects_run --only flix,ts  # a subset
    python -m tools.effects_run --fetch         # flix.jar and node_modules
"""

import argparse
import difflib
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tools.config import ROOT

EFFECTS = ROOT / "effects"
EXPECTED = EFFECTS / "expected.txt"
NAME = "Bruce"
"""The line every program reads from stdin; expected.txt greets it."""

FLIX_VERSION = "0.79.0"
"""The Flix release --fetch downloads; the chapter's listing was checked
against it on 2026-10-21. Bump it here and in effects/README.md."""
FLIX_URL = (f"https://github.com/flix/flix/releases/download/"
            f"v{FLIX_VERSION}/flix.jar")


@dataclass(frozen=True)
class Step:
    """One command of a program's build-and-run, in its directory."""

    argv: list[str]
    stdin: str | None = None
    """Text piped to the command; None leaves stdin closed."""
    check_output: bool = False
    """Whether this step's stdout is the transcript to compare."""


@dataclass(frozen=True)
class Program:
    key: str
    directory: str
    locate: Callable[[], list[Step] | str]
    """The steps to run, or a one-line reason the program is skipped."""


@dataclass(frozen=True)
class Outcome:
    key: str
    status: str
    """"ok", "skip", or "FAIL"."""
    detail: str
    seconds: float


def which(name: str, env_var: str) -> str | None:
    """`env_var`'s value if set, else `name` on PATH, else None."""
    override = os.environ.get(env_var)
    if override:
        return override
    return shutil.which(name)


def msvc_env() -> dict[str, str] | None:
    """The environment vcvars64.bat sets up, on Windows without one.

    Koka compiles its C output with `cl.exe`, which it finds on PATH but
    which cannot find its own headers unless INCLUDE and LIB are set.
    vswhere (installed with any Visual Studio or Build Tools) names the
    installation, and its vcvars64.bat prints the variables. None when
    not on Windows, when the shell already has them, or when there is no
    MSVC to find.
    """
    if os.name != "nt" or "INCLUDE" in os.environ:
        return None
    vswhere = (Path(os.environ.get("ProgramFiles(x86)",
                                   r"C:\Program Files (x86)"))
               / "Microsoft Visual Studio" / "Installer" / "vswhere.exe")
    if not vswhere.exists():
        return None
    found = subprocess.run(
        [str(vswhere), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
         "-property", "installationPath"],
        capture_output=True, text=True).stdout.strip()
    if not found:
        return None
    bat = Path(found) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    if not bat.exists():
        return None
    # One string, not a list: subprocess would escape the inner quotes
    # and cmd would then read the path's spaces as separate words. /S
    # makes cmd strip exactly the outer pair of quotes.
    dump = subprocess.run(
        f'cmd /S /C "call "{bat}" >nul && set"',
        capture_output=True, text=True).stdout
    env = dict(os.environ)
    for line in dump.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            env[key] = value
    return env


def locate_koka() -> list[Step] | str:
    koka = which("koka", "KOKA")
    if not koka:
        return "koka not on PATH (install Koka, or set KOKA=path/to/koka)"
    # An absolute path: Windows resolves a bare program name against the
    # parent's directory, not the child's cwd.
    exe = EFFECTS / "koka" / ("greet.exe" if os.name == "nt" else "greet")
    return [
        Step([koka, "-c", "-v0", "--builddir=.koka", "-o", "greet",
              "greet.kk"]),
        Step([str(exe)], stdin=f"{NAME}\n", check_output=True),
    ]


def locate_flix() -> list[Step] | str:
    java = shutil.which("java")
    if not java:
        return "java not on PATH (Flix runs on the JVM)"
    jar = os.environ.get("FLIX_JAR") or str(EFFECTS / "flix" / "flix.jar")
    if not Path(jar).exists():
        return "flix.jar not fetched (tip effects-fetch, or set FLIX_JAR=path)"
    return [Step([java, "-jar", jar, "Greet.flix"],
                 stdin=f"{NAME}\n", check_output=True)]


def locate_zio() -> list[Step] | str:
    scala_cli = which("scala-cli", "SCALA_CLI")
    if not scala_cli:
        return "scala-cli not on PATH (install it, or set SCALA_CLI=path)"
    return [Step([scala_cli, "run", ".", "--server=false"],
                 stdin=f"{NAME}\n", check_output=True)]


def locate_ts() -> list[Step] | str:
    node = shutil.which("node")
    if not node:
        return "node not on PATH"
    tsc = EFFECTS / "ts" / "node_modules" / "typescript" / "bin" / "tsc"
    if not tsc.exists():
        return "node_modules not installed (tip effects-fetch)"
    return [
        Step([node, str(tsc), "--noEmit"]),
        Step([node, "greet.ts"], stdin=f"{NAME}\n", check_output=True),
    ]


PROGRAMS = [
    Program("koka", "koka", locate_koka),
    Program("flix", "flix", locate_flix),
    Program("zio", "zio", locate_zio),
    Program("ts", "ts", locate_ts),
]


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n")


def run_program(program: Program, env: dict[str, str] | None) -> Outcome:
    started = time.perf_counter()
    located = program.locate()
    if isinstance(located, str):
        return Outcome(program.key, "skip", located, 0.0)
    expected = normalize(EXPECTED.read_text(encoding="utf-8"))
    cwd = EFFECTS / program.directory
    for step in located:
        shown = " ".join(Path(a).name if os.sep in a or "/" in a else a
                         for a in step.argv)
        print(f"  [{program.key}] {shown}")
        try:
            proc = subprocess.run(
                step.argv, cwd=cwd, env=env, input=step.stdin,
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=900)
        except (OSError, subprocess.TimeoutExpired) as e:
            return Outcome(program.key, "FAIL", f"{shown}: {e}",
                           time.perf_counter() - started)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            return Outcome(program.key, "FAIL",
                           f"{shown}: exit {proc.returncode}",
                           time.perf_counter() - started)
        if step.check_output and normalize(proc.stdout) != expected:
            diff = "".join(difflib.unified_diff(
                expected.splitlines(keepends=True),
                normalize(proc.stdout).splitlines(keepends=True),
                "expected.txt", f"{program.key} stdout"))
            sys.stderr.write(diff + "\n")
            return Outcome(program.key, "FAIL", "output differs (diff above)",
                           time.perf_counter() - started)
    return Outcome(program.key, "ok", "", time.perf_counter() - started)


def fetch() -> int:
    """Download flix.jar and install the TypeScript packages, if absent."""
    jar = EFFECTS / "flix" / "flix.jar"
    if jar.exists():
        print(f"{jar.relative_to(ROOT).as_posix()}: present")
    else:
        print(f"downloading Flix {FLIX_VERSION} -> "
              f"{jar.relative_to(ROOT).as_posix()}")
        tmp = jar.with_suffix(".part")
        urllib.request.urlretrieve(FLIX_URL, tmp)
        tmp.replace(jar)
    npm = shutil.which("npm")
    modules = EFFECTS / "ts" / "node_modules"
    if modules.exists():
        print(f"{modules.relative_to(ROOT).as_posix()}: present")
    elif not npm:
        print("npm not on PATH: effects/ts/node_modules not installed")
    else:
        print("npm ci in effects/ts")
        proc = subprocess.run([npm, "ci", "--no-audit", "--no-fund"],
                              cwd=EFFECTS / "ts")
        if proc.returncode != 0:
            return proc.returncode
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="download flix.jar and run npm ci, then exit")
    ap.add_argument("--require", action="store_true",
                    help="a missing toolchain is a failure, not a skip")
    ap.add_argument("--only", default="",
                    help="comma-separated program keys to run")
    args = ap.parse_args(argv)
    if args.fetch:
        return fetch()
    keys = {k for k in args.only.split(",") if k}
    unknown = keys - {p.key for p in PROGRAMS}
    if unknown:
        ap.error(f"unknown program(s): {', '.join(sorted(unknown))}")
    chosen = [p for p in PROGRAMS if not keys or p.key in keys]
    env = msvc_env()
    outcomes = [run_program(p, env) for p in chosen]
    print()
    for o in outcomes:
        timing = f"{o.seconds:6.1f}s" if o.status != "skip" else " " * 7
        print(f"  {o.key:<5} {o.status:<5} {timing}  {o.detail}")
    failed = [o for o in outcomes if o.status == "FAIL"]
    skipped = [o for o in outcomes if o.status == "skip"]
    ran = len(outcomes) - len(skipped)
    print(f"\n{ran} program(s) ran, {len(failed)} failed, "
          f"{len(skipped)} skipped.")
    if failed or (args.require and skipped):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
