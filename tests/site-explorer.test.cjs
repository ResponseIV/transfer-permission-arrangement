const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "docs/assets/explorer.js"), "utf8");
const data = JSON.parse(fs.readFileSync(path.join(root, "docs/data/episodes.json"), "utf8"));
const html = fs.readFileSync(path.join(root, "docs/explorer.html"), "utf8");
const config = source.match(/const PAIR_COPY = (\{[\s\S]*?\n\});/);
assert.ok(config, "comparison exhibit map is present as a data-only object");
const exhibits = JSON.parse(JSON.stringify(vm.runInNewContext(`(${config[1]})`)));

test("every comparison landmark points to a real event in its named source case", () => {
  assert.deepEqual(Object.keys(exhibits).sort(), data.compare.map((pair) => pair.key).sort());
  for (const pair of data.compare) {
    const map = exhibits[pair.key];
    const left = data.episodes.find((episode) => episode.key === pair.left);
    const right = data.episodes.find((episode) => episode.key === pair.right);
    assert.ok(map.landmarks.length > 0, `${pair.key} has selected landmarks`);
    for (const landmark of map.landmarks) {
      for (const [side, episode] of [["left", left], ["right", right]]) {
        const refs = landmark[side];
        assert.ok(Array.isArray(refs) && refs.length > 0, `${pair.key}: ${landmark.title} selects ${side} source events`);
        for (const seq of refs) assert.ok(episode.steps.some((step) => step.seq === seq), `${pair.key}: ${episode.key} has event ${seq}`);
      }
    }
  }
});

test("arranged/scripted landmarks preserve their actual offer, read, reply and answer events", () => {
  const pair = data.compare.find((item) => item.key === "arranged-scripted");
  const left = data.episodes.find((episode) => episode.key === pair.left);
  const right = data.episodes.find((episode) => episode.key === pair.right);
  const rows = Object.fromEntries(exhibits[pair.key].landmarks.map((item) => [item.title, item]));
  assert.deepEqual(rows["Offer written"].left, [3]);
  assert.deepEqual(rows["Offer written"].right, [1]);
  assert.deepEqual(rows["Offer read"].left, [4]);
  assert.deepEqual(rows["Offer read"].right, [2]);
  assert.deepEqual(rows["Reply written"].left, [6]);
  assert.deepEqual(rows["Reply written"].right, [4]);
  assert.deepEqual(rows["Reply read"].left, [7]);
  assert.deepEqual(rows["Reply read"].right, [5]);
  assert.deepEqual(rows["Answers submitted"].left, [8, 9]);
  assert.deepEqual(rows["Answers submitted"].right, [9, 10]);
  for (const [episode, rowsToCheck] of [[left, exhibits[pair.key].landmarks.map((row) => row.left)], [right, exhibits[pair.key].landmarks.map((row) => row.right)]]) {
    const events = rowsToCheck.flat().map((seq) => episode.steps.find((step) => step.seq === seq));
    assert.ok(events.every(Boolean));
    assert.ok(events.some((step) => step.pages?.body), `${episode.key} includes a page-write event`);
  }
});

test("observer and fixture records remain separately named, and answer stays opt-in", () => {
  assert.match(source, /Observer record/);
  assert.match(source, /Experiment fixture · complete record/);
  assert.match(source, /renderCompareAnswer/);
  assert.match(source, /aria-expanded/);
  assert.match(html, /id="nojs-evidence"/);
  assert.match(html, /id="compare-inspector"/);
  assert.match(html, /id="single-inspector"/);
});

test("legacy case fragments and complete reader state are encoded by the router", () => {
  assert.match(source, /Both #case and #single\/case are preserved/);
  assert.match(source, /params\.set\("record"/);
  assert.match(source, /params\.set\("step"/);
  assert.match(source, /params\.set\("reveal"/);
  assert.match(source, /history\[push \? "pushState" : "replaceState"\]/);
});
