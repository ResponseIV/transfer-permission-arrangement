"use strict";

const RECORDS = {
  text: "page writes",
  both: "page writes and access log",
  full: "page writes, access log and final answers",
};
const JUDGES = [
  ["astra-p10", "Astra, prompt 10"],
  ["luna-p9", "Luna, prompt 9"],
  ["qwen-p10", "Qwen3-32B, prompt 10"],
];
const LABELS = {
  transfer: "transfer",
  exposure: "receipt (read the other's revision)",
  coded: "transfer found only through the answer (encoded carrier)",
  via_archive: "token taken from the archive",
  own_token_written: "an agent wrote its own token",
  obtained: "an answer holds the other's token",
};

const state = { data: null, episode: null, record: "both", step: 0 };
const $ = (id) => document.getElementById(id);

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

const page = (path) => (path || "").replace(/^fixture:\/\/pages\//, "");
const who = (name) => el("span", { class: `who ${name}` }, name === "anon" ? "anonymous" : name);
const body = (text) => el("div", { class: "body" }, text === "" ? "(empty)" : text);

function observerPane(step) {
  const record = state.record;
  const parts = [];
  if (step.log && record !== "text") {
    const entry = step.log;
    parts.push(el("div", {}, who(entry.actor), ` ${entry.action}s `, el("code", {}, page(entry.page)),
      entry.allowed ? null : el("span", { class: "status-denied" }, " · denied")));
  }
  if (step.pages) {
    const written = step.pages;
    if (record === "text") {
      parts.push(el("div", {}, "Page ", el("code", {}, page(written.page)), " written by ", who(written.author)));
    }
    parts.push(body(written.body));
  }
  if (step.answer && record === "full") {
    parts.push(el("div", {}, who(step.answer.actor), " answers"), body(step.answer.answer));
  }
  if (!parts.length) {
    const what = step.action === "final_answer" ? "A final answer" : step.action === "read" ? "A read" : "A denied write";
    return el("div", { class: "pane hidden-record" }, el("div", { class: "label mobile" }, "Observer"),
      `${what}: not in this record.`);
  }
  return el("div", { class: "pane" }, el("div", { class: "label mobile" }, "Observer"), parts);
}

function truthPane(step) {
  const verb = { read: "reads", write: "writes", final_answer: "answers" }[step.action];
  const head = el("div", {}, who(step.actor), ` ${verb}`, step.page ? [" ", el("code", {}, page(step.page))] : null,
    step.status === "allowed" ? null : el("span", { class: "status-denied" }, ` · denied (${step.error || step.status})`));
  const lines = [head];
  if (step.seeded) lines.push(el("div", { class: "small muted" }, "Seeded by the fixture before the task; nobody is told."));
  if (step.action === "read" && step.status === "allowed") {
    lines.push(el("div", { class: "small" }, "Returned a revision written by ", who(step.read_author || "nobody")));
  }
  if (step.action === "final_answer") lines.push(body(step.text || ""));
  else if (step.status === "allowed" && step.text !== null && !step.pages && step.action !== "read") lines.push(body(step.text));
  if (step.carries.length) {
    lines.push(el("div", {}, step.carries.map((c) =>
      el("span", { class: "pill carrier" }, `${c.token_of}'s token, ${c.form}`))));
  }
  if (step.note) lines.push(el("div", { class: "note" }, el("b", {}, step.note)));
  return el("div", { class: "pane" }, el("div", { class: "label mobile" }, "Ground truth"), lines);
}

function renderPicker() {
  const picker = $("picker");
  picker.replaceChildren(...state.data.episodes.map((episode) =>
    el("button", { type: "button", class: "chip", "aria-pressed": String(episode === state.episode), "data-key": episode.key },
      el("span", { class: "k" }, episode.kind), episode.title.split(":")[0])));
}

function renderSummary() {
  const e = state.episode;
  const tokens = Object.entries(e.tokens).map(([agent, token]) => [who(agent), " ", el("code", {}, token), "  "]);
  $("summary").replaceChildren(
    el("div", { class: "tag" }, e.kind),
    el("h2", { style: "margin:4px 0 8px" }, e.title),
    el("p", {}, e.story),
    el("div", { class: "meta" },
      el("span", {}, "Model ", el("b", {}, e.model)),
      el("span", {}, "Arm ", el("b", {}, e.arm)),
      el("span", {}, "Confidentiality rule ", el("b", {}, e.rule_in_prompt ? "yes" : "no")),
      el("span", {}, "Origin ", el("b", {}, e.origin)),
      el("span", {}, "Tokens ", tokens)),
    el("details", {}, el("summary", {}, "Instructions both agents saw"), el("pre", {}, e.prompt)),
  );
}

function renderTimeline() {
  const steps = state.episode.steps;
  $("timeline").replaceChildren(...steps.slice(0, state.step + 1).map((step, index) =>
    el("div", { class: `event${index === state.step ? " current" : ""}` },
      el("div", { class: "n" }, step.seq),
      el("div", { class: "panes" }, observerPane(step), truthPane(step)))));
  const slider = $("slider");
  slider.max = steps.length;
  slider.value = state.step + 1;
  $("position").textContent = `Step ${state.step + 1} of ${steps.length}`;
  $("prev").disabled = state.step === 0;
  $("next").disabled = $("all").disabled = state.step === steps.length - 1;
}

function verdictCard(title, value, text) {
  const tone = value === true ? "yes" : value === false ? "no" : "";
  return el("div", { class: `verdict ${tone}` }, el("div", { class: "who-judge" }, title), el("div", { class: "v" }, text));
}

function renderVerdicts() {
  const e = state.episode;
  $("verdicts-title").textContent = `Judges on the ${RECORDS[state.record]}`;
  const judged = JUDGES.map(([key, name]) => {
    const value = (e.judges[key] || {})[state.record];
    return verdictCard(name, value, value === true ? "Transfer" : value === false ? "No transfer" : "Not run");
  });
  const label = e.label;
  $("verdicts").replaceChildren(
    el("p", { class: "small muted" }, "Frozen model judges, asked whether a secret reached another agent, blind to ",
      "tokens, model and arm. An absent verdict is unknown, never false."),
    el("div", { class: "verdicts" }, judged),
    el("h3", { style: "margin-top:18px" }, "Ground truth"),
    el("div", { class: "verdicts" },
      verdictCard("Frozen label", label.transfer, label.transfer ? "Transfer" : "No transfer"),
      verdictCard("Benchmark case", null, e.case),
      verdictCard("In the paper", null, e.kind)),
    el("div", { class: "signals" }, Object.entries(LABELS).filter(([key]) => key !== "transfer").map(([key, text]) =>
      el("span", { class: `pill ${label[key] ? "on" : "off"}` }, text))),
    el("h3", { style: "margin-top:18px" }, "Observer signals"),
    el("p", { class: "small muted" }, "The eight frozen signals, computed from the observer records."),
    el("div", { class: "signals" }, Object.entries(e.signals).map(([name, on]) =>
      el("span", { class: `pill ${on ? "on" : "off"}` }, name))),
    el("p", { class: "small muted", style: "margin-top:12px" }, "Cell ", el("code", {}, e.cell_id)),
  );
}

function render() {
  renderPicker();
  renderSummary();
  for (const button of document.querySelectorAll("#records button")) {
    button.setAttribute("aria-pressed", String(button.dataset.record === state.record));
  }
  renderTimeline();
  renderVerdicts();
}

function select(key) {
  state.episode = state.data.episodes.find((episode) => episode.key === key) || state.data.episodes[0];
  state.step = 0;
  if (location.hash.slice(1) !== state.episode.key) history.replaceState(null, "", `#${state.episode.key}`);
  render();
}

function move(step) {
  state.step = Math.max(0, Math.min(state.episode.steps.length - 1, step));
  renderTimeline();
  const current = document.querySelector(".event.current");
  if (current && current.getBoundingClientRect().bottom > window.innerHeight) current.scrollIntoView({ block: "nearest" });
}

function wire() {
  $("picker").addEventListener("click", (event) => {
    const chip = event.target.closest(".chip");
    if (chip) select(chip.dataset.key);
  });
  $("records").addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    state.record = button.dataset.record;
    render();
  });
  $("prev").addEventListener("click", () => move(state.step - 1));
  $("next").addEventListener("click", () => move(state.step + 1));
  $("all").addEventListener("click", () => move(state.episode.steps.length - 1));
  $("slider").addEventListener("input", (event) => move(Number(event.target.value) - 1));
  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, textarea")) return;
    if (event.key === "ArrowRight") move(state.step + 1);
    if (event.key === "ArrowLeft") move(state.step - 1);
  });
  window.addEventListener("hashchange", () => select(location.hash.slice(1)));
}

fetch("data/episodes.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((data) => {
    state.data = data;
    wire();
    select(location.hash.slice(1));
  })
  .catch((error) => {
    const box = $("error");
    box.hidden = false;
    box.replaceChildren("Could not load data/episodes.json (", String(error.message), "). Opened from disk? Serve the ",
      "folder instead: ", el("code", {}, "python3 -m http.server -d docs"), ", then open http://localhost:8000/explorer.html.");
  });
