"use strict";

// Reading level and theme, shared by every page. The inline head script has already applied any stored or
// linked choice to <html data-level data-theme> before first paint; this file wires the controls.

const LEVELS = {
  beginner: "The key findings, in plain language.",
  amateur: "The process, comparisons and results.",
  expert: "Definitions, full tables and reproduction.",
};
const NAMES = { beginner: "Essentials", amateur: "Investigation", expert: "Research" };
const THEMES = ["auto", "light", "dark"];
const LEVEL_CODES = { beginner: "b", amateur: "a", expert: "e" };
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

function isRendered(node) {
  return Boolean(node?.getClientRects().length);
}

function readingEdge() {
  const bar = document.getElementById("levelbar");
  return bar ? bar.getBoundingClientRect().bottom : 0;
}

function nearestToEdge(nodes, edge) {
  let nearest = null;
  let nearestDistance = Infinity;
  for (const node of nodes) {
    const rect = node.getBoundingClientRect();
    const distance = edge < rect.top ? rect.top - edge : edge > rect.bottom ? edge - rect.bottom : 0;
    if (distance < nearestDistance) {
      nearest = node;
      nearestDistance = distance;
    }
  }
  return nearest;
}

function chapterSections() {
  return Array.from(document.querySelectorAll(".article-body > .chapter[id]"));
}

function chapterAnchor() {
  const visible = chapterSections().filter(isRendered);
  const edge = readingEdge() + 24;
  const chapter = nearestToEdge(visible, edge);
  if (!chapter) return null;
  const rect = chapter.getBoundingClientRect();
  if (rect.top > window.innerHeight || rect.bottom < edge) return null;
  return { kind: "chapter", id: chapter.id, index: chapterSections().indexOf(chapter), top: rect.top };
}

function eventAnchor() {
  const allEvents = Array.from(document.querySelectorAll(".record-event"));
  const events = allEvents.filter(isRendered);
  const edge = readingEdge() + 24;
  const event = nearestToEdge(events, edge);
  if (!event) return null;
  const rect = event.getBoundingClientRect();
  if (rect.top > window.innerHeight || rect.bottom < edge) return null;
  return { kind: "event", index: allEvents.indexOf(event), sequence: event.dataset.seq, top: rect.top };
}

function readingAnchor() {
  return chapterAnchor() || eventAnchor();
}

function linkedChapterAfterPriorTail() {
  const rawId = location.hash.slice(1);
  if (!rawId) return null;
  let id = rawId;
  try {
    id = decodeURIComponent(rawId);
  } catch {
    // An invalid fragment cannot identify an article chapter.
  }

  const sections = chapterSections();
  const index = sections.findIndex((section) => section.id === id);
  if (index < 0) return null;

  const section = sections[index];
  if (!isRendered(section)) return null;
  const sectionRect = section.getBoundingClientRect();
  const edge = readingEdge();
  if (sectionRect.top <= edge || sectionRect.top >= window.innerHeight || sectionRect.bottom <= sectionRect.top) return null;

  const nearest = chapterAnchor();
  if (!nearest || nearest.id === id || nearest.index >= index) return null;
  const priorRect = sections[nearest.index].getBoundingClientRect();
  const anchorEdge = edge + 24;
  if (priorRect.top > anchorEdge || priorRect.bottom < anchorEdge) return null;

  return { kind: "chapter", id, index, top: edge + 16 };
}

function nearestVisibleChapter(sections, from) {
  for (let distance = 1; distance < sections.length; distance += 1) {
    const next = sections[from + distance];
    if (next && isRendered(next)) return next;
    const previous = sections[from - distance];
    if (previous && isRendered(previous)) return previous;
  }
  return sections.find(isRendered) || null;
}

function chapterTitle(section) {
  const labelledBy = section.getAttribute("aria-labelledby");
  const title = labelledBy ? document.getElementById(labelledBy) : section.querySelector("h2");
  return title?.textContent.trim().replace(/\s+/g, " ") || section.id;
}

function locateEvent(anchor) {
  const events = Array.from(document.querySelectorAll(".record-event"));
  const indexed = events[anchor.index];
  if (indexed?.dataset.seq === anchor.sequence) return indexed;
  return events
    .map((event, index) => ({ event, distance: Math.abs(index - anchor.index) }))
    .filter(({ event }) => event.dataset.seq === anchor.sequence)
    .sort((left, right) => left.distance - right.distance)[0]?.event || null;
}

function withLevel(href, level) {
  const url = new URL(href, location.href);
  url.searchParams.set("level", level);
  return url;
}

