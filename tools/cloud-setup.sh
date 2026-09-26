#!/bin/bash
# Installs the book's toolchain in a Claude Code cloud session. Paste
# this file into the cloud environment's Setup script field (the cloud
# environment menu in a session's title bar, then Edit). The environment
# keeps its own copy, so paste it again after editing this file.
#
# The script runs as root on Ubuntu 24.04 when a session starts, and
# the cloud then caches the VM's filesystem, so later sessions skip it
# until the script changes or about a week passes. Run
# `tip tools-check-full` in the first session after a change.
#
# Why not the install lines `tip tools-check-full` prints: its pandoc,
# typst, and vale lines download GitHub releases, and the session's
# GitHub proxy refuses release and API requests for any repository not
# attached to the session, at every network access level (`uv self
# update` fails the same way). Every tool here comes from PyPI, apt, or
# the Go module proxy instead.
#
# Left out: typst (`tip pdf` only), which no PyPI or apt package
# ships. A crates.io build took 4m27s on a 4-core VM, too close to the
# setup script's five-minute limit; `cargo install --locked typst-cli`
# builds it in a session that needs it. gh (`tip release` only) is a
# local job.
#
# A failed install prints a line and never fails the script, because a
# nonzero exit stops the session from starting at all.

fail() { echo "cloud-setup: $1 failed" >&2; }

# The image's toolchains, in case this shell's PATH lacks them.
export PATH="/root/.local/bin:/root/.cargo/bin:/usr/local/go/bin:$PATH"

# uv: the image's 0.8.17 cannot fetch Python 3.15, so replace it from
# PyPI. --user overwrites /root/.local/bin/uv, which is first on PATH.
python3 -m pip install --user -q -U uv || fail uv
uv python install 3.15 || fail "python 3.15"

# The rest runs in parallel.

# vale (tip prose), built from source through the Go module proxy.
# tip prose runs `vale sync` for its style packages, which works here.
(GOBIN=/usr/local/bin go install github.com/vale-cli/vale/v3/cmd/vale@latest \
    || fail vale) &

# An SVG rasterizer (the figure gallery's PNGs, the EPUB).
(apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq librsvg2-bin \
    || fail rsvg-convert) &

# pandoc >= 3.5 (make site, epub, pdf). apt's is 3.1, so link the
# binary that PyPI's pypandoc_binary bundles.
bundled_pandoc() {
    python3 -c 'import pathlib, pypandoc
print(pathlib.Path(pypandoc.__file__).parent / "files" / "pandoc")'
}
(python3 -m pip install --user -q pypandoc_binary \
    && ln -sf "$(bundled_pandoc)" /usr/local/bin/pandoc \
    || fail pandoc) &

wait
exit 0
