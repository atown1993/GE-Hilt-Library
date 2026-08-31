# Submission Template — capturing a hilt for the Library

You don't have to decode anything or match our probe order. Capture your hilt
best-effort, then **tell us your channel map** and a few details below. We take
it from there: decode, normalize, add it to the catalog, and credit you.

Copy this block, fill it in, and post it in the `#hilt-submissions` Discord
thread with your capture file attached. Fields you can't answer — leave as
`?`. The channel map is the one part we really need; it saves us from having to
reverse-engineer which probe was on what.

---

## 1. Who to credit
- **Credit as:** (name / handle / "anonymous")

## 2. The hilt
- **Hilt:** (character or model, e.g. "Legacy Ahsoka", "Savi's Workshop")
- **Kyber / color installed:** (and, if Savi's, the color you captured in)
- **Box set / SKU / release, if known:**
- **Approx. purchase or manufacture date, if known:** (firmware revisions vary
  by release — this helps)

## 3. The analyzer
- **Make / model:** (Saleae Logic, DSLogic, generic 8-channel, etc.)
- **Software used:**
- **File format attached:** (`.dsl`, `.sal`, `.vcd`, `.csv`, raw binary…)
- **Sample rate:**
- **Channels captured:** (how many, e.g. 8)

## 4. The channel map  ← the important one
For every channel you recorded, tell us what was physically on the probe. Use
the roles below; add "unsure" freely — a labeled "unsure" is still useful.

| Channel | What was on it (role) | Probe point / notes |
|---|---|---|
| CH0 | | |
| CH1 | | |
| CH2 | | |
| CH3 | | |
| CH4 | | |
| CH5 | | |
| CH6 | | |
| CH7 | | |
| (add rows if more) | | |

**Roles to choose from** (pick the closest; "unsure" is fine):
- `DATA` — the hilt→blade data line (the single command wire)
- `SEG1`…`SEG4` — blade segment-enable lines (SEG1 = hilt end → SEG4 = tip, if
  you know the order; if not, just say "segment, position unknown")
- `RED` / `GREEN` / `BLUE` — the per-color channel gate (FET gate or LED drive)
- `GND` / `VREF` — ground or a reference/rail
- `CLK` / `other` / `unsure`

If you tapped the FET **gates** vs the **segment lines** directly, say which —
they read differently and it changes how we interpret PWM duty.

## 5. What the saber was doing during the capture
- **Actions captured:** (ignite / steady burn / clash(es) / extinguish /
  color-change / idle — check all that apply)
- **Color / mode shown on the blade during capture:** (needed to line up the
  RGB PWM duty with the color you saw)
- **Blade used:** (stock Galaxy's Edge blade / custom Neopixel / bare LED rig —
  this matters; custom blades can inject noise on the data line)

## 6. Anything else
- Rig notes, pull-up/pull-down resistors added, anything that looked odd, or
  things you specifically wanted to test.

---

### Why the map, not a fixed probe order?
Different analyzers number and arrange channels differently, and we'd rather you
capture the way that's easy for you than force a layout. Your map is the
Rosetta Stone: with it, decoding is deterministic on our end. Without it we'd be
guessing which channel is which — and our own testing shows that guess is wrong
more often than not on multi-channel blade captures.
