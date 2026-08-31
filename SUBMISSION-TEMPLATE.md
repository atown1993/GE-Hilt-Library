# Submission Template — capturing a hilt for the Library

You don't have to decode anything or match our probe order. Capture your hilt
best-effort, then **tell us your channel map** and what you saw. We take it from
there: decode, normalize, add it to the catalog, and credit you.

Copy this block, fill it in, and post it in the `#hilt-submissions` Discord
thread with your capture file attached. Fields you can't answer — leave as `?`.

---

## ⚠️ READ FIRST — stock blades only
Capture with a **stock Galaxy's Edge blade** (the one that came with the hilt, or
another genuine GE blade) as the load. **Do not** submit captures taken with an
upgraded / aftermarket / Neopixel / custom-firmware blade — those drive the
segments and gates completely differently and their signaling won't match the
stock hilt behavior this catalog documents. A custom blade also injects current
noise onto the data line during ignite/clash/extinguish and corrupts the very
bytes we're trying to read.

- Stock GE blade → **yes, submit.**
- Upgraded/custom/Neopixel blade → **not for this catalog** (interesting, but a
  different beast — mention it in the thread and we can talk).

The **hilt** can be any real Savi's Workshop or Legacy hilt. It's the **blade**
that must be stock.

---

## 1. Who to credit
- **Credit as:** (name / handle / "anonymous")

## 2. The hilt
- **Hilt:** (character or model, e.g. "Legacy Ahsoka", "Savi's Workshop")
- **Kyber / color installed:** (and, if Savi's, the color you captured in)
- **Box set / SKU / release, if known:**
- **Approx. purchase or manufacture date, if known:** (firmware revisions vary by
  release — this helps)

## 3. The analyzer
- **Make / model:** (Saleae Logic, DSLogic, generic 8-channel, etc.)
- **Software used:**
- **File format attached:** (`.dsl`, `.sal`, `.vcd`, `.csv`, raw binary…)
- **Sample rate:**
- **Channels captured:** (how many, e.g. 8)

## 4. The channel map  ← the important one
For every channel you recorded, tell us what was physically on the probe. Use the
roles below; "unsure" is fine — a labeled "unsure" is still useful.

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
  you know the order; if not, "segment, position unknown")
- `RED` / `GREEN` / `BLUE` — the per-color channel gate
- `GND` / `VREF` — ground or a reference/rail
- `CLK` / `other` / `unsure`

**Segment line vs FET gate — tell us which you tapped.** If you probed the
transistor **gates** (low-impedance, driven) rather than the **segment-enable
lines** directly, say so. They read differently and it changes how we interpret
PWM duty. This one detail saves us a lot of second-guessing.

## 5. What you SAW  ← helps us map signals to behavior
The electrical trace and the visible blade behavior corroborate each other, so
describe what the blade actually did on camera or by eye:

- **Blade color / mode shown during the capture:**
- **On ignite — what did you see?** (color; the light-up **wave direction** —
  hilt→tip or tip→hilt; roughly how long the wipe took; any flicker/pulsing once
  lit)
- **On clash (if captured):** (flash color, how many, how it recovered)
- **On extinguish:** (retract direction, fade time, any color shift on the way
  out)
- **Anything that didn't match what you expected to see:**

## 6. What actions are in the file
- **Actions captured:** (ignite / steady burn / clash(es) / extinguish /
  color-change / idle — check all that apply)

## 7. Anything else
- Rig notes, pull-up/pull-down resistors added, anything odd, or things you
  specifically wanted to test.

---

### Why the map + what-you-saw, not a fixed probe order?
Different analyzers number and arrange channels differently, and we'd rather you
capture the way that's easy for you than force a layout. Your channel map plus
what you saw on the blade is the Rosetta Stone: with them, decoding is
deterministic on our end. Without them we'd be guessing which channel is which —
and our own testing shows that guess is wrong more often than not on
multi-channel blade captures.
