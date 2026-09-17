// Hover previews for the links in a chapter's text on the static site.
// Resting the pointer on a link shows what is at the other end in a
// floating panel beside the link; clicking it still follows the link, as
// any link would. What the panel holds depends on the target:
//
//   a listing (a.listing-link, written by tools/listing_links.py): the
//     listing;
//   a heading, on this page or another chapter's: the heading and the
//     text under it, up to the next heading of its level or MAX_BLOCKS;
//   a whole chapter (a link with no #anchor): its title and opening text;
//   a footnote reference: the note.
//
// A same-page target is cloned from the document. A cross-chapter target
// is fetched from its page (once per page, then cached) and cloned from
// that; if the fetch fails, the link still works as a link. A link to
// another site gets no panel, since a browser will not let this page read
// that one. Neither do the page's own navigation links (Contents, the
// chapter's table of contents, previous/next, a footnote's way back).
// Devices with no hover get no previews.
(function () {
  "use strict";

  var SHOW_DELAY = 150;             // ms the pointer must rest first
  var HIDE_DELAY = 250;             // ms allowed to move into the panel
  var MAX_BLOCKS = 12;              // paragraphs, listings, ... per excerpt

  var panel = null;
  var current = null;               // the link the panel belongs to
  var showTimer = null;
  var hideTimer = null;
  var pages = {};                   // href path -> Promise<Document>

  function h(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  }

  function canHover() {
    return !(window.matchMedia && window.matchMedia("(hover: none)").matches);
  }

  // ── which links get a panel ─────────────────────────────────────────────

  var EXTERNAL = /^([a-z][a-z0-9+.-]*:|\/\/)/i;
  var NAVIGATION = ".link-preview, .chapter-toc, .chapter-nav";

  function previewable(link) {
    if (!link.closest(".page") || link.closest(NAVIGATION)) return false;
    if (link.classList.contains("footnote-back")) return false;
    if (link.getAttribute("aria-hidden") === "true") return false;
    var href = link.getAttribute("href") || "";
    if (EXTERNAL.test(href)) return false;
    var page = href.split("#")[0];
    if (page === "index.html") return false;
    return href.indexOf("#") >= 0 || /\.html$/.test(page);
  }

  // ── finding the target ──────────────────────────────────────────────────

  // Resolves to { el, doc, page, whole }: the target element, the document
  // holding it, that document's path ("" for this page), and whether the
  // link named the chapter and no place within it.
  function targetOf(link) {
    var href = link.getAttribute("href") || "";
    var hash = href.indexOf("#");
    var page = hash < 0 ? href : href.slice(0, hash);
    var id = hash < 0 ? "" : decodeURIComponent(href.slice(hash + 1));
    var here = location.pathname.split("/").pop();
    if (page === here) page = "";
    if (!page && !id) return null;

    function find(doc) {
      var el = id ? doc.getElementById(id) : doc.querySelector(".page > h1");
      return el ? { el: el, doc: doc, page: page, whole: !id } : null;
    }

    if (!page) return Promise.resolve(find(document));
    if (!pages[page]) {
      pages[page] = fetch(page).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      }).then(function (html) {
        return new DOMParser().parseFromString(html, "text/html");
      });
    }
    return pages[page].then(find);
  }

  // ── choosing what to show ───────────────────────────────────────────────

  function level(el) {
    var m = /^H([1-6])$/.exec(el.tagName);
    return m ? Number(m[1]) : 0;
  }

  function isProse(el) { return level(el) === 0; }

  // The elements from `first` on, until `stop` says so, the page's closing
  // matter begins, or MAX_BLOCKS is reached (`more` then reports the cut).
  function collect(first, stop) {
    var nodes = [first];
    var more = false;
    for (var el = first.nextElementSibling; el; el = el.nextElementSibling) {
      if (el.matches(".chapter-ornament, .chapter-toc")) continue;
      if (el.matches(".footnotes, .chapter-nav") || stop(el, nodes)) break;
      if (nodes.length >= MAX_BLOCKS) { more = true; break; }
      nodes.push(el);
    }
    return { nodes: nodes, more: more };
  }

  function excerpt(found) {
    var el = found.el;
    if (found.whole) {
      // The chapter's opening: everything ahead of its first section, or
      // that section too when the chapter starts with a heading.
      var opening = collect(el, function (next, nodes) {
        return level(next) === 2 && nodes.some(isProse);
      });
      return { nodes: opening.nodes, more: true };
    }
    var depth = level(el);
    if (depth) {
      return collect(el, function (next) {
        return level(next) > 0 && level(next) <= depth;
      });
    }
    if (el.tagName === "LI" && el.closest(".footnotes")) {
      // A note ending in a list has its back-link as a child of its own,
      // where copyOf() cannot remove it from a parent.
      var note = Array.prototype.filter.call(el.children, function (part) {
        return !part.classList.contains("footnote-back");
      });
      return { nodes: note, more: false };
    }
    if (el.matches("div, pre, p, li, table, blockquote")) {
      return { nodes: [el], more: false };
    }
    return { nodes: [el.closest("p, li, td, blockquote, div") || el],
             more: false };
  }

  function textOf(doc, selector) {
    var el = doc.querySelector(selector);
    return el ? el.textContent.trim() : "";
  }

  // The small caption over the excerpt: the listing's name, and where the
  // target is when that is somewhere other than this page.
  function caption(link, found) {
    var parts = [];
    if (link.classList.contains("listing-link")) parts.push(link.textContent);
    if (link.classList.contains("footnote-ref")) parts.push("Footnote");
    if (found.page) {
      parts.push(textOf(found.doc, ".chapter-label"));
      if (!found.whole) parts.push(textOf(found.doc, ".page > h1"));
    } else if (!parts.length) {
      parts.push("In this chapter");
    }
    return parts.filter(Boolean).join(" · ");
  }

  // A clone fit for the panel: no ids to collide with the page's, no
  // footnote back-link, and a "#place" link taken from another page made
  // to name that page.
  function copyOf(node, page) {
    var copy = node.cloneNode(true);
    var all = [copy].concat(
      Array.prototype.slice.call(copy.querySelectorAll("*")));
    all.forEach(function (el) {
      el.removeAttribute("id");
      if (el.classList.contains("footnote-back")) { el.remove(); return; }
      var href = el.tagName === "A" ? el.getAttribute("href") : null;
      if (page && href && href.charAt(0) === "#") {
        el.setAttribute("href", page + href);
      }
    });
    return copy;
  }

  // ── the panel ───────────────────────────────────────────────────────────

  function show(link, found) {
    hide();
    var content = excerpt(found);
    panel = h("div", "link-preview");
    var title = caption(link, found);
    if (title) panel.appendChild(h("div", "link-preview-title", title));
    content.nodes.forEach(function (node) {
      panel.appendChild(copyOf(node, found.page));
    });
    if (content.more) {
      panel.appendChild(h("p", "link-preview-more",
                          "Continues: click the link to read on."));
    }
    panel.addEventListener("mouseenter", cancelHide);
    panel.addEventListener("mouseleave", scheduleHide);
    document.body.appendChild(panel);
    current = link;
    place(link);
  }

  function place(link) {
    var rect = link.getBoundingClientRect();
    var column = document.querySelector(".page");
    var left = column ? column.getBoundingClientRect().left : rect.left;
    var width = panel.offsetWidth;
    var height = panel.offsetHeight;
    var gap = 8;
    var top;
    if (rect.bottom + gap + height <= window.innerHeight
        || rect.top - gap - height < 0) {
      top = rect.bottom + gap;      // below the link, the usual case
    } else {
      top = rect.top - gap - height; // above, when the bottom is short
    }
    var maxLeft = window.innerWidth - width - 16;
    left = Math.max(16, Math.min(left, maxLeft));
    panel.style.top = (top + window.scrollY) + "px";
    panel.style.left = (left + window.scrollX) + "px";
  }

  function hide() {
    cancelHide();
    if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
    panel = null;
    current = null;
  }

  function scheduleHide() {
    cancelHide();
    hideTimer = setTimeout(hide, HIDE_DELAY);
  }

  function cancelHide() {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }

  function cancelShow() {
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
  }

  // ── wiring ──────────────────────────────────────────────────────────────

  function linkFrom(ev) {
    var el = ev.target;
    var link = el && el.closest ? el.closest("a[href]") : null;
    return link && previewable(link) ? link : null;
  }

  function onOver(ev) {
    var link = linkFrom(ev);
    if (!link) return;
    if (link === current) { cancelHide(); return; }
    cancelShow();
    showTimer = setTimeout(function () {
      var found = targetOf(link);
      if (!found) return;
      found.then(function (target) {
        if (target && link.matches(":hover")) show(link, target);
      }, function () { /* fetch failed: the link still jumps */ });
    }, SHOW_DELAY);
  }

  function onOut(ev) {
    var link = linkFrom(ev);
    if (!link) return;
    cancelShow();
    if (link === current) scheduleHide();
  }

  function init() {
    if (!canHover()) return;
    document.addEventListener("mouseover", onOver);
    document.addEventListener("mouseout", onOut);
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") hide();
    });
    window.addEventListener("scroll", function () {
      if (current && panel) place(current);
    }, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
