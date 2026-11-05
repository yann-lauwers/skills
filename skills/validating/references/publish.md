# Publishing

- `run.md` on disk stays the deliverable; the published page is its artifact.
- Write `run.html` beside `run.md`, carrying the same content in the house style, per /house-style ; its `<title>` is `<ID> · <slice> · validation run <key> · <VERDICT>`, `<ID>` the slice's ticket id, none → dropped, and each capture it links is `<scenario>/<capture>`, relative to the run directory.
- Copy them into `<scratchpad>/<slice>-<key>/`, `run.html` renamed `<slice>-<key>.html`, every capture at its path relative to the run directory, and publish that page with its captures.
- Each run publishes a new artifact; never redeploy over another run's `url`.
- A capture the Artifact tool's limits refuse → link its path on disk and name it as not published.
