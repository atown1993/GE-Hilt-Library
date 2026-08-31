# GE Hilt → Blade Protocol Catalog

A firsthand catalog of how Galaxy's Edge lightsaber hilts drive their blades,
built entirely from captures taken on the bench with stock Galaxy's Edge blades.
Everything here is something measured directly; every behavior described is backed
by a capture file in this repository.

This documents the **hilt → blade wire protocol** and the stock blade's response to
it. It does not cover the hilt's internal workings (accelerometer, RFID reader,
audio) — only what crosses the wire to the blade and what the blade does with it.

> **Capture basis:** Savi's Workshop hilts across all 8 kyber colors, plus a
> growing set of Legacy character hilts (Cal Kestis, Mace Windu, Kanan, Devon,
> both Maul staff halves, Obi-Wan, Qui-Gon, Rey, Vader, Shin Hati, Baylan Skoll,
> Master Sol, Kylo Ren, and the "Arresting the Chancellor" LE set — Kit Fisto,
> Saesee Tiin, Agen Kolar). Per-hilt bytes and timings live in
> [`data/hilt-timings.csv`](data/hilt-timings.csv).

---

## 1. Wire format

One half-duplex data line. The hilt drives, the blade listens. Idle is HIGH;
command bursts pull LOW.

Every command is a single 8-bit byte preceded by two synchronization preambles:

```
   ┌─────┐         ┌─────┐         ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
HIGH│     └─────────┘     └─────────┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └────
    └─ preamble ───┴── preamble ────┴── 8 data bits, MSB first ──┘
```

| Element | Width (measured) | Notes |
|---------|------------------|-------|
| Preamble LOW | ~17,900 µs | |
| Bit-`1` LOW | ~1,250 µs | |
| Bit-`0` LOW | ~2,500 µs | |
| Inter-bit HIGH gap | ~500 µs | |
| Inter-frame idle | ~739 ms (Savi) / ~1000 ms (Legacy) | during steady-state on (§6) |

Bit-`0` and bit-`1` have *inverted* duty from the usual pulse convention — `0` is
the **longer** LOW pulse, `1` is the **shorter** LOW pulse. A LOW longer than
~3.75 ms is a preamble (resync), not a bit. The decoder in
[`tools/decode_dsl.py`](tools/decode_dsl.py) reads this directly from a capture.

---

## 2. Byte structure: high nibble = action, low nibble = color

Every wire byte breaks into two nibbles:

- **High nibble** — the action (ignite, refresh, clash, extinguish, etc.)
- **Low nibble** — the color (or a sub-index, depending on the action)

The color is fixed once per session: the hilt reads the kyber's RFID at boot, maps
it to a color index, and that nibble rides on **every byte** sent to the blade for
the rest of the session. Because the color is repeated on every refresh, the
protocol is robust to brief signal interruptions — any single refresh frame fully
re-establishes color state.

### Action high-nibble table (observed)

| High nibble | Family | Action | Notes |
|-------------|--------|--------|-------|
| `0x2X` | Savi's | Ignite | See §4 — whether a discrete ignite byte appears depends on the capture setup. |
| `0x3X` | Legacy | Ignite | Observed on Legacy hilts (e.g. Mace `0x33`, Maul `0x38`). |
| `0x4X` | Savi's | Extinguish | e.g. `0x47` (purple). |
| `0x5X` | Legacy | Extinguish | e.g. `0x55` (Cal Kestis white). |
| `0x6X` | — | Red flicker (low band) | Kylo Ren — a streamed animation *level* (§10). |
| `0x7X` | — | Red flicker (high band) | Kylo Ren — a streamed animation *level* (§10). |
| `0x8X` | Savi's | Post-off | `0x80` trailing extinguish in some configurations (§12.1). |
| `0xAX` | Savi's | Refresh / set color | The workhorse byte, sent every ~739 ms during steady on. Also emitted by some Legacy hilts (§8). |
| `0xBX` | Legacy | Refresh / set color | Legacy workhorse, ~1000 ms cadence. Extends past idx 7 with character-specific variants. |
| `0xCX` | — | Clash | **Always `0xC0`** across every captured clash (§7). |
| `0xDX` | Legacy | Clash (rare) | Seen once as `0xDF` inside a long Maul clash burst; clash is otherwise always `0xC0` (§7). |
| `0xEX` | Savi's | Disable / blank | Used as a transient blanking byte during Cal Kestis color changes (§8). |

