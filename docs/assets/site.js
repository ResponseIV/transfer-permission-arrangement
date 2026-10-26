"use strict";

// Reading level and theme, shared by every page. The inline head script has already applied any stored or
// linked choice to <html data-level data-theme> before first paint; this file wires the controls.

const LEVELS = {
  beginner: "The key findings, in plain language.",
  amateur: "The process, comparisons and results.",
  expert: "Definitions, full tables and reproduction.",
};
const NAMES = { beginner: "The essentials", amateur: "The investigation", expert: "The research" };
const THEMES = ["auto", "light", "dark"];
const root = document.documentElement;

function store(key, value) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch (error) {
    // Storage blocked: the choice still holds for this page and in the URL.
  }
}

function currentLevel() {
  return LEVELS[root.dataset.level] ? root.dataset.level : "beginner";
}

// The first shared (level-independent) element on screen, so a switch keeps the reader's place.
function anchor(nextLevel) {
  const bar = document.getElementById("levelbar");
  const top = bar ? bar.getBoundingClientRect().bottom : 0;
  const candidates = document.querySelectorAll("main h2, main h3, main figure, main table, main .tiles, main .cards, main .stack-list, main .event, main .ex-summary");
  for (const node of candidates) {
    const levelBlock = node.closest("[data-lv]");
    const code = { beginner: "b", amateur: "a", expert: "e" }[nextLevel];
    if (levelBlock && !levelBlock.dataset.lv.split(" ").includes(code)) continue;
    const rect = node.getBoundingClientRect();
    if (rect.height && rect.bottom > top) return { node, top: rect.top };
  }
  return null;
}

function withLevel(href, level) {
  const url = new URL(href, location.href);
  url.searchParams.set("level", level);
  return url;
}

function applyLevel(level, announce) {
  const keep = window.scrollY > 0 ? anchor(level) : null;
  root.dataset.level = level;
  store("tpa-level", level);
  const url = withLevel(location.href, level);
  if (url.href !== location.href) history.replaceState(history.state, "", url);
  for (const link of document.querySelectorAll("a[data-internal]")) {
    link.href = withLevel(link.getAttribute("href"), level).href;
  }
  for (const input of document.querySelectorAll('input[name="level"]')) input.checked = input.value === level;
  const whoFor = document.getElementById("who-for");
  if (whoFor) whoFor.textContent = LEVELS[level];
  if (keep) window.scrollBy(0, keep.node.getBoundingClientRect().top - keep.top);
  if (announce) {
    const status = document.getElementById("level-status");
    if (status) status.textContent = `Reading depth: ${NAMES[level]}. ${LEVELS[level]} The findings and their limits are unchanged.`;
  }
  document.dispatchEvent(new CustomEvent("tpa:level", { detail: level }));
}

function currentTheme() {
  return THEMES.includes(root.dataset.theme) ? root.dataset.theme : "auto";
}

function showTheme() {
  const button = document.getElementById("theme");
  if (!button) return;
  const theme = currentTheme();
  const next = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
  button.querySelector("span").textContent = { auto: "Auto", light: "Light", dark: "Dark" }[theme];
  button.setAttribute("aria-label", `Theme: ${theme === "auto" ? "follows your system" : theme}. Switch to ${next === "auto" ? "your system's theme" : next}.`);
}

function wireExhibit() {
  const record = document.getElementById("exhibit-record");
  if (!record) return;
  const findings = {
    pages: ["An offer. A reply. Enough to suspect an arrangement?", "The pages show what was written. They leave out how the exchange came about."],
    reads: ["The offer was read. The reply was used.", "The event order fits an arrangement. It still does not tell us who supplied the plan."],
    prompt: ["The whole sequence was supplied as a script.", "No confidentiality rule was given. The same visible offer and reply can have a different explanation."],
  };
  for (const input of document.querySelectorAll('input[name="exhibit"]')) {
    input.addEventListener("change", () => {
      if (!input.checked) return;
      record.dataset.record = input.value;
      for (const node of record.querySelectorAll("[data-evidence]")) {
        node.hidden = !node.dataset.evidence.split(" ").includes(input.value);
      }
      document.getElementById("exhibit-finding").textContent = findings[input.value][0];
      document.getElementById("exhibit-explanation").textContent = findings[input.value][1];
    });
  }
}

function revealLinkedSection() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target || !target.closest(".article-body")) return;
  const block = target.closest("[data-lv]");
  if (!block || getComputedStyle(block).display !== "none") return;
  applyLevel(block.dataset.lv.includes("a") ? "amateur" : "expert", true);
  target.scrollIntoView();
}

function wireContents() {
  const menu = document.getElementById("contents-menu");
  if (!menu) return;
  const narrow = matchMedia("(max-width: 999px)");
  const fitMenu = () => { menu.open = !narrow.matches; };
  fitMenu();
  narrow.addEventListener("change", fitMenu);
  menu.querySelector("nav").addEventListener("click", (event) => {
    if (event.target.closest("a") && narrow.matches) menu.open = false;
  });
  const links = [...menu.querySelectorAll('a[href^="#"]')];
  const sections = links.map((link) => document.querySelector(link.getAttribute("href")));
  function trackSection() {
    const edge = (document.getElementById("levelbar")?.getBoundingClientRect().bottom || 0) + 130;
    let active = null;
    for (const section of sections) {
      if (section?.getClientRects().length && section.getBoundingClientRect().top <= edge) active = section.id;
    }
    for (const link of links) {
      if (link.hash === `#${active}`) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
  }
  let scheduled = false;
  window.addEventListener("scroll", () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { trackSection(); scheduled = false; });
  }, { passive: true });
  document.addEventListener("tpa:level", trackSection);
  window.addEventListener("hashchange", revealLinkedSection);
  revealLinkedSection();
  trackSection();
}

function measureControls() {
  const bar = document.getElementById("levelbar");
  const controls = document.querySelector(".ex-controls");
  if (!window.ResizeObserver) return;
  const observer = new ResizeObserver(() => {
    if (bar) root.style.setProperty("--bar", `${bar.getBoundingClientRect().height}px`);
    if (controls) root.style.setProperty("--controls-height", `${controls.getBoundingClientRect().height}px`);
  });
  if (bar) observer.observe(bar);
  if (controls) observer.observe(controls);
}

function wire() {
  for (const input of document.querySelectorAll('input[name="level"]')) {
    input.addEventListener("change", () => input.checked && applyLevel(input.value, true));
  }
  const button = document.getElementById("theme");
  if (button) {
    button.addEventListener("click", () => {
      const next = THEMES[(THEMES.indexOf(currentTheme()) + 1) % THEMES.length];
      if (next === "auto") delete root.dataset.theme;
      else root.dataset.theme = next;
      store("tpa-theme", next === "auto" ? null : next);
      showTheme();
    });
  }
  showTheme();
  applyLevel(currentLevel(), false);
  wireExhibit();
  wireContents();
  measureControls();
}

wire();
