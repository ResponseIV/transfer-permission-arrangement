"use strict";

// Reading level and theme, shared by every page. The inline head script has already applied any stored or
// linked choice to <html data-level data-theme> before first paint; this file wires the controls.

const LEVELS = {
  beginner: "No AI or statistics background needed. Plain words, every term explained.",
  amateur: "You know what an LLM and an AI agent are. The findings and how they were measured.",
  expert: "You work on multi-agent safety, evals or monitoring. Denominators, intervals, methods and caveats.",
};
const NAMES = { beginner: "Beginner", amateur: "AI amateur", expert: "Field expert" };
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
  return LEVELS[root.dataset.level] ? root.dataset.level : "amateur";
}

// The first shared (level-independent) element on screen, so a switch keeps the reader's place.
function anchor() {
  const bar = document.getElementById("levelbar");
  const top = bar ? bar.getBoundingClientRect().bottom : 0;
  const candidates = document.querySelectorAll("main h2, main h3, main figure, main table, main .tiles, main .cards, main .stack-list, main .event, main .ex-summary");
  for (const node of candidates) {
    if (node.closest("[data-lv]")) continue;
    const rect = node.getBoundingClientRect();
    if (rect.height && rect.bottom > top) return { node, top: rect.top };
  }
  return null;
}

function withLevel(href, level) {
  const url = new URL(href, location.href);
  if (level === "amateur") url.searchParams.delete("level");
  else url.searchParams.set("level", level);
  return url;
}

function applyLevel(level, announce) {
  const keep = window.scrollY > 0 ? anchor() : null;
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
  for (const row of document.querySelectorAll("[data-level-row]")) {
    row.classList.toggle("current", row.dataset.levelRow === level);
  }
  for (const details of document.querySelectorAll("details[data-open-at]")) {
    details.open = details.dataset.openAt.split(" ").includes(level);
  }
  if (keep) window.scrollBy(0, keep.node.getBoundingClientRect().top - keep.top);
  if (announce) {
    const status = document.getElementById("level-status");
    if (status) status.textContent = `Reading level: ${NAMES[level]}. The results are the same at every level.`;
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
}

wire();