A Legacy-family disable byte (`0xFX`) has **not** been observed on the wire in any
capture here.

### Color low-nibble table — Savi's family (`0xAX`)

All 8 kyber indexes empirically captured on a Savi's Workshop hilt with matched
crystals. Stock blades render only 6 of the 8 (§5).

| Low nibble | Protocol color | Stock blade renders as |
|------------|----------------|------------------------|
| `0x0` | White | White |
| `0x1` | Red | Red |
| `0x2` | Orange | **Yellow** (folded) |
| `0x3` | Yellow | Yellow |
| `0x4` | Green | Green |
| `0x5` | Cyan / Teal | **Blue** (folded) |
| `0x6` | Blue | Blue |
| `0x7` | Purple | Purple |

The 8 kyber-color indexes (0–7) are complete, but the Savi *opcode family* itself is
open-ended: it also carries higher, character-specific indexes on Legacy-character
hilts that emit it — for example **Rey Skywalker = Savi-family idx 11 (`0xAB`)**,
rendering yellow. Rey's yellow at idx 11 is a different index than Savi kyber yellow
(`0xA3` = idx 3): a per-character slot, not a raw color code.

### Color low-nibble table — Legacy family (`0xBX`)

Observed Legacy mappings. The Legacy table extends past idx 0–7 into
character-specific variants, so the same visual color may map to different bytes on
different hilts.

| Code | Visual color | Hilt(s) |
|------|--------------|---------|
| `0xB1` | Red (with `0x6X`/`0x7X` flicker) | Kylo Ren |
| `0xB2` | Blue | Kanan, Devon, Agen Kolar |
| `0xB3` | Purple | Mace Windu |
| `0xB4` | Red (Cal Kestis variant) | Cal Kestis |
| `0xB5` | White | Cal Kestis |
| `0xB6` | Green | Qui-Gon Jinn, Kit Fisto, Saesee Tiin |
| `0xB7` | Red (clean, no flicker) | Darth Vader |
| `0xB8` | "Blood red" (deeper crimson) | Maul (both staff halves) |
| `0xB9` | Blue | Obi-Wan Kenobi (2026 release) |
| `0xBA` | Orange | Shin Hati, Baylan Skoll |

Key points established from these captures:

- **Some codes are shared across hilts** — `0xB2` is blue on Kanan, Devon, and Agen
  Kolar. Disney reuses some Legacy codes across characters.
- **Some codes are character-specific shades** — Cal Kestis red (`0xB4`) and Maul
  "blood red" (`0xB8`) both read as red but use different bytes; Maul's is a
  noticeably deeper crimson.
- **The Legacy table is not a parallel of the Savi table.** Savi idx 4 is green;
  Legacy idx 4 (`0xB4`) is Cal Kestis red. The two families keep independent color
  tables.
- **Multiple indexes render red**, each per-character: idx 1 (Kylo, flickering), idx
  4 (Cal Kestis), idx 7 (Vader, clean), idx 8 (Maul blood-red). "Red" is a family of
  slots, not one code.

**Character identity is invisible on the wire — the protocol is color-keyed.**
Controlled captures confirm this on both families: two different kyber tags of the
same color produce byte-identical, timing-identical output (a Savi crystal
reprogrammed between captures; and separately, Qui-Gon vs Yoda, two green tags). On
the Legacy side, Kit Fisto and Saesee Tiin (both idx-6 green) are byte- and
timing-identical to Qui-Gon; Agen Kolar (idx-2 blue) matches Kanan and Devon. The
hilt derives a single color index from the crystal and drives the blade with that
index's bytes; the character is rendered locally as sound and never reaches the
blade line. **A capture is complete per color slot, regardless of which character is
installed.**

---

## 3. The blade runs its own animation

Each GE blade has its own MCU. The blade is not a passive LED string — it runs its
own animation logic in response to the hilt's terse commands. It can ignite, fade,
clash, and extinguish locally; the hilt sends short bytes and the blade fills in the
animation. This is why so much behavior below (the ignition wave, the fade, the
render model) is a **blade** property that holds across every hilt.

---

## 4. Ignite bytes and the stock-blade ignition

When a stock blade's MCU is in "off" state and receives any color-bearing command
(a refresh in the `0xAX`/`0xBX` family), it runs its **local ignition animation**
and ends at the specified color — no separate ignite command strictly required to
light up.

