// Hover previews for listing links on the static site. A chapter's prose
// names its listings in code spans that build_site.py (via
// tools/listing_links.py) turns into a.listing-link anchors. In "preview"
// mode, resting the pointer on one shows the listing in a floating panel
// beside the link; in "jump" mode the anchor is an ordinary link. The mode
// is a small switch under the Contents link, remembered in localStorage,
// and preview is the default.
//
// A same-page target is cloned from the document. A cross-chapter target
// is fetched from its page (once per page, then cached) and cloned from
// that; if the fetch fails, the link still works as a link. Devices with
// no hover get no switch and no previews.
(function () {
  "use strict";

  var KEY = "listing-links-mode";   // "preview" | "jump"
  var SHOW_DELAY = 150;             // ms the pointer must rest first
  var HIDE_DELAY = 250;             // ms allowed to move into the panel

  var mode = "preview";
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

  function loadMode() {
    try {
      var saved = window.localStorage.getItem(KEY);
      if (saved === "preview" || saved === "jump") mode = saved;
    } catch (e) { /* storage unavailable: keep the default */ }
  }

  function saveMode() {
    try { window.localStorage.setItem(KEY, mode); } catch (e) { /* ignore */ }
  }

  // ── the switch ──────────────────────────────────────────────────────────

  function buildSwitch() {
    var box = h("div", "listing-mode");
    box.setAttribute("role", "group");
    box.setAttribute("aria-label", "Listing links");
    box.appendChild(h("span", "listing-mode-label", "Listings"));
    var preview = option(box, "preview", "Preview");
    box.appendChild(h("span", "sep", "·"));
    var jump = option(box, "jump", "Jump");
    function paint() {
      preview.setAttribute("aria-pressed", String(mode === "preview"));
      jump.setAttribute("aria-pressed", String(mode === "jump"));
    }
    box.addEventListener("click", function (ev) {
      var choice = ev.target && ev.target.getAttribute("data-mode");
      if (!choice) return;
      mode = choice;
      saveMode();
      paint();
      hide();
    });
    paint();
    document.body.appendChild(box);
  }

  function option(box, value, label) {
    var b = h("button", "", label);
    b.type = "button";
    b.setAttribute("data-mode", value);
    box.appendChild(b);
    return b;
  }

  // ── finding the listing ─────────────────────────────────────────────────

  function targetOf(link) {
    var href = link.getAttribute("href") || "";
    var hash = href.indexOf("#");
    if (hash < 0) return null;
    var page = href.slice(0, hash);
    var id = href.slice(hash + 1);
    var here = location.pathname.split("/").pop();
    if (!page || page === here) {
      var el = document.getElementById(id);
      return el ? Promise.resolve(el) : null;
    }
    if (!pages[page]) {
      pages[page] = fetch(page).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      }).then(function (html) {
        return new DOMParser().parseFromString(html, "text/html");
      });
    }
    return pages[page].then(function (doc) {
      return doc.getElementById(id);
    });
  }

  function stripIds(node) {
    if (node.removeAttribute) node.removeAttribute("id");
    var all = node.querySelectorAll ? node.querySelectorAll("[id]") : [];
    for (var i = 0; i < all.length; i++) all[i].removeAttribute("id");
    return node;
  }

  // ── the panel ───────────────────────────────────────────────────────────

  function show(link, listing) {
    hide();
    panel = h("div", "listing-preview");
    panel.appendChild(h("div", "listing-preview-title", link.textContent));
    panel.appendChild(stripIds(listing.cloneNode(true)));
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
    while (el && el !== document.body) {
      if (el.classList && el.classList.contains("listing-link")) return el;
      el = el.parentNode;
    }
    return null;
  }

  function onOver(ev) {
    if (mode !== "preview") return;
    var link = linkFrom(ev);
    if (!link) return;
    if (link === current) { cancelHide(); return; }
    cancelShow();
    showTimer = setTimeout(function () {
      var found = targetOf(link);
      if (!found) return;
      found.then(function (listing) {
        if (listing && link.matches(":hover")) show(link, listing);
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
    if (!document.querySelector("a.listing-link")) return;
    if (!canHover()) return;
    loadMode();
    buildSwitch();
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