function applyLevel(level, announce, preserveReadingPlace = true, placeBeforeControl = undefined) {
  const changed = currentLevel() !== level;
  let keep = changed && preserveReadingPlace
    ? (placeBeforeControl === undefined ? readingAnchor() : placeBeforeControl)
    : null;
  if (changed && preserveReadingPlace) {
    const linked = linkedChapterAfterPriorTail();
    if (linked && keep?.id !== linked.id) keep = linked;
  }
  root.dataset.level = level;
  store("tpa-level", level);
  const url = withLevel(location.href, level);
  let continuation = null;
  if (keep?.kind === "chapter") {
    const sections = chapterSections();
    const same = sections.find((section) => section.id === keep.id);
    const target = same && isRendered(same) ? same : nearestVisibleChapter(sections, keep.index);
    if (target) {
      const fallback = target.id !== keep.id;
      continuation = {
        kind: "chapter",
        id: target.id,
        top: fallback ? readingEdge() + 16 : keep.top,
        fallback,
        title: fallback ? chapterTitle(target) : "",
      };
      if (fallback) url.hash = target.id;
    }
  } else if (keep?.kind === "event") {
    continuation = keep;
  }
  if (url.href !== location.href) history.replaceState(history.state, "", url);
  for (const link of document.querySelectorAll("a[data-internal]")) {
    link.href = withLevel(link.getAttribute("href"), level).href;
  }
  for (const input of document.querySelectorAll('input[name="level"]')) input.checked = input.value === level;
  const whoFor = document.getElementById("who-for");
  if (whoFor) whoFor.textContent = LEVELS[level];
  if (announce) {
    const status = document.getElementById("level-status");
    if (status) {
      const moved = continuation?.fallback ? ` Continued at ${continuation.title}.` : "";
      status.textContent = `Reading depth: ${NAMES[level]}. ${LEVELS[level]} The findings and their limits are unchanged.${moved}`;
    }
  }
  document.dispatchEvent(new CustomEvent("tpa:level", { detail: level }));
  if (continuation) {
    requestAnimationFrame(() => {
      const target = continuation.kind === "chapter"
        ? document.getElementById(continuation.id)
        : locateEvent(continuation);
      if (isRendered(target)) window.scrollBy(0, target.getBoundingClientRect().top - continuation.top);
    });
  }
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
    prompt: ["This is the scripted control.", "The instructions supplied the sequence, with no confidentiality rule. An offer and reply cannot show that the agents planned it independently."],
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
  const levelBlocks = [];
  for (let node = target; node && node.closest(".article-body"); node = node.parentElement) {
    if (node.matches("[data-lv]")) levelBlocks.push(node);
  }
  let needsScroll = false;
  if (levelBlocks.some((block) => getComputedStyle(block).display === "none")) {
    const level = ["beginner", "amateur", "expert"].find((candidate) =>
      levelBlocks.every((block) => block.dataset.lv.split(" ").includes(LEVEL_CODES[candidate])));
    if (!level) return;
    applyLevel(level, true, false);
    needsScroll = true;
  }
  for (let node = target; node && node.closest(".article-body"); node = node.parentElement) {
    if (node.tagName === "DETAILS" && !node.open) {
      node.open = true;
      needsScroll = true;
    }
  }
  if (needsScroll) window.scrollBy(0, target.getBoundingClientRect().top - readingEdge() - 16);
}

function wireContents() {
  const menu = document.getElementById("contents-menu");
  if (!menu) return;
  const narrow = matchMedia("(max-width: 1023px)");
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

function measureLevelbar() {
  const bar = document.getElementById("levelbar");
  if (!bar || !window.ResizeObserver) return;
  const observer = new ResizeObserver(() => {
    root.style.setProperty("--bar", `${bar.getBoundingClientRect().height}px`);
  });
  observer.observe(bar);
}

function wire() {
  let preparedLevelPlace = null;
  document.addEventListener("pointerdown", (event) => {
    const target = event.target?.closest?.('label[for], input[name="level"]');
    if (!target) return;
    const input = target.matches('input[name="level"]') ? target : document.getElementById(target.htmlFor);
    if (input?.name !== "level") return;
    preparedLevelPlace = { level: input.value, anchor: readingAnchor(), at: Date.now() };
  }, true);
  document.addEventListener("keydown", (event) => {
    const input = event.target?.closest?.('input[name="level"]');
    if (!input || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", " ", "Spacebar"].includes(event.key)) return;
    preparedLevelPlace = { level: null, anchor: readingAnchor(), at: Date.now() };
  }, true);

  for (const input of document.querySelectorAll('input[name="level"]')) {
    input.addEventListener("change", () => {
      if (!input.checked) return;
      let placeBeforeControl;
      if (preparedLevelPlace) {
        const pending = preparedLevelPlace;
        preparedLevelPlace = null;
        if (Date.now() - pending.at < 2000 && (pending.level === null || pending.level === input.value)) {
          placeBeforeControl = pending.anchor;
        }
      }
      applyLevel(input.value, true, true, placeBeforeControl);
    });
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
  measureLevelbar();
}

wire();
