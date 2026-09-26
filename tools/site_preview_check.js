#!/usr/bin/env node
// Check the site's link previews by using them: load every built page
// under jsdom, hover and tap its links, and look at the panel
// resources/static/link-preview.js puts up.
//
//   node tools/site_preview_check.js            # every page in build/site
//   node tools/site_preview_check.js 29 index   # pages whose names start so
//
// `tip preview-check` builds the site first and then runs this, and so
// does the site job in .github/workflows/ci.yml, ahead of the deploy. No
// local gate runs it: it needs node, which nothing else in the repo does,
// and on its first run it needs the network, to install jsdom under
// build/node/ (build/ is derived and gitignored, so the repo gains no
// package.json). JSDOM_VERSION pins the major, so a jsdom release cannot
// change what a deploy depends on.
//
// The pages come from build/site, the script from resources/static, so an
// edit to the script is tested without a site rebuild. What it fails on:
//
//   - a link into the book (a heading, a chapter, a listing, a footnote)
//     that gets no panel, or a navigation or external link that gets one;
//   - a panel that is empty, keeps an id or a footnote back-link, or holds
//     a "#place" link taken from another page and still naming this one;
//   - a link inside a panel opening a second panel, or Escape not closing;
//   - a tap that fails to show the panel with its "Go there" link, a
//     second tap that fails to follow the link, a tap elsewhere that leaves
//     the panel up, or a mouse click that gets caught as a tap.
//
// Nine links in ten are the line-number anchors pandoc puts in a listing,
// all of one shape, so only the first CODE_LINES_PER_PAGE on a page are
// hovered, which takes a quarter off the run. Most of the rest goes to
// parsing the pages that cross-chapter links fetch. jsdom lays nothing
// out, so where the panel sits and how it looks are not checked here.
"use strict";

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const SITE = path.join(ROOT, "build", "site");
const SCRIPT = path.join(ROOT, "resources", "static", "link-preview.js");
const NODE_DIR = path.join(ROOT, "build", "node");
const JSDOM_VERSION = "27";
const CODE_LINES_PER_PAGE = 5;

function loadJsdom() {
  const local = path.join(NODE_DIR, "node_modules", "jsdom");
  if (!fs.existsSync(local)) {
    console.log("Installing jsdom under build/node/ (first run only)...");
    fs.mkdirSync(NODE_DIR, { recursive: true });
    execSync("npm install --no-save --no-package-lock --no-audit --no-fund"
             + ` --prefix "${NODE_DIR}" jsdom@${JSDOM_VERSION}`,
             { stdio: "inherit" });
  }
  return require(local);
}

const tick = () => new Promise(resolve => setImmediate(resolve));

// jsdom follows a "#place" link on a timer of its own, so the hashchange
// that closes the panel arrives some ticks after the click. Left pending,
// it sometimes closed the *next* link's panel. A timer queued
// after jsdom's fires after it.
const settle = async () => {
  await new Promise(resolve => setTimeout(resolve, 0));
  await tick();
};

// What the script should make of a link, judged from the page's markup and
// by rules written apart from the script's own.
function kindOf(a) {
  const href = a.getAttribute("href");
  if (/^[a-z][a-z0-9+.-]*:/i.test(href)) return "external";
  if (a.closest(".chapter-nav")) return "previous/next";
  if (a.closest(".chapter-toc")) return "chapter contents";
  if (a.classList.contains("toc-toggle")) return "Contents";
  if (a.classList.contains("footnote-back")) return "footnote back-link";
  if (a.getAttribute("aria-hidden") === "true") return "code line";
  if (a.classList.contains("footnote-ref")) return "footnote";
  if (a.classList.contains("listing-link")) return "listing";
  return href.includes("#") ? "heading" : "chapter";
}

const PREVIEWED = new Set(["footnote", "listing", "heading", "chapter"]);

function pointerDown(w, el, pointerType) {
  const ev = new w.Event("pointerdown", { bubbles: true });
  Object.defineProperty(ev, "pointerType", { value: pointerType });
  el.dispatchEvent(ev);
}

// True when the click's default action (following the link) was left alone.
function click(w, el) {
  return el.dispatchEvent(
    new w.MouseEvent("click", { bubbles: true, cancelable: true }));
}

function openPage(jsdom, name, script) {
  const virtualConsole = new jsdom.VirtualConsole(); // drops "navigation
  const dom = new jsdom.JSDOM(                       // not implemented"
    fs.readFileSync(path.join(SITE, name), "utf8"),
    { url: "http://localhost/" + name, runScripts: "outside-only",
      virtualConsole });
  const w = dom.window;
  // Timers fire at once, fetch reads the built page, and every link counts
  // as hovered: jsdom has no pointer for :hover to follow.
  w.setTimeout = fn => { fn(); return 0; };
  w.clearTimeout = () => {};
  w.fetch = page => {
    const file = path.join(SITE, page);
    const ok = fs.existsSync(file);
    return Promise.resolve({
      ok, status: ok ? 200 : 404,
      text: () => Promise.resolve(fs.readFileSync(file, "utf8")) });
  };
  const matches = w.Element.prototype.matches;
  w.Element.prototype.matches = function (selector) {
    return selector === ":hover" || matches.call(this, selector);
  };
  w.eval(script);
  return w;
}

const panelIn = w => w.document.querySelector(".link-preview");

