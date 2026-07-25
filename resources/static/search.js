// Client-side search for the static site. No dependencies and no server: the
// index (search-index.json, built by tools/search_index.py) is one record per
// chapter section, fetched the first time the reader opens the box and cached
// by the browser after that.
//
// This script builds its own UI, so a page needs only search.css and this
// file. Open with the "Search" link, Ctrl+K (Cmd+K), or "/". Arrow keys move
// through results, Enter follows one, Escape closes.
(function () {
  "use strict";

  var INDEX_URL = "search-index.json";
  var MAX_RESULTS = 40;
  var SNIPPET_RADIUS = 110;

  var docs = null;      // the index, once loaded
  var loading = null;   // the in-flight fetch, so we only ask once
  var selected = 0;
  var els = {};

  function h(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  }

  function build() {
    var toggle = h("button", "search-toggle", "Search");
    // Chapter pages carry a fixed "Contents" link in the same corner.
    if (document.querySelector(".toc-toggle")) {
      toggle.className += " beside-toc";
    }
    toggle.type = "button";
    toggle.setAttribute("aria-haspopup", "dialog");
    toggle.addEventListener("click", open);

    var scrim = h("div", "search-scrim");
    var dialog = h("div", "search-dialog");
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", "Search the book");

    var field = h("div", "search-field");
    var input = document.createElement("input");
    input.type = "search";
    input.placeholder = "Search the book";
    input.setAttribute("aria-label", "Search the book");
    var count = h("span", "search-count", "");
    field.appendChild(input);
    field.appendChild(count);

    var results = h("ul", "search-results");
    var note = h("p", "search-note", "");
    var hint = h("p", "search-hint");
    hint.innerHTML =
      "<kbd>&uarr;</kbd> <kbd>&darr;</kbd> to move &middot; " +
      "<kbd>Enter</kbd> to open &middot; <kbd>Esc</kbd> to close";

    dialog.appendChild(field);
    dialog.appendChild(note);
    dialog.appendChild(results);
    dialog.appendChild(hint);
    scrim.appendChild(dialog);
    document.body.appendChild(toggle);
    document.body.appendChild(scrim);

    els = { scrim: scrim, input: input, count: count,
            results: results, note: note };

    scrim.addEventListener("click", function (e) {
      if (e.target === scrim) close();
    });
    input.addEventListener("input", function () { run(input.value); });
    input.addEventListener("keydown", onKey);
  }

  function load() {
    if (loading) return loading;
    loading = fetch(INDEX_URL)
      .then(function (r) {
        if (!r.ok) throw new Error(r.status + " " + r.statusText);
        return r.json();
      })
      .then(function (data) { docs = data; return data; });
    return loading;
  }

  function open() {
    els.scrim.setAttribute("data-open", "");
    els.input.focus();
    els.input.select();
    if (docs) return;
    els.note.textContent = "Loading the index…";
    load().then(function () {
      els.note.textContent = "";
      run(els.input.value);
    }).catch(function (err) {
      els.note.textContent = "Could not load the search index (" +
        err.message + ").";
    });
  }

  function close() {
    els.scrim.removeAttribute("data-open");
    els.input.blur();
  }

  function isOpen() {
    return els.scrim.hasAttribute("data-open");
  }

  // --- searching --------------------------------------------------------

  // Matching is by substring, so "operator" already finds "operators". Trim a
  // trailing plural "s" so the query works in that direction too. Everything
  // downstream (scoring, highlighting) uses the trimmed form.
  function stem(term) {
    if (term.length > 3 && /[^s]s$/.test(term)) return term.slice(0, -1);
    return term;
  }

  function tokens(query) {
    return query.toLowerCase().split(/\s+/).filter(function (t) {
      return t.length > 0;
    }).map(stem);
  }

  // Every token must appear somewhere in the record. Headings outrank body
  // text, and a match on the whole query outranks the same words scattered.
  function score(doc, terms, phrase) {
    var heading = doc.s.toLowerCase();
    var chapter = doc.c.toLowerCase();
    var body = doc.t.toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i];
      var inBody = body.indexOf(term) !== -1;
      var inHeading = heading.indexOf(term) !== -1;
      var inChapter = chapter.indexOf(term) !== -1;
      if (!inBody && !inHeading && !inChapter) return 0;
      if (inHeading) total += 12;
      if (inChapter) total += 6;
      if (inBody) total += 1 + Math.min(occurrences(body, term), 5);
    }
    if (terms.length > 1 || phrase.length > 2) {
      if (heading.indexOf(phrase) !== -1) total += 40;
      if (body.indexOf(phrase) !== -1) total += 20;
    }
    return total;
  }

  function occurrences(haystack, needle) {
    var n = 0;
    var at = haystack.indexOf(needle);
    while (at !== -1 && n < 6) {
      n += 1;
      at = haystack.indexOf(needle, at + needle.length);
    }
    return n;
  }

  function search(query) {
    var terms = tokens(query);
    if (!terms.length) return [];
    var phrase = query.toLowerCase().trim();
    var hits = [];
    for (var i = 0; i < docs.length; i++) {
      var points = score(docs[i], terms, phrase);
      if (points > 0) hits.push({ doc: docs[i], points: points });
    }
    hits.sort(function (a, b) { return b.points - a.points; });
    return hits.slice(0, MAX_RESULTS);
  }

  // --- rendering --------------------------------------------------------

  function escapeHtml(text) {
    return text.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // Wrap each occurrence of a term in <mark>, working on escaped text so the
  // book's own angle brackets cannot become markup.
  function highlight(text, terms) {
    var out = escapeHtml(text);
    for (var i = 0; i < terms.length; i++) {
      var pattern = terms[i].replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      out = out.replace(new RegExp("(" + pattern + ")", "gi"),
                        "<mark>$1</mark>");
    }
    return out;
  }

  function snippet(text, terms, phrase) {
    var lower = text.toLowerCase();
    var at = lower.indexOf(phrase);
    if (at === -1) {
      for (var i = 0; i < terms.length && at === -1; i++) {
        at = lower.indexOf(terms[i]);
      }
    }
    if (at === -1) at = 0;
    var start = Math.max(0, at - SNIPPET_RADIUS);
    var end = Math.min(text.length, at + SNIPPET_RADIUS * 2);
    var cut = text.slice(start, end).trim();
    return (start > 0 ? "…" : "") + cut +
           (end < text.length ? "…" : "");
  }

  function href(doc) {
    return doc.a ? doc.u + "#" + doc.a : doc.u;
  }

  function render(hits, query) {
    var terms = tokens(query);
    var phrase = query.toLowerCase().trim();
    els.results.textContent = "";
    selected = 0;

    if (!query.trim()) {
      els.count.textContent = docs ? docs.length + " sections" : "";
      els.note.textContent = "";
      return;
    }
    els.count.textContent = hits.length
      ? hits.length + (hits.length === MAX_RESULTS ? "+ results" : " results")
      : "";
    els.note.textContent = hits.length ? "" : "Nothing matches that.";

    hits.forEach(function (hit, i) {
      var doc = hit.doc;
      var li = document.createElement("li");
      li.setAttribute("role", "option");
      if (i === 0) li.setAttribute("aria-selected", "true");
      var a = document.createElement("a");
      a.href = href(doc);

      var where = h("div", "search-where", doc.l + " · " + doc.c);
      var heading = h("div", "search-heading");
      heading.innerHTML = highlight(doc.s, terms);
      var body = h("div", "search-snippet");
      body.innerHTML = highlight(snippet(doc.t, terms, phrase), terms);

      a.appendChild(where);
      a.appendChild(heading);
      a.appendChild(body);
      li.appendChild(a);
      els.results.appendChild(li);
    });
  }

  function run(query) {
    if (!docs) return;
    render(search(query), query);
  }

  // --- keyboard ---------------------------------------------------------

  function move(delta) {
    var items = els.results.children;
    if (!items.length) return;
    items[selected].removeAttribute("aria-selected");
    selected = (selected + delta + items.length) % items.length;
    items[selected].setAttribute("aria-selected", "true");
    items[selected].scrollIntoView({ block: "nearest" });
  }

  function onKey(e) {
    if (e.key === "Escape") { close(); return; }
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); return; }
    if (e.key === "ArrowUp") { e.preventDefault(); move(-1); return; }
    if (e.key === "Enter") {
      var items = els.results.children;
      if (items.length) {
        e.preventDefault();
        items[selected].querySelector("a").click();
      }
    }
  }

  function onGlobalKey(e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName);
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      isOpen() ? close() : open();
      return;
    }
    if (e.key === "/" && !typing && !isOpen()) {
      e.preventDefault();
      open();
    }
  }

  function start() {
    build();
    document.addEventListener("keydown", onGlobalKey);
    // The index is small enough to prefetch once the page is idle, so the
    // first search feels instant. A failure here is silent: open() retries.
    if (window.requestIdleCallback) {
      window.requestIdleCallback(function () { load().catch(function () {}); });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