Whether a discrete ignite byte (`0x2X`/`0x3X`) *precedes* that refresh depends on
the capture setup rather than the hilt or the color. On the current bench rig with a
stock RGB blade, every hilt emits a discrete ignite byte before the refresh (Qui-Gon
`0x36`, Rey `0x2B`, Vader `0x37`, the full Legacy fleet, all seven Savi crystals, Cal
Kestis `0x26`); other setups show only the refresh. Either way the blade lights
correctly.

**For blade-firmware authors:** don't rely on a discrete ignite command to trigger
your ignition animation. Detect the off→on transition from the *first* color-bearing
command (an `0xAX`/`0xBX` refresh) instead.

---

## 5. Stock-blade color rendering — the 6-color fold and the gate PWM model

Stock GE blades render only **6 of the 8** Savi colors, even though the hilt sends
the full byte for any kyber: **orange folds to yellow, cyan/teal folds to blue.**
The wire byte is correct; the fold is in the stock blade's rendering.

This is proven at the electrical level. Tapping the blade's three RGB transistor
gates directly and measuring the PWM duty each color drives:

**PWM carrier is ~5917–5952 Hz** on a stock RGB blade (confirmed ~5,956 Hz at 10 MHz
sampling). Brightness is set by duty cycle, in three discrete tiers:

| Kyber | Hilt byte | Green gate | Red gate | Blue gate | Stock-blade visible |
|-------|-----------|-----------|----------|-----------|---------------------|
| Red    | `0xA1` | off    | 99.4% | off    | Red |
| Green  | `0xA4` | 99.4% | off    | off    | Green |
| Blue   | `0xA6` | off    | off    | 99.7% | Blue |
| Yellow | `0xA3` | 59.8% | 59.8% | off    | Yellow |
| **Orange** | `0xA2` | 59.5% | 59.5% | off | **YELLOW (folded)** |
| Purple | `0xA7` | off    | 59.8% | 60.1% | Purple |
| White  | `0xA0` | 44.0% | 43.5% | 44.0% | White |
| **Teal** | `0xA5` | off | off | 99.7% | **BLUE (folded)** |

**Three-tier brightness ladder** — each active primary is driven at one of three
duty levels depending on how many primaries are lit:

| Active primaries | Duty per primary | Total brightness budget |
|-----------------|-----------------|-------------------------|
| 1 (single primary) | ~99.4% | 99% |
| 2 (yellow, purple, folded-orange) | ~60% | 120% |
| 3 (white) | ~44% | 132% |

This looks like current/brightness balancing: pure white shouldn't blow out relative to a single primary, so per-gate duty drops as colors stack.

**The fold happens at the gate, not by remapping the byte.** `0xA2` (orange) and
`0xA3` (yellow) drive R+G at the same ~60% duty — byte-for-byte identical gate
signals — which is why both look yellow. `0xA5` (teal) and `0xA6` (blue) both drive
only the B gate at ~99.7%. The blade receives distinct codes; it just drives the
same physical signal for each folded pair.

These are the canonical **render targets** for any blade aiming to match stock
rendering: 99% for a single primary, 60% for two-color mixes, 44% for white.

---

## 6. Refresh cadence

In steady-state on, hilts send refresh frames at a regular cadence, and the interval
tracks the **physical hilt platform**, not the opcode family:

- **Savi's Workshop hilts:** ~706–739 ms (condition-dependent; battery state appears
  to shift it within this band).
- **Legacy character hilts:** ~1005–1013 ms across current-generation hilts.

Rey is the tell: she emits the *Savi* opcode family (`0xAB`) yet refreshes at
~1005 ms like the Legacy hilts, because she is a Legacy-platform hilt. Some hilts
hold an extremely tight clock — Vader measures 1012.21 ms with a standard deviation
of 0.11 ms across 40 intervals, the tightest in the set, usable as a
hilt-generation fingerprint.

The cadence is **not disturbed by clashes** — clash bytes are inserted into the
stream when the accelerometer fires, and the next scheduled refresh still arrives on
its clock. Blade firmware can use the refresh interval as a liveness heartbeat: two
missed refreshes (~1.5 s for Savi, ~2 s for Legacy) means the link is probably
broken.

Two exceptions:
- **Box-set Baylan Skoll** refreshes at ~2113 ms — roughly 2.09× the normal Legacy
  rate. Baylan and Shin Hati share an index, color, and ignite/extinguish timing but
  run different refresh firmware (Shin ~1013 ms, box-set Baylan ~2113 ms).
