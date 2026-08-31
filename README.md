# GE-Hilt-Library

A firsthand, community-built catalog of **Galaxy's Edge lightsaber hilt
captures** — raw logic-analyzer recordings of how these hilts actually behave,
electrically, so builders don't have to start from zero or own every hilt to
work with one.

Everything here was measured directly from a physical hilt. Every claim is
backed by a capture file in this repo. See [`NOTICE`](NOTICE) for the full
provenance statement.

## What's captured

Galaxy's Edge hilts drive their blades over a wire protocol, and the blade
itself lights up as a set of addressable segments. This catalog covers two
capture targets:

1. **Hilt → blade protocol (present today).** The single-wire, pulse-width
   command stream the hilt sends: ignite, refresh, clash, extinguish, and the
   color/mode encoding. This is the bulk of the current catalog — Savi's
   Workshop hilts across all eight kyber colors, plus a growing set of Legacy
   character hilts.

2. **Blade-internal signals (a target we want, not yet populated).** A
   multi-channel view *inside* the blade drive: the individual blade
   segment-enable lines and the RGB channel gates alongside the data line.
   This is what lets a builder reproduce the exact light-up/fade wave. We have
   the capture rig and the analysis tooling for it; we're actively looking for
   contributors and captures here.

## Repository layout

```
captures/
  savis/<color>/       Savi's Workshop hilts, by kyber color
  legacy/<hilt>/       Legacy character hilts, by character
  validation/          rig-validation / channel-mapping reference captures
NOTICE                 provenance statement (all data firsthand)
CONTRIBUTORS.md        everyone credited for a firsthand capture
LICENSE                MIT — covers the tools/code
LICENSE-DATA           CC BY 4.0 — covers the captures and measurements
```

Capture files are **DSView `.dsl`** format (DreamSource Lab's native format — a
ZIP archive holding a header plus bit-packed per-channel sample data). Open them
in the free [DSView](https://www.dreamsourcelab.com/) application for visual
inspection. **Timings reference:** `data/hilt-timings.csv` is the per-hilt/per-color table of protocol bytes and measured timings — the source of truth. A browsable, sortable version renders from it under `docs/` (GitHub Pages) with a one-click CSV download. A protocol decoder and the full findings write-up are being finalized and will land as the clean-room build completes.

## Contributing — you don't need to decode anything

The whole point is to catalog hilts no one person owns. The bar to contribute is
deliberately low:

- You capture your hilt best-effort with whatever logic analyzer you have.
- You **don't** have to arrange your probes a specific way, match our channel
  order, or decode the protocol. Send the raw file plus a few lines about what
  you probed and what analyzer you used.
- The maintainer normalizes it — identifies which channel is the data line,
  which are segments, which are gates — decodes it, adds it to the catalog, and
  credits you in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

A step-by-step submission guide (`CONTRIBUTING.md` / `SUBMIT.md`) and the Discord
submission thread are set up at public launch. Until then, this repo is the
maintainer's working catalog.

## Licensing

- **Captures and measurements:** [CC BY 4.0](LICENSE-DATA) — reuse freely with
  attribution.
- **Tools and code:** [MIT](LICENSE).

## Not affiliated with Disney / Lucasfilm

Galaxy's Edge, Savi's Workshop, and the named hilts are Disney / Lucasfilm
products. This is an independent, non-commercial fan research project, not
affiliated with or endorsed by either. Names identify which physical product a
capture came from — nothing more.
