// Progress memory for a Solutions page's step ladders.
//
// tools/solution_steps.py folds each exercise's answer into nested
// <details> elements: "Where to look", then "The shape", then
// "Solution". The nesting is what orders the steps, and the browser
// renders it with no script, so this file adds only what HTML cannot:
//
//   - each step a reader opens stays open on the next visit, kept in
//     localStorage under this page's path and the exercise's heading id;
//   - a row above the exercises counts the open steps and offers to
//     close every one, which also forgets them.
//
// A later "check your answer" step (a listing run in the browser) would
// be one more <details> level in the same ladder, and would need no
// change here: a step is any <details> whose summary carries one of
// the LABELS, wherever it sits.
(function () {
  "use strict";

  var LABELS = { "Where to look": 1, "The shape": 1, "Solution": 1 };
  var KEY = "tip-steps:" + location.pathname;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
    catch (e) { return {}; }
  }

  function save(state) {
    try {
      if (Object.keys(state).length) {
        localStorage.setItem(KEY, JSON.stringify(state));
      } else {
        localStorage.removeItem(KEY);
      }
    } catch (e) { /* private mode, or storage disabled: forget nothing */ }
  }

  function label(details) {
    var summary = details.firstElementChild;
    if (!summary || summary.tagName !== "SUMMARY") return null;
    var text = summary.textContent.trim();
    return LABELS[text] ? text : null;
  }

  // The heading of the exercise a ladder belongs to: the nearest h2
  // before the ladder's outermost <details>.
  function exerciseId(details) {
    var root = details;
    while (root.parentElement && root.parentElement.tagName === "DETAILS") {
      root = root.parentElement;
    }
    for (var el = root.previousElementSibling; el; el = el.previousElementSibling) {
      if (el.tagName === "H2" && el.id) return el.id;
    }
    return "";
  }

  function build() {
    var steps = [];
    var all = document.querySelectorAll("details");
    for (var i = 0; i < all.length; i++) {
      var text = label(all[i]);
      if (!text) continue;
      all[i].className += " step";
      all[i].setAttribute("data-step", exerciseId(all[i]) + "/" + text);
      steps.push(all[i]);
    }
    if (!steps.length) return;

    var state = load();
    steps.forEach(function (details) {
      if (state[details.getAttribute("data-step")]) details.open = true;
    });

    var bar = document.createElement("div");
    bar.className = "steps-bar";
    var count = document.createElement("span");
    var hide = document.createElement("button");
    hide.type = "button";
    hide.textContent = "Hide every answer";
    bar.appendChild(count);
    bar.appendChild(hide);
    var first = document.querySelector(".page h2");
    if (first) first.parentNode.insertBefore(bar, first);

    function refresh() {
      var open = steps.filter(function (d) { return d.open; }).length;
      count.textContent = open
        ? open + " step" + (open === 1 ? "" : "s") + " revealed"
        : "Nothing revealed yet";
      hide.disabled = !open;
      bar.className = "steps-bar ready";
    }

    steps.forEach(function (details) {
      details.addEventListener("toggle", function () {
        var current = load();
        var key = details.getAttribute("data-step");
        if (details.open) current[key] = 1; else delete current[key];
        save(current);
        refresh();
      });
    });

    hide.addEventListener("click", function () {
      steps.forEach(function (d) { d.open = false; });
      save({});
      refresh();
    });

    refresh();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