- **Kylo Ren** has no periodic refresh at all — it streams flicker bytes instead
  (§10). Do not apply a cadence fallback to Kylo.

---

## 7. Clashes

**The clash byte is always `0xC0`**, regardless of hilt family, across every hilt
captured with clash events. (A single `0xDF` was seen once, mid-burst, inside a long
Maul cycling-clash sequence — the `0xDX` family exists but is rare; `0xC0` is the
practical rule.)

What varies by hilt is the **count and pattern** of `0xC0` bytes per physical strike
— and that is set by the hilt's firmware, not by strike strength or the blade. The
visible flash count matches the byte count:

| Hilt | Clash pattern |
|------|---------------|
| Savi (all) | 1 byte per strike |
| Devon, Kanan, Mace, Obi-Wan, Cal Kestis, Vader, Kit Fisto, Saesee Tiin, Agen Kolar | 1:1 single |
| **Maul staff LONG halves** | **Cycling (1, 3, 1, 4), period 4, repeats indefinitely** — phase does not reset per ignition |
| **Maul staff SHORT half** | 1:1 single — same bytes as the longs, different clash firmware |
| **Qui-Gon Jinn** | Random/intermittent double (~30–48%, session-variable), doubles ~135–190 ms apart |
| **Rey Skywalker** | Mostly single; a "long clash" is a sustained burst of ~15 `0xC0` at ~128 ms over ~1.8 s, triggered by rapid impulse accumulation |

So there is no single "Legacy clash protocol" — each hilt may carry its own clash
firmware, and cycling vs 1:1 can even coexist within one product (the Maul staff:
longs cycle, short is 1:1). Most of the fleet is 1:1; the Maul long halves are the
only cycling firmware seen. In a multi-byte Maul burst, the first two bytes sit ~65 ms
apart (a tight pair) with later bytes spaced wider.

**Clash-flash color is a delayed gate pulse, not a brightness flash.** About 75 ms
*after* the `0xC0`, one or more otherwise-off gates rise for ~35–40 ms, then fall —
a hue shift while the segments stay fully on. On the Legacy hilts this is a fixed
**Red+Green full / Blue off** pulse regardless of the blade's steady color:
electrically yellow, but through the diffuser at full intensity the eye reads it as
**white**. On the Savi crystals the added color is per-crystal-slot specific (a
firmware lookup per index), which gives a useful discriminator: **teal (idx 5) shows
no clash flash at all, while blue (idx 6) flashes full white** — the first behavior
that tells teal and blue apart on a stock blade, where they otherwise both render as
plain blue.

Clash **audio** variation is produced locally by the hilt's MCU; only the
visual-flash count crosses the wire.

Maul carries one extra quirk: **after a clash it switches to a fast ~127 ms refresh
cadence** for several seconds (vs its normal ~1000 ms) to drive a more elaborate
post-clash recovery animation, then settles back.

---

## 8. Cal Kestis — the color-changing hilt

Cal Kestis is a color-changer. Holding the change button ~5 s drives a brief
white-flash, then the blade settles on the next color in a 6-color cycle.

**On the wire, a color change is a fixed 6-byte sequence, ~581 ms total:**

```
[old-color refresh] → [white-trigger byte] → [4× disable byte (0xE0/0xE1)] → [new-color refresh]
```

The four disable bytes are spaced ~130 ms apart. The white-trigger byte alternates
between transitions in a strict `0xB5 / 0xA0 / 0xB5 / 0xA0 …` flip-flop, independent
of which color the hilt is going from or to — a stateful toggle in the hilt firmware.
Sampling the gates through a transition shows the white flash is a
dim-bright-dim-bright pulse (each duty change lands with a disable byte), and the
**segments stay fully HIGH throughout** — the flash is rendered purely at the gate
level, not by cutting segment power.

**The cycle is 6 of the 8 Savi colors, in a fixed hand-picked order:**

| Position | Color | Byte |
|----------|-------|------|
| 1 | Blue | `0xA6` |
| 2 | Green | `0xA4` |
| 3 | Purple | `0xA7` |
| 4 | Red | `0xB4` |
| 5 | Yellow | `0xA3` |
| 6 | White | `0xB5` |

Orange and cyan are excluded — exactly the two colors a stock blade can't render
(§5), so the cycle matches the stock-displayable set.

