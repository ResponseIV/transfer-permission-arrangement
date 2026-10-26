# Website

The GitHub Pages site is self-contained in this folder. It has no build step, package install, analytics,
external fonts or runtime dependencies. Serve it over HTTP for the episode data to load:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:4173/`. The reading choice is stored locally and can be shared as
`?level=beginner`, `?level=amateur` or `?level=expert`.

The article is a case notebook: a refused read, a matched instruction pair, an arranged exchange,
its scripted control, and an overwritten leak. Each exhibit separates the available record from
the supported finding and the alternative it leaves open. The research depth adds a source map.

The evidence desk starts with an arranged/scripted comparison. A sticky band switches between comparing two
episodes and stepping through one, picks the case, and sets which records you hold. The reveal is opt-in;
observer and experiment-fixture records stay separately labelled. A copied URL keeps
the record, selected event and reveal state, for example:
`explorer.html?level=expert#single/sol-21?record=full&step=3&reveal=false`.

The folder can be moved to another static host or mounted below a path; runtime assets and navigation are
relative. The canonical/social metadata currently targets `responseiv.github.io/transfer-permission-arrangement`.
Update those URLs when moving to a permanent domain.

For GitHub Pages, the intended source is branch `site`, folder `/docs`. This work does not change repository
settings, push the branch or publish the site. Obtain the owner's approval before those actions.

See [DESIGN.md](DESIGN.md) for the reading journeys and design decisions. Verify with:

```sh
python3 -m unittest discover -s tests -p 'test_site*.py' -q
node --test tests/site-reading-state.test.cjs tests/site-explorer.test.cjs
node --check docs/assets/site.js
node --check docs/assets/explorer.js
```

The `assets/report.pdf` copy is the submitted paper and is checked byte for byte. The opening and case exhibits
are checked against real source episodes. Episode data and generated figures retain their existing
generators, `scripts/site_data.py` and `scripts/site_figures.py`.

The [design system](DESIGN-SYSTEM.md) defines type roles, spacing and component relationships.
Its primitives and semantic roles live in `assets/tokens.css`, shared composition in `assets/style.css`,
and desk composition in `assets/explorer.css`. Both pages load the same tokens first.
The original audit and the revision’s verification record are in `audit/site-2026-10-26/` at repository root.
