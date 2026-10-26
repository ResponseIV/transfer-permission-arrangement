"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { test } = require("node:test");
const vm = require("node:vm");

const source = readFileSync(new URL("../docs/assets/site.js", `file://${__filename}`), "utf8");

function site({ level = "beginner", href = "https://example.test/?level=beginner#transfer", chapters = [], targets = [], decoy, events = [], scrollY = 2369 } = {}) {
  const root = { dataset: { level, theme: "light" }, style: { setProperty() {} } };
  const window = {
    scrollY,
    innerHeight: 1000,
    scrollBy(_x, y) { this.scrollY += y; },
    addEventListener() {},
  };
  const inputs = ["beginner", "amateur", "expert"].map((value) => ({
    id: `lv-${value}`, name: "level", value, checked: value === level, listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
    closest(selector) { return selector === 'input[name="level"]' ? this : null; },
    matches(selector) { return selector === 'input[name="level"]'; },
  }));
  const labels = inputs.map((input) => ({
    htmlFor: input.id,
    closest(selector) { return selector === 'label[for], input[name="level"]' ? this : null; },
    matches() { return false; },
  }));
  const documentListeners = {};
  const status = { textContent: "" };
  const whoFor = { textContent: "" };
  const bar = { getBoundingClientRect: () => ({ bottom: 80, height: 56 }) };
  const article = {
    parentElement: null,
    matches: (selector) => selector === ".article-body",
    closest: (selector) => selector === ".article-body" ? article : null,
  };
  let currentHref = href;
  const internalLink = {
    href: "",
    getAttribute: () => "./explorer.html#single/sol-21?record=instr&step=3",
  };

  function rendered(node) {
    const code = { beginner: "b", amateur: "a", expert: "e" }[root.dataset.level];
    return !node.dataset.lv || node.dataset.lv.split(" ").includes(code);
  }

  function makeChapter({ id, allowed, positions, height = 1800, heading = id }) {
    const node = {
      id,
      dataset: allowed ? { lv: allowed } : {},
      parentElement: article,
      textContent: heading,
      getAttribute(name) { return name === "aria-labelledby" ? `${id}-title` : null; },
      getClientRects() { return rendered(this) ? [{}] : []; },
      getBoundingClientRect() {
        const top = (positions[root.dataset.level] ?? positions.default) - window.scrollY;
        return { top, bottom: top + height, height };
      },
      closest(selector) {
        if (selector === ".article-body") return article;
        if (selector === "[data-lv]" && this.dataset.lv) return this;
        return null;
      },
      matches(selector) { return selector === "[data-lv]" && Boolean(this.dataset.lv); },
      scrollIntoView() {
        const desired = bar.getBoundingClientRect().bottom + 16;
        window.scrollBy(0, this.getBoundingClientRect().top - desired);
      },
    };
    return node;
  }

  const sectionNodes = chapters.map(makeChapter);
  const targetNodes = targets.map((target) => ({
    id: target.id,
    tagName: target.detail ? "DETAILS" : "H3",
    open: target.open ?? false,
    dataset: target.allowed ? { lv: target.allowed } : {},
    parentElement: article,
    textContent: target.heading || target.id,
    getAttribute() { return null; },
    getClientRects() { return rendered(this) ? [{}] : []; },
    getBoundingClientRect() {
      const top = (target.positions[root.dataset.level] ?? target.positions.default) - window.scrollY;
      return { top, bottom: top + 300, height: 300 };
    },
    closest(selector) { return selector === ".article-body" ? article : null; },
    matches(selector) { return selector === "[data-lv]" && Boolean(this.dataset.lv); },
  }));
  const timeline = {};
  const makeEvent = (event) => ({
    dataset: { seq: String(event.seq ?? event.index) },
    getClientRects() { return event.visible?.[root.dataset.level] === false ? [] : [{}]; },
    getBoundingClientRect() {
      const top = event.positions[root.dataset.level] - window.scrollY;
      return { top, bottom: top + 180, height: 180 };
    },
    closest(selector) { return selector === "#timeline" ? timeline : null; },
  });
  let eventNodes = events.map(makeEvent);
  const decoyNode = decoy ? {
    dataset: {},
    getBoundingClientRect() {
      const top = (decoy.positions[root.dataset.level] ?? decoy.positions.default) - window.scrollY;
      return { top, bottom: top + decoy.height, height: decoy.height };
    },
    closest() { return null; },
  } : null;

  const document = {
    documentElement: root,
    dispatchEvent(event) {
      if (event.type === "tpa:level") eventNodes = events.map(makeEvent);
    },
    addEventListener(name, callback) {
      documentListeners[name] = [...(documentListeners[name] || []), callback];
    },
    getElementById(id) {
      if (id === "levelbar") return bar;
      if (id === "who-for") return whoFor;
      if (id === "level-status") return status;
      const input = inputs.find((item) => item.id === id);
      if (input) return input;
      const chapter = [...sectionNodes, ...targetNodes].find((section) => section.id === id);
      if (chapter) return chapter;
      const title = sectionNodes.find((section) => `${section.id}-title` === id);
      return title ? { textContent: title.textContent } : null;
    },
    querySelectorAll(selector) {
      if (selector === 'input[name="level"]') return inputs;
      if (selector === "a[data-internal]") return [internalLink];
      if (selector === ".article-body > .chapter[id]") return sectionNodes;
      if (selector === ".record-event") return eventNodes;
      if (selector.startsWith("main h2,")) return decoyNode ? [decoyNode] : [];
      return [];
    },
    querySelector() { return null; },
  };
  const context = vm.createContext({
    document,
    window,
    location: {
      get href() { return currentHref; },
      set href(value) { currentHref = value; },
      get hash() { return new URL(currentHref).hash; },
      get search() { return new URL(currentHref).search; },
      get pathname() { return new URL(currentHref).pathname; },
    },
    history: {
      state: null,
      replaceState(_state, _title, value) { currentHref = new URL(value, currentHref).href; },
    },
    localStorage: { setItem() {}, removeItem() {} },
    CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    URL,
    getComputedStyle(node) { return { display: rendered(node) ? "block" : "none" }; },
    matchMedia() { return { matches: true, addEventListener() {} }; },
    requestAnimationFrame(callback) { callback(); },
  });
  vm.runInContext(`${source}\nglobalThis.__site = { applyLevel, revealLinkedSection };`, context);
  return {
    context, inputs, labels, internalLink, sectionNodes, targetNodes, status, window,
    dispatchDocument(name, event) { for (const callback of documentListeners[name] || []) callback(event); },
    get href() { return currentHref; },
  };
}