**Cal Kestis is a hybrid hilt: it uses the Savi byte family for 4 colors and the
Legacy family for 2** (red `0xB4` and white `0xB5` are Legacy; blue/green/purple/
yellow are Savi), all at Legacy ~1000 ms cadence. For blade firmware, handle both
`0xAX` and `0xBX` refresh families and treat them identically — don't assume a hilt
sticks to one family for a whole session.

Note the disable bytes: firmware that has no handler for them will drop them and jump
straight from the white refresh to the new color, producing a single white blink
instead of the intended flash pattern — worth handling if you're matching stock
behavior.

---

## 9. Master Sol — two families on one hilt

Master Sol is a color-changer with a physical selector (up = blue, middle = off,
down = red). It drives **two different protocol families depending on the color:**

| Mode | Ignite | Refresh | Extinguish | Family |
|------|--------|---------|------------|--------|
| Blue | `0x26` | `0xA6` | `0x46` | Savi (idx 6) |
| Red  | `0x34` | `0xB4` | `0x54` | Legacy (idx 4) |

Measured timings: blue 172 / 442 / 258 ms, red 172 / 748 / 258 ms
(ignition / ext-delay / extinguish). Ignition and extinguish-wave durations are
identical across both colors, consistent with the blade-firmware ignition constant
(§11).

**Mid-burn color change is a bare cross-family re-ignite.** Flicking the selector
past the middle during a burn fires the new family's *ignite* byte with **no
extinguish** and no white-flash sequence — and the blade **re-runs its full ignition
wave** in the new color (segments collapse ~60 ms after the byte and re-sweep
base→tip on the same staggered schedule as a cold ignition, with the gate swap
synchronized to the collapse). A Sol color change is therefore a visible
re-ignition, not an instant swap or a cross-fade — replay the ignition wave if you're
emulating it.

---

## 10. Kylo Ren — the flicker protocol

Kylo's steady burn is not the periodic refresh every other Legacy hilt uses. Instead
the hilt **streams a continuous sweep of flicker-level bytes** to animate the
unstable-blade wobble in real time:

- `0x7X` is the high-flicker band, `0x6X` the low-flicker band.
- The low nibble (idx 0–F) is an animation *level*, swept smoothly up and down.
- Step cadence is **~126 ms** (roughly 8× faster than a normal Legacy refresh).
- Only one `0xB1` (red refresh) appears, immediately before extinguish — the flicker
  stream replaces the refresh cadence during burn.

A clean 42-second burn pins the full model: a **triangle sweep between `0x69` and
`0x7F`**, step cadence 125.8 ms with essentially zero jitter, a near-uniform level
histogram — and one oddity, **`0x7D` is never emitted** (its neighbors `0x7C`/`0x7E`
appear normally). Unexplained; likely a firmware skip.

**The flicker is segment-brightness modulation, not blanking.** The red color gate
holds a constant ~100% the whole burn; all the visible flicker lives in the
**segment-enable PWM duty**, which swings ~60–100%. No disable/blank byte appears
anywhere in the stream — a Kylo blade that looks like it flickers off is being deeply
dimmed, not commanded off. This is a distinct blade-render mode from steady
single-color rendering.

---

## 11. Electrical architecture — segments, gates, and the ignition wave

Beyond the single DATA line, a stock blade exposes two more signal groups worth
capturing: **four blade-segment enable lines** (LED groups, hilt-end to tip) and
**three RGB transistor gates** (one per color channel). Capturing DATA + 4 segments +
3 gates together is what produced the render model in §5 and the timing model below.

**Gate PWM.** Each active color gate drives PWM at ~5917–5952 Hz on a stock RGB
blade. (A modified-firmware blade — such as the LE set's keyed orange blade, which
unlocks orange — drives a faster ~15.7 kHz gate carrier; the carrier is a blade-
firmware property.) When inactive, a gate idles LOW; brief simultaneous pulses on all
inactive gates at ignition/extinguish are supply-rail bounce from LED current spikes,
not real signals.

**Segments.** During steady burn the segment enables are held constant HIGH (not
time-multiplexed) — color comes entirely from which RGB gate is firing. The tip-end
segment (group 4) is electrically anomalous: instead of a clean enable it shows a
mix of short spikes and longer pulses with more total edges than the other groups,
regardless of color. Most likely end-of-chain termination behavior or a physically
different tip PCB.

**Idle default.** With no hilt commands at all, the blade firmware boots into a
default state with all three RGB gates already PWM'd at ~36.5% duty (segments off, so
no visible light) — the gates sit ready to deliver color before any protocol arrives.

