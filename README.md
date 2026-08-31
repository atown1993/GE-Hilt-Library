# GE-Hilt-Library

A firsthand, community-built catalog of **Galaxy's Edge lightsaber hilt
captures** — raw logic-analyzer recordings of how these hilts actually behave,
electrically, so builders don't have to start from zero or own every hilt to
work with one.

Everything here was measured directly from a physical hilt with a stock Galaxy's
Edge blade. Every claim is backed by a capture file in this repo. See
[`NOTICE`](NOTICE) for the full provenance statement.

## What's captured

Galaxy's Edge hilts drive their blades over a wire protocol, and the blade itself
lights up as a set of addressable segments. This catalog covers two capture
targets:

1. **Hilt → blade protocol (present today).** The single-wire, pulse-width
   command stream the hilt sends: ignite, refresh, clash, extinguish, and the
   color/mode encoding. This is the bulk of the current catalog — Savi's Workshop
   hilts across all eight kyber colors, plus a growing set of Legacy character
   hilts.

2. **Blade-internal signals (a target we want, more captures welcome).** A
   multi-channel view *inside* the blade drive — the individual segment-enable
   lines and the RGB channel gates alongside the data line — which is what lets a
   builder reproduce the exact light-up/fade wave.

## Start here

- **The protocol, in full:** [`CATALOG.md`](CATALOG.md) — wire format, byte
  structure, color rendering, cadence, clashes, and per-hilt behavior.
- **The per-hilt data:** [`data/hilt-timings.csv`](data/hilt-timings.csv) — bytes
  and measured timings, one row per hilt/color. Browsable and sortable under
  [`docs/`](docs/) (GitHub Pages) with a one-click CSV download.
- **The captures:** [`captures/INDEX.md`](captures/INDEX.md) lists all of them.

## Repository layout

```
CATALOG.md              the protocol catalog — how hilts drive blades, in full
captures/
  savis/<color>/        Savi's Workshop hilts, by kyber color
  legacy/<hilt>/        Legacy character hilts, by character
  validation/           rig-validation / channel-mapping captures
  INDEX.md              generated index of every capture
data/hilt-timings.csv   per-hilt/per-color bytes + measured timings (source of truth)
docs/                   browsable, sortable Pages table + CSV download
tools/                  decode_dsl.py (protocol decoder) + analyze_timings.py
scripts/                regenerate docs/ and the capture index
guides/                 Blade-Types.md · DSLogic-Setup.md (capture procedure)
SUBMISSION-TEMPLATE.md  what to send when you contribute a capture
NOTICE                  provenance statement (all data firsthand)
CONTRIBUTORS.md         everyone credited for a firsthand capture
LICENSE / LICENSE-DATA  MIT (code) / CC0 1.0 (captures + measurements)
```

Capture files are **DSView `.dsl`** format (DreamSource Lab's native format — a
ZIP archive holding a header plus bit-packed per-channel sample data). Open them
in the free [DSView](https://www.dreamsourcelab.com/) app, or decode them with
[`tools/decode_dsl.py`](tools/decode_dsl.py) (Python 3, no dependencies).

## Contributing — you don't need to decode anything

The whole point is to catalog hilts no one person owns, and the bar is
deliberately low:

- Capture your hilt best-effort with **a stock GE blade** and whatever logic
  analyzer you have. You **don't** have to arrange your probes a specific way,
  match a channel order, or decode anything.
- Fill out [`SUBMISSION-TEMPLATE.md`](SUBMISSION-TEMPLATE.md) — your channel map,
  what you saw on the blade, and which hilt — and post it with your raw capture
  file in the Discord submission thread.
- The maintainer normalizes it, decodes it, adds it to the catalog, and credits
  you in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

New to logic-analyzer capture? [`guides/DSLogic-Setup.md`](guides/DSLogic-Setup.md)
is a step-by-step procedure written for someone with no prior experience. Until
public launch, this repo is the maintainer's working catalog.

## Licensing

- **Captures and measurements:** [CC0 1.0](LICENSE-DATA) — public domain, use
  freely, no attribution required.
- **Tools and code:** [MIT](LICENSE).

## Not affiliated with Disney / Lucasfilm

Galaxy's Edge, Savi's Workshop, and the named hilts are Disney / Lucasfilm
products. This is an independent, non-commercial fan research project, not
affiliated with or endorsed by either. Names identify which physical product a
capture came from — nothing more.