test("depth changes keep the active chapter heading in the same viewport position", () => {
  const app = site({
    chapters: [
      { id: "setup", positions: { beginner: -2600, amateur: -2800 }, height: 700 },
      { id: "transfer", positions: { beginner: 2552, amateur: 1526 }, heading: "Transfer" },
    ],
    decoy: { positions: { beginner: 1300, amateur: 800 }, height: 4000 },
  });
  const transfer = app.sectionNodes.find((section) => section.id === "transfer");
  const before = transfer.getBoundingClientRect().top;

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(transfer.getBoundingClientRect().top, before);
  assert.match(app.href, /level=amateur#transfer$/);
  assert.equal(app.inputs[1].checked, true);
  assert.match(app.status.textContent, /Reading depth: Investigation/);
});

test("a radio click that scrolls the sticky control preserves the pre-focus chapter", () => {
  const app = site({
    chapters: [
      { id: "setup", positions: { beginner: -2600, amateur: -2800 }, height: 700 },
      { id: "transfer", positions: { beginner: 2552, amateur: 1526 }, heading: "Transfer" },
    ],
    decoy: { positions: { beginner: 1300, amateur: 800 }, height: 4000 },
  });
  const transfer = app.sectionNodes.find((section) => section.id === "transfer");
  const before = transfer.getBoundingClientRect().top;

  app.dispatchDocument("pointerdown", { target: app.labels[1] });
  app.window.scrollBy(0, -525);
  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(transfer.getBoundingClientRect().top, before);
});

test("keyboard depth changes preserve the chapter before focus or scroll adjustments", () => {
  const app = site({
    chapters: [
      { id: "setup", positions: { beginner: -2600, amateur: -2800 }, height: 700 },
      { id: "transfer", positions: { beginner: 2552, amateur: 1526 }, heading: "Transfer" },
    ],
  });
  const transfer = app.sectionNodes.find((section) => section.id === "transfer");
  const before = transfer.getBoundingClientRect().top;

  app.dispatchDocument("keydown", { target: app.inputs[0], key: "ArrowRight" });
  app.window.scrollBy(0, -525);
  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(transfer.getBoundingClientRect().top, before);
});

test("a visible linked chapter wins when a prior chapter tail covers the reading edge", () => {
  const app = site({
    href: "https://example.test/?level=beginner#transfer",
    scrollY: 2000,
    chapters: [
      { id: "setup", positions: { beginner: 1450, amateur: 1300 }, height: 700 },
      { id: "transfer", positions: { beginner: 2220, amateur: 1600 }, heading: "Transfer" },
    ],
  });
  const transfer = app.sectionNodes.find((section) => section.id === "transfer");
  assert.ok(transfer.getBoundingClientRect().top > 80);

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(transfer.getBoundingClientRect().top, 96);
  assert.match(app.href, /level=amateur#transfer$/);
});

test("a control activated after scrolling still respects the visible chapter route", () => {
  const app = site({
    href: "https://example.test/?level=beginner#transfer",
    scrollY: 2000,
    chapters: [
      { id: "setup", positions: { beginner: 1450, amateur: 1300 }, height: 700 },
      { id: "transfer", positions: { beginner: 2220, amateur: 1600 }, heading: "Transfer" },
    ],
  });

  app.dispatchDocument("pointerdown", { target: app.labels[1] });
  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(app.sectionNodes[1].getBoundingClientRect().top, 96);
});

test("an offscreen linked chapter does not replace the reading-edge anchor", () => {
  const app = site({
    href: "https://example.test/?level=beginner#transfer",
    scrollY: 2000,
    chapters: [
      { id: "setup", positions: { beginner: 1450, amateur: 1450 }, height: 700 },
      { id: "transfer", positions: { beginner: 3100, amateur: 3100 }, heading: "Transfer" },
    ],
  });
  const setup = app.sectionNodes.find((section) => section.id === "setup");
  const before = setup.getBoundingClientRect().top;
  assert.ok(app.sectionNodes[1].getBoundingClientRect().top >= app.window.innerHeight);

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(setup.getBoundingClientRect().top, before);
});

test("depth changes at the cover do not pull a distant chapter into view", () => {
  const app = site({
    scrollY: 0,
    chapters: [{ id: "setup", positions: { beginner: 1800, amateur: 1700 } }],
  });

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(app.window.scrollY, 0);
});
test("when a chapter disappears, the nearest visible next chapter becomes the shared link", () => {
  const app = site({
    level: "expert",
    href: "https://example.test/?level=expert#methods",
    scrollY: 1000,
    chapters: [
      { id: "limits", positions: { expert: 500, amateur: 500 }, height: 500, heading: "What this does not show" },
      { id: "methods", allowed: "e", positions: { expert: 1080, amateur: 1080 }, height: 500, heading: "Methods" },
      { id: "words", allowed: "a e", positions: { expert: 1750, amateur: 1750 }, height: 500, heading: "Words" },
    ],
  });

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.match(app.href, /level=amateur#words$/);
  assert.equal(app.sectionNodes[2].getBoundingClientRect().top, 96);
  assert.match(app.status.textContent, /Continued at Words/);
});

test("a deep link upgrades to the least reading depth that contains its target", () => {
  const app = site({
    href: "https://example.test/?level=beginner#methods",
    scrollY: 0,
    chapters: [
      { id: "methods", allowed: "e", positions: { beginner: 1000, expert: 1000 }, heading: "Methods" },
    ],
  });

  app.context.__site.revealLinkedSection();

  assert.match(app.href, /level=expert#methods$/);
  assert.equal(app.context.document.documentElement.dataset.level, "expert");
  assert.equal(app.sectionNodes[0].getBoundingClientRect().top, 96);
  assert.equal(app.inputs[2].checked, true);
  assert.match(app.status.textContent, /Reading depth: Research/);
});

test("a direct specialist link opens its closed details target before scrolling", () => {
  const app = site({
    href: "https://example.test/?level=beginner#transfer-definition",
    scrollY: 0,
    targets: [{
      id: "transfer-definition",
      allowed: "e",
      detail: true,
      positions: { beginner: 1000, expert: 1000 },
    }],
  });

  app.context.__site.revealLinkedSection();

  assert.match(app.href, /level=expert#transfer-definition$/);
  assert.equal(app.targetNodes[0].open, true);
  assert.equal(app.targetNodes[0].getBoundingClientRect().top, 96);
});

test("a link to a visible but closed technical note opens it before scrolling", () => {
  const app = site({
    level: "expert",
    href: "https://example.test/?level=expert#transfer-definition",
    scrollY: 0,
    targets: [{
      id: "transfer-definition",
      allowed: "e",
      detail: true,
      positions: { expert: 1000 },
    }],
  });

  app.context.__site.revealLinkedSection();

  assert.equal(app.targetNodes[0].open, true);
  assert.equal(app.targetNodes[0].getBoundingClientRect().top, 96);
});

test("explorer depth changes retain the selected event position and query state", () => {
  const app = site({
    href: "https://example.test/explorer.html?level=beginner#single/sol-21?record=instr&step=3",
    scrollY: 850,
    events: [
      { seq: 1, positions: { beginner: 1000, amateur: 800 }, visible: { beginner: false, amateur: false } },
      { seq: 2, positions: { beginner: 1200, amateur: 900 } },
    ],
  });
  const eventTop = () => 900 - app.window.scrollY;
  const before = 1200 - app.window.scrollY;

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(eventTop(), before);
  const url = new URL(app.href);
  assert.equal(url.searchParams.get("level"), "amateur");
  assert.equal(url.hash, "#single/sol-21?record=instr&step=3");
  const routeState = new URLSearchParams(url.hash.split("?")[1]);
  assert.equal(routeState.get("record"), "instr");
  assert.equal(routeState.get("step"), "3");
  const internal = new URL(app.internalLink.href);
  assert.equal(internal.searchParams.get("level"), "amateur");
  assert.equal(internal.hash, "#single/sol-21?record=instr&step=3");
});

test("depth changes above the explorer records do not pull a distant event into view", () => {
  const app = site({
    href: "https://example.test/explorer.html?level=beginner#single/sol-21?record=both&step=1",
    scrollY: 0,
    events: [{ index: 0, positions: { beginner: 1400, amateur: 1200 } }],
  });

  app.inputs[1].checked = true;
  app.inputs[1].listeners.change();

  assert.equal(app.window.scrollY, 0);
});
