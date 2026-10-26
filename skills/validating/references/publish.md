# Publishing

- `report.md` on disk stays the deliverable; the published page is its artifact.
- Write `report.html` beside `report.md`, carrying the same content in the house style, per /house-style ; its `<title>` is `<ID> · <slice> · validation run <key> · <VERDICT>`, `<ID>` the slice's ticket id, none → dropped, and each capture it links is `<scenario>/<capture>`, relative to the run directory.
- Copy them into `<scratchpad>/<slice>-<key>/`, `report.html` renamed `<slice>-<key>.html`, every capture at its path relative to the run directory; publish that page with the Artifact tool, `root` that directory and every capture in `files` at its relative path.
- Each run publishes a new artifact; never redeploy over another run's `url`.
- A capture the Artifact tool's limits refuse → link its path on disk and name it as not published.
- Quote only the addresses the publish reported.