**The ignition wave.** Relative to the first hilt byte:

| Event | Timing |
|-------|--------|
| First gate activity (color drive starts) | ~17–18 ms |
| First segment enable (group 1, hilt end) | ~80–85 ms |
| Last segment enable (group 4, tip) | ~165–245 ms |
| Post-extinguish gate fade-out | ~1.0–1.2 s |

The segment spread is the **visible ignition wave** propagating hilt-end to tip
across the four groups (~165 ms total) — what you see at the bench as the blade
lighting from the bottom up. **The ignition-wave duration is a blade-firmware
constant: 172–174 ms** across every clean ignition on the stock RGB blade, a ~2 ms
window over many measurements, independent of which hilt sends the byte (~86 ms per
segment × 4). It can be hard-coded; no per-character calibration is needed. The
constant is per-blade-firmware, though — the LE set's keyed orange blade shows a
~180 ms wave with reversed segment order, so each blade model hard-codes its own.

The ~1 s of post-extinguish gate activity is the **visible fade-out** — the blade
ramps brightness down gradually rather than cutting off when the hilt sends the
extinguish byte.

---

## 12. Per-hilt data and cross-hilt firmware traits

### 12.1 Timing data

Per-hilt, per-color bytes and timings — ignite / refresh / extinguish bytes,
ignition, extinguish-delay, extinguish, and refresh cadence — are in
[`data/hilt-timings.csv`](data/hilt-timings.csv) (also browsable and sortable via the
[`docs/`](docs/) page). Notes on the timings established from the data:

- **Ignition wave** is the 172–174 ms blade constant (§11).
- **Extinguish-delay** (the audio-tail period the blade stays lit after the
  extinguish byte) is a **per-crystal-slot** property, not a per-hilt one: on a
  single Savi hilt it spans 55 ms (orange) to 992 ms (red) across crystals. The
  yellow-rendering slots (Savi orange 55, Savi/Cal/Rey yellow ~40) extinguish almost
  immediately; the red-family slots run long (Savi red 992, Cal red 752, Mauls ~830,
  Vader 742).
- Cal Kestis timings were taken on alkaline batteries; treat those absolute numbers
  as carrying a small battery-state caveat. Cal Kestis purple can show an extended
  ignition wave (~301 ms vs the 172 ms baseline) only after heavy bench activity —
  most likely battery-voltage sag on the highest-current color; the cold-boot value
  is the normal ~175 ms.
- Mace's extinguish fade is stochastic (~450–540 ms run to run on the same unit), so
  a single-capture value there is false precision.

### 12.2 Cross-hilt firmware traits

- **Kanan's extinguish quirk.** Kanan runs steady on Legacy `0xB2` (blue) but
  extinguishes with two *Savi*-family bytes — `0xA5` (cyan) at the next scheduled
  refresh slot, then `0x45` extinguish ~65 ms later. On a stock blade `0xA5` folds to
  blue (§5), so there's no visible color shift; the apparent purpose is a longer
  fade-out animation, matching Kanan's noticeably longer extinguish audio. This breaks
  the otherwise-universal "extinguish family matches the active refresh family" rule —
  Agen Kolar (same idx-2 blue wire identity) and Devon both extinguish cleanly with
  Legacy `0x52`, so the swap is a Kanan-specific trait.
- **Baylan blade-detection lockout.** The Baylan hilt refuses to drive the protocol
  at all when paired with a non-original blade — the wire stays essentially silent.
  With its own keyed blade it runs normally. This is hilt-side blade detection gating
  protocol output; the other Legacy hilts captured all accept a compatible test blade.
  Blade keying is per-set (the LE set's orange blade unlocks both Baylan and Shin).
- **LE-set / box-set firmware splits.** Within a single product, two hilts can run
  different firmware: the Maul staff (long halves cycle clashes, short is 1:1) and the
  Baylan/Shin pair (different refresh cadence) both show this. By contrast, the
  "Arresting the Chancellor" box-set Mace is electrically identical to the standard
  clamshell Mace — no split. So a repackage may or may not change firmware; capture
  and check rather than assume.

---

## Not affiliated with Disney / Lucasfilm

Galaxy's Edge, Savi's Workshop, and the named hilts are products of The Walt Disney
Company / Lucasfilm. This is an independent, non-commercial fan research project, not
affiliated with or endorsed by either. Hilt and character names identify which
physical product a capture came from.
