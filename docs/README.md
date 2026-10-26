# Website

The GitHub Pages site is self-contained in this folder. It has no build step, package install, analytics,
external fonts or runtime dependencies. Serve it over HTTP for the episode data to load:

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:4173/`. The reading choice is stored locally and can be shared as
`?level=beginner`, `?level=amateur` or `?level=expert`.

The folder can be moved to another static host or mounted below a path; runtime assets and navigation are
relative. The canonical/social metadata currently targets `responseiv.github.io/transfer-permission-arrangement`.
Update those URLs when moving to a permanent domain.

For GitHub Pages, the intended source is branch `site`, folder `/docs`. This work does not change repository
settings, push the branch or publish the site. Obtain the owner's approval before those actions.

See [DESIGN.md](DESIGN.md) for the reading journeys and design decisions. Verify with:

```sh
python3 -m unittest discover -s tests -p 'test_site*.py' -q
node --check docs/assets/site.js
node --check docs/assets/explorer.js
```

The `assets/report.pdf` copy is the submitted paper and is checked byte for byte. The opening is a condensed
real episode, also checked against the source. Episode data and generated figures retain their existing
generators, `scripts/site_data.py` and `scripts/site_figures.py`.