async function hoverEvery(w, name, counts, problems) {
  const firstOfKind = new Map();
  let codeLines = 0;
  for (const a of w.document.querySelectorAll("a[href]")) {
    const href = a.getAttribute("href");
    const at = `${name} ${href}`;
    const kind = kindOf(a);
    if (kind === "code line" && ++codeLines > CODE_LINES_PER_PAGE) continue;
    const expected = PREVIEWED.has(kind);
    if (expected && !firstOfKind.has(kind)) firstOfKind.set(kind, a);
    pointerDown(w, a, "mouse");
    (a.firstElementChild || a).dispatchEvent(
      new w.MouseEvent("mouseover", { bubbles: true }));
    await tick(); await tick();
    const panel = panelIn(w);
    const row = counts[kind] = counts[kind] || { panel: 0, none: 0 };
    row[panel ? "panel" : "none"] += 1;
    if (!panel) {
      if (expected) problems.push(`${at}: no panel`);
      continue;
    }
    if (!expected) problems.push(`${at}: a ${kind} link got a panel`);
    if (!panel.textContent.trim()) problems.push(`${at}: empty panel`);
    if (panel.querySelector("[id]")) problems.push(`${at}: id in panel`);
    if (panel.querySelector(".footnote-back")) {
      problems.push(`${at}: footnote back-link in panel`);
    }
    if (panel.querySelector(".link-preview-go")) {
      problems.push(`${at}: "Go there" in a hovered panel`);
    }
    if (href[0] !== "#") {
      for (const inner of panel.querySelectorAll("a[href^='#']")) {
        if (inner.getAttribute("aria-hidden") === "true") continue;
        problems.push(`${at}: panel link ${inner.getAttribute("href")}`
                      + " names this page, not the one it came from");
      }
    }
    const inner = panel.querySelector("a[href]");
    if (inner) {
      inner.dispatchEvent(new w.MouseEvent("mouseover", { bubbles: true }));
      await tick();
      if (panelIn(w) !== panel
          || w.document.querySelectorAll(".link-preview").length !== 1) {
        problems.push(`${at}: a link inside the panel opened another`);
      }
    }
    w.document.dispatchEvent(new w.KeyboardEvent("keydown", { key: "Escape" }));
    if (panelIn(w)) problems.push(`${at}: Escape left the panel up`);
  }
  return firstOfKind;
}

async function tapOne(w, a, at, problems) {
  await settle();
  pointerDown(w, a, "touch");
  a.dispatchEvent(new w.MouseEvent("mouseover", { bubbles: true }));
  await tick(); await tick();
  if (panelIn(w)) problems.push(`${at}: a tap's mouseover opened the panel`);
  if (click(w, a)) problems.push(`${at}: first tap followed the link`);
  await tick(); await tick();
  const panel = panelIn(w);
  const go = panel && panel.querySelector(".link-preview-go");
  if (!panel) {
    problems.push(`${at}: first tap showed no panel`);
    return;
  }
  if (!go || go.getAttribute("href") !== a.getAttribute("href")) {
    problems.push(`${at}: no "Go there" link to the target`);
  }
  pointerDown(w, w.document.body, "touch");
  click(w, w.document.body);
  if (panelIn(w)) problems.push(`${at}: a tap elsewhere left the panel up`);

  pointerDown(w, a, "touch");
  click(w, a);
  await tick(); await tick();
  pointerDown(w, a, "touch");
  if (!click(w, a)) problems.push(`${at}: second tap did not follow the link`);
  if (panelIn(w)) problems.push(`${at}: second tap left the panel up`);
  await settle();

  pointerDown(w, a, "mouse");
  if (!click(w, a)) problems.push(`${at}: a mouse click was caught as a tap`);
  if (panelIn(w)) problems.push(`${at}: a mouse click opened the panel`);
  await settle();
}

async function main() {
  if (!fs.existsSync(path.join(SITE, "index.html"))) {
    console.error(`No built site at ${SITE}; run \`tip site\` first.`);
    process.exit(2);
  }
  const jsdom = loadJsdom();
  const script = fs.readFileSync(SCRIPT, "utf8");
  const wanted = process.argv.slice(2);
  const names = fs.readdirSync(SITE)
    .filter(f => f.endsWith(".html"))
    .filter(f => !wanted.length || wanted.some(p => f.startsWith(p)))
    .sort();
  const counts = {};
  const problems = [];
  let taps = 0;
  for (const name of names) {
    const w = openPage(jsdom, name, script);
    const firstOfKind = await hoverEvery(w, name, counts, problems);
    for (const [kind, a] of firstOfKind) {
      await tapOne(w, a, `${name} ${a.getAttribute("href")} (${kind}, tapped)`,
                   problems);
      taps += 1;
    }
    w.close();
  }

  console.log(`Hovered every link on ${names.length} page(s):`);
  for (const kind of Object.keys(counts).sort()) {
    const { panel, none } = counts[kind];
    console.log(`  ${kind.padEnd(20)} ${String(panel).padStart(6)} panel`
                + `  ${String(none).padStart(6)} none`);
  }
  console.log(`Tapped ${taps} link(s): the first of each kind on each page.`);
  if (problems.length) {
    console.log(`\n${problems.length} problem(s):`);
    for (const p of problems) console.log("  " + p);
    process.exit(1);
  }
  console.log("Link previews OK");
}

main().catch(err => { console.error(err); process.exit(2); });
