# Capturing Hilt Protocol Data with a DSLogic Logic Analyzer

> Written from hands-on capture sessions with a DSLogic U2Basic + DSView. The
> procedure is validated on stock Galaxy's Edge blades.

## 1. What this is

A novice-friendly procedure for capturing the protocol bytes a Galaxy's Edge hilt sends
to its blade, using a DSLogic logic analyzer. The captures land in a community catalog
that blade firmware and other lightsaber projects can use to test hilt support
without owning every hilt.

**You don't need prior logic-analyzer experience.** The expensive part is the hilt; the
analyzer is ~$50; the rest is jumper wires and a benchtop power supply. If you can
follow a recipe, you can capture a hilt.

**Why contribute?** Disney releases new Legacy hilts faster than any one person can buy
them. Every contributor capture expands the catalog by one hilt that nobody else had to
buy. Builds compatibility for everyone, including yourself when you decide to add the
*next* hilt to your own collection.

---

## 2. Hardware you need

| Item | Notes |
|------|-------|
| DSLogic logic analyzer | Any model. This guide was written using a U2Basic (~$50). Plus / Pro models work the same way with more channels and deeper buffer. |
| DSLogic grabber probes | Comes with the analyzer. **Caveat:** the stock grabbers are flimsy — see Gotcha #1. |
| Galaxy's Edge hilt | Either a Savi's Workshop build hilt or a Legacy character hilt. |
| Blade plug | Attaches to the hilt's pogo connector and breaks out three wires: VCC, GND, DATA. The "blade plug Dupont breakout" sold by saber-mod vendors works well. |
| Test blade | **A stock GE blade is the default choice.** A custom Neopixel test blade is also useful for some captures — see Gotcha #3. |
| 10 kΩ resistor | **Required when capturing on a stock GE blade** — see Gotcha #2. Standard 1/4 W through-hole is fine. |
| Pogo / Dupont adapter for the test blade | So the blade plug's three leads can attach to the test blade's matching terminals. |
| Benchtop DC power supply | To power the test blade. ~3 V at a couple amps is fine for a stock blade. |
| USB cable | DSLogic to PC. |
| A PC running Windows / Mac / Linux | DSView is cross-platform. |

You do **not** need an oscilloscope, a microcontroller, or any soldering for the basic
capture procedure — though see Gotcha #1 for an optional solder upgrade.

---

## 3. Software

**DSView** by DreamSource Lab. Free download from the DreamSource Lab website. Tested
with v1.3.2 on Windows.

After install, plug in the DSLogic and verify DSView recognizes the device — top-left of
the toolbar should show "USB 2.0" and your model (e.g. "DSLogic U2Basic") in the
device dropdown. If not, check USB drivers per DSView's install guide.

---

## 4. Wiring

Three connections plus the analyzer's grabber probes. Take it slow — the ground
reference is the most failure-prone of the three.

```
              ┌───────────────────────────┐
              │   GE hilt (Savi's/Legacy) │
              │      pogo connector        │
              └─────────────┬─────────────┘
                            │ blade plug
                ┌───────────┼───────────┐
            ┌───┴─┐     ┌───┴─┐     ┌───┴─┐
            │ VCC │     │ GND │     │ DATA│  ← the three Dupont leads
            └─┬───┘     └─┬───┘     └─┬───┘
              │           │           │
              ├──[10kΩ]───┼───────────┤   ← pull-up: required for stock blades
              │           │           │     (between VCC and DATA, at the breakout)
              ▼           │           │
        ┌───────────┐     │           │
        │ test blade│     │           │
        │ VCC term. │     │           │
        └───────────┘     │           │
              ▲           │           │
              │           ▼           ▼
        ┌─────┴──────────────────────────┐
        │     test blade GND term. ──────┼──→ DSLogic GND clip
        │     test blade DATA term. ─────┼──→ DSLogic CH0 clip
        └────────────────────────────────┘
              ▲
              │
        Benchtop power supply
        (positive to test blade VCC, negative to test blade GND;
         tie negative to DSLogic GND for a common reference)
```

**Why the test blade is in the loop at all:** you want the hilt to think it's talking
to a real blade so it sends the same commands it normally would. The blade also lights
up, which is your eyes-on confirmation that the hilt is actually firing. If the blade
doesn't light up, fix that before worrying about the analyzer.

**Common ground is non-negotiable.** The DSLogic, the test blade, and the benchtop
supply must all share GND. Without that, your capture will look like noise even when
nothing's wrong with the data wire.

**The 10 kΩ pull-up is non-negotiable for stock blades.** With a stock GE blade as the
load, the DSLogic's input loading drops the idle DATA voltage low enough that the hilt
fires the disconnect sound the moment your grabber clips on. The pull-up holds the line
where the hilt expects it. See Gotcha #2 for the full diagnostic story; for now, just
wire it in.

---

## 5. DSView setup

### 5.1 Acquisition mode: Buffer (not Stream)

The DSLogic has two acquisition modes selected via the **Mode** dropdown in the toolbar:

- **Stream mode** — continuously streams samples to the PC. Has limited trigger
  support; trigger panel often shows everything grayed out.
- **Buffer mode** — captures samples to the device's onboard RAM, then dumps to PC
  when full. Hardware triggers work properly here.

For triggered captures (which is most of what you want), **use Buffer mode**.

### 5.2 Sample rate and duration

The hilt protocol's smallest feature is a ~500 µs HIGH gap between bits. Any sample rate
≥ 100 kHz oversamples that comfortably. Recommended:

| Capture type | Sample rate | Duration | Total samples |
|--------------|-------------|----------|---------------|
| Single-event ignite | 1 MHz | 2 s | 2,000,000 |
| Full activation cycle | 200 kHz | 10 s | 2,000,000 |
| Multi-clash session (future) | 200 kHz | 30 s | 6,000,000 |

The U2Basic's buffer is small — DSView will quietly cap your sample rate or duration
if you exceed it. If the dropdowns don't offer a value you'd expect (e.g. 250 kHz),
DSView is silently constraining the options to fit the buffer; pick the next available.

### 5.3 Trigger configuration

Most useful trigger: **CH0 falling edge**. The hilt's data line idles HIGH and pulls
LOW at the start of every command, so this fires at the first command edge.

To set:

1. Click **Trigger** in the toolbar. Trigger Setting panel opens.
2. Leave on **Simple Trigger**. (Advanced is for multi-condition stuff you don't need.)
3. In the **Stage 0** pattern row labeled `15 -------- 8 7 -------- 0`, the rightmost
   box is channel 0. Click that box until it cycles to **F** (Falling edge).
4. Leave the second pattern row all `X` (don't care).
5. Leave **Trigger Position** at 1% (gives ~99% post-trigger data; that's what you want).
6. Close the panel — settings persist until you change them.

### 5.4 Arming and capturing

- **Start** (green play button) — uses your trigger configuration. Device arms and
  waits for the trigger condition before recording. **This is what you want.**
- **Instant** (orange button) — ignores triggers, captures immediately. Useful for
  quick-and-dirty captures, but you'll get dead air at the start.

After clicking Start, DSView shows a "waiting for trigger" indicator. Press the hilt
button (or whatever fires the event you want to capture) and the capture runs.

---

### 5.5 Channel-map & colour calibration — DO THIS EVERY WIRING (required)

**The grabber-to-channel mapping is NOT fixed. It is a property of how the wires were
landed this session, not of the board.** The blade grabbers are not keyed or colour-coded,
so each time a blade is re-wired the DATA line, the three RGB **gate** channels, and the
four **segment** groups can all land on different logic-analyzer channels than last time.
A channel map carried forward from a previous capture is a guess, and a wrong colour is
the result.

**Why this is not optional (2026-08-22, Shin Hati).** Shin Hati's first capture nearly
filed as a *blue* hilt. Under the previous session's map (CH4=Red / CH5=Green / CH6=Blue)
its gates read blue-dominant (CH6 69%). The blade was visibly **orange**: that wiring had
swapped the gate lines to CH6=Red / CH4=Green / CH5=Blue, so 69% was RED, not blue. The
only thing that caught it was asking the operator what colour the blade actually lit.

**The calibration step, before you trust any colour or segment finding:**

1. **DATA** — derive by signature, never by label: it is the channel that idles HIGH and
   carries the framed command bursts. Confirm the decoder finds well-formed frames on it
   (`decode_dsl.py -c <ch>`).
2. **Colour / gates** — ignite the blade and **look at it**. Note the real colour. Run
   `analyze_timings.py` and read the three gate duties. Assign the gate channels so the
   duties match the colour you saw (red-dominant+green = orange; single strong channel =
   a primary; R+G = yellow; etc.). **If the gates and your eyes disagree, your eyes win
   and the channel labels are wrong — re-derive them, do not file the colour the numbers
   imply.** When in any doubt about the colour, ASK THE OPERATOR — that is the cheapest
   and most reliable ground truth.
3. **Segment groups** — the four segment channels can also reorder. Confirm the ignition
   wave fires hilt-end → tip in ascending time before trusting any ignition/extinguish
   wave-direction finding; if it doesn't, re-map the segment order for this wiring.
4. **Record the derived map in the capture notes / INDEX entry** (e.g. "this wiring:
   R=CH6, G=CH4, B=CH5") so the numbers in that capture are interpretable later. Do NOT
   assume the next capture inherits it.

---

## 6. Capture procedures

### 6.1 Single-event ignite capture

Captures one activation event cleanly. Best for catalog-quality reference data.

Settings:
- Mode: Buffer
- Sample rate: **1 MHz**
- Duration: **2 s**
- Trigger: CH0 falling edge

Steps:
1. Make sure the hilt is OFF (blade dark).
2. Click **Start** to arm.
3. Press the hilt's activation button.
4. Trigger fires, capture runs 2 s, auto-stops.
5. Save (see §7 for the naming convention).

What you'll see in the capture depends on the blade type:

- **Stock GE blade:** the hilt opens with an `0xA2`-family refresh frame (color in low
  nibble — `0xA2` for orange, `0xA7` for purple, etc.) and continues refreshing every
  ~740 ms. **There is no discrete ignite frame** — the blade's own MCU runs the
  ignition animation locally on receipt of any color-bearing command. See Gotcha #3.
- **Custom Neopixel test blade:** the hilt opens with a discrete `0x2X` ignite frame
  (e.g. `0x22` for orange) followed by `0xAX` refreshes. Useful when you want the
  ignite command on the wire for protocol research.

### 6.2 Full activation cycle capture

Captures activate → on-state → clash (optional) → deactivate in one trace. Great for
characterizing a hilt's natural behavior.

Settings:
- Mode: Buffer
- Sample rate: **200 kHz**
- Duration: **10 s**
- Trigger: CH0 falling edge

Steps:
1. Click **Start** to arm.
2. Press activate. Trigger fires. Blade ignites.
3. Wait ~2 seconds for the blade to fully ignite and stabilize.
4. *(Optional)* Tap the hilt body lightly to trigger a clash. **Don't whack it** —
   these have accelerometers, gentle is enough.
5. Wait another ~2 seconds.
6. Press deactivate.
7. Capture auto-stops at 10 s.
8. Save (see §7).

### 6.3 What to capture per hilt for the catalog

What makes a useful contribution, with a stock blade + the 10 kΩ pull-up:

- **One full-cycle reference per hilt** — ignite → steady state → optional clash →
  extinguish, 200 kHz, ~20 s.
- **One multi-event capture** per available color/character — same wiring, longer
  duration, deliberately fire several clashes during the on-state, so refresh +
  clash + extinguish bytes all land in one trace.

**About clashes:** hilts produce a variety of clash sounds, but the wire byte is
constant — every clash decodes to `0xC0`. Sound variety is generated locally by the
hilt MCU; nothing to differentiate on the wire. Multi-clash captures are still useful
for stress-testing the refresh cadence, just not for differentiating clash sub-types.

---

## 7. File naming convention

```
<hilt-type>-<variant>-<action>-<sample-rate>-<date>.dsl
```

| Field | Examples |
|-------|----------|
| `hilt-type` | `savis` (Savi's Workshop) · `legacy` (Legacy character hilt) |
| `variant` | For Savi's: the Kyber color (`white`, `red`, `orange`, `yellow`, `green`, `cyan`, `blue`, `purple`). For Legacy: the character name short form (`windu`, `kylo`, `rey`, `kestis`, `obiwan`, etc.) |
| `action` | `ignite`, `extinguish`, `clash`, `fullcycle`, `clashes` (multi-clash session) |
| `sample-rate` | `1MHz`, `200kHz`, `100kHz` etc. |
| `date` | ISO `YYYY-MM-DD` |

Examples:
- `savis-orange-ignite-1MHz-2026-05-06.dsl`
- `savis-purple-fullcycle-200kHz-2026-05-06.dsl`
- `legacy-windu-fullcycle-200kHz-2026-05-06.dsl`
- `legacy-kestis-clashes-200kHz-2026-05-07.dsl`

If you take multiple takes of the same capture (because the first was bad), append
`-take2`, `-take3`, etc.

### 7.1 Short names at capture time (the two-stage convention)

**Do not type the canonical name into DSView's save dialog.** It's long, it's
error-prone under bench conditions, and DSView's save dialog is buggy enough on its own
(§ Gotchas — the OK button vanishes; short names were the 2026-05-15 workaround).

**Stage 1 — capture.** Save with a short name into the session's capture folder:

```
<hilt>-<action>[-N].dsl
```

| Field | Values |
|-------|--------|
| `hilt` | Savi's: `s` + colour initial — `sb` blue, `sg` green, `sr` red, `so` orange, `sp` purple, `sy` yellow, `sw` white, `st` teal. Legacy: character short form — `rey`, `vader`, `kylo`, `maul`, `mace`, `obiwan`, `kanan`, `devon`, `sol`, `kestis`, `baylan` |
| `action` | `idle` · `ign` (ignite→burn→extinguish) · `clash` · `cyc` (full activation cycle) · `map` (channel-mapping test) |
| `N` | Take number for retries: `-2`, `-3`. Omit on the first take. |

Examples: `sb-idle.dsl` · `sb-ign.dsl` · `sg-ign.dsl` · `rey-ign.dsl` · `vader-clash-2.dsl`

**Stage 2 — filing.** Claude renames to the canonical §7 name when the capture is filed
into `captures/`. Renames work from the sandbox on the Storage mount (verified
2026-08-18); deletes do not, so nothing is ever removed — only renamed and moved.

**Why sample rate and date are dropped from the capture-time name.** Both are already
recorded more reliably elsewhere: the sample rate lives in the `.dsl` header, and the
date is the session folder. A filename rate label is not just redundant, it has
**already been wrong once** — `savis-teal-12ch-fullcycle-200kHz-2026-05-09.dsl` was
captured at a different rate than its name claims (Session Notes 2026-05-09). The
header is authoritative; a hand-typed label is a second source that can disagree with
it. Fewer hand-typed fields at the bench, fewer lies in the catalog.

---

## 8. Verifying your capture

The [`tools/decode_dsl.py`](../tools/decode_dsl.py) script decodes a `.dsl` file. Run
it before submitting — it dumps every command frame found and labels the byte values:

```bash
python3 tools/decode_dsl.py savis-orange-ignite-1MHz-2026-05-06.dsl
```

Sample output (this one captured on a custom Neopixel test blade, hence the
discrete `0x22` ignite frame — see Gotcha #3):

```
======================================================================
FILE: savis-orange-ignite-1MHz-2026-05-06.dsl
======================================================================
  Sample rate: 1000 kHz   Total samples: 2,000,896   Trigger@19,993
  LOW pulses found: 30
  Command frames decoded: 3

    #      t (ms)  preamb  byte  description
   1       +0.00       2   0x22  Savi Ignite Orange
   2     +670.31       2   0xA2  Savi Refresh (Orange)
   3    +1409.44       2   0xA2  Savi Refresh (Orange)
```

**What "good" looks like:**
- Decoded frames where you expect them. Ignite at t≈0, refreshes at ~740 ms intervals,
  extinguish ~5 s in (if it's a full-cycle).
- Total LOW pulses ≈ frames × 10 (each frame = 2 preambles + 8 data bits). If pulses
  vastly exceed frames × 10, you have noise or signal-integrity issues.
- Byte values match expected commands per the protocol model in
  [`CATALOG.md`](../CATALOG.md).

**What "bad" looks like:**
- Frame count < expected events (some events failed to decode → corruption).
- Garbled byte values (e.g., a Savi's hilt clash decoding as `0xD3` instead of
  `0xC0`-range — that's bit corruption from probe contact or current-draw issues).
- Pulse widths that don't fall into clean clusters around 1.2 ms / 2.4 ms / 16 ms.

If your verify run looks bad, see Gotchas (§10) before trying again.

---

## 9. Submitting your capture

You don't have to decode, arrange your channels a particular way, or open a pull
request. Fill out the [`SUBMISSION-TEMPLATE`](../SUBMISSION-TEMPLATE.md) — your channel
map, what you saw on the blade, and which hilt — and post it with your raw capture file
in the `#hilt-submissions` Discord thread. The maintainer normalizes it, decodes it,
adds it to the catalog, and credits you in [`CONTRIBUTORS.md`](../CONTRIBUTORS.md).
Running the decoder on your capture first (§8) is welcome but not required.

---

## 10. Gotchas

A growing list of things that bit us during the early capture sessions.

### Gotcha #1: Flimsy DSLogic grabber probes lose contact when cables move

**Symptom.** Capture looks weird — lots of short sub-millisecond pulses where there
should be clean ~16 ms preambles. Decoder reports far more raw LOW pulses than command
frames.

**Cause.** The stock DSLogic grabbers are spring-loaded clips designed for IC pins.
They're fine when stationary, but any cable movement can break the contact mid-capture.
A flaky contact during a LOW pulse looks like the line bouncing back HIGH briefly —
which the analyzer dutifully records as multiple short pulses.

**Fix.**
- Don't move cables between captures. Once everything's clipped, leave it alone.
- For a permanent fix, solder short wire stubs to the GND and DATA tap points on your
  blade plug or test blade. A 5-minute mod that pays off forever. **If you're
  soldering anyway, this is a good time to also solder the 10 kΩ pull-up resistor
  in place — see Gotcha #2.**
- Or use solid pin-header probe tips (sold separately) instead of the stock grabbers.

### Gotcha #2: Stock GE blades need a 10 kΩ pull-up between DATA and VCC

**Symptom.** The instant you clip the DSLogic GND grabber on, the hilt fires its
disconnect / blade-removed sound. The hilt drops out of "blade present" state and
won't drive the data line. DSView sits waiting for a trigger that never fires, or
you get a few junk pulses and silence.

**Cause.** A stock GE blade's only pull-up on the DATA line is the hilt MCU's
internal pull-up (~50–100 kΩ — weak). When the DSLogic's input loading is added in
parallel, idle voltage on DATA collapses from ~2.8 V to ~1.2 V — below the hilt's
"blade present" threshold. The hilt thinks the blade got pulled out and shuts down.

**Fix.** Wire a **10 kΩ resistor between the DATA Dupont and the VCC Dupont** at the
breakout (see the wiring diagram in §4). This pulls idle DATA up to ~3.0 V — solidly
above the hilt's threshold — without preventing the hilt from driving the line LOW for
command bits.

**Why 10 kΩ specifically:**

| Pull-up value | Result |
|---------------|--------|
| None | Hilt fires disconnect sound at probe attach. No usable data. |
| 22 kΩ | Protocol decodes, but the line is too floaty against analyzer loading — ~142× more LOW pulses recorded than there are real edges. Frames are decodable but the noise count is misleading. |
| **10 kΩ** | **Clean signal. LOW-pulse count matches frame count × ~10 as expected.** |

**Note on Neopixel test blades.** This issue does NOT happen with custom Neopixel
test blades — they typically have a stronger discrete pull-up that overcomes the
analyzer's input loading on its own. The pull-up is specifically a stock-blade
gotcha. If you solder the resistor in line for stock-blade work, you can leave it in
for Neopixel-blade work too — it doesn't hurt anything.

### Gotcha #3: Choosing a test blade — stock vs Neopixel tradeoffs

**TL;DR.** Use a stock GE blade by default. Use a custom Neopixel test blade only
when you specifically need the discrete `0x2X` ignite frame on the wire.

**The tradeoff.**

| Property | Stock GE blade | Custom Neopixel test blade |
|----------|----------------|---------------------------|
| Capture quality on transient events (ignite, clash, extinguish) | Clean | Bit corruption — current spikes during LED events disturb the ground reference |
| Real-world animation behavior | Yes (this is what shipping hilts drive) | Different — drives a single addressable LED strip across the whole blade |
| Discrete `0x2X` ignite frame on the wire | **Absent** — blade's own MCU runs ignition animation internally on receipt of any color-bearing command | **Present** — hilt sends an explicit ignite command |
| 10 kΩ pull-up required (Gotcha #2) | **Yes** | No (Neopixel blade has its own pull-up) |
| Disney-canonical electrical load | Yes | No |

**Neopixel-blade transient corruption symptom.** Refresh-stream commands decode
cleanly, but ignite, clash, and extinguish commands show bit corruption — byte
values that *should* be clean (e.g. `0xC0` clash) decode as nearby bit-flipped values
(e.g. `0xD3`). Caused by the Neopixel blade's 60+ WS2812B LEDs drawing far more
current at ignition than the hilt was designed to drive; the current spike sags the
local voltage and disturbs the ground reference during exactly those events.

**For catalog captures**, use a stock GE blade. Your captures will be repeatable and
match what other contributors get.

**For protocol-completeness research** where you need to see the discrete `0x2X`
ignite frame, capture on a Neopixel blade and accept the noise on transient events.
Better still: capture both ways and cross-reference.

### Gotcha #4: Use fresh / LiPo batteries on Savi's hilts

**Symptom.** Older or low batteries cause similar transient-event corruption to
Gotcha #3.

**Cause.** Voltage sag during high-current LED events.

**Fix.** Fresh AAs or a quality LiPo pack. (Helps. Doesn't fully eliminate
Neopixel-blade issues — Gotcha #3 is the bigger lever.)

### Gotcha #5: Buffer mode is required for triggers

**Symptom.** Trigger Setting panel opens, but every field is grayed out. Clicking
boxes does nothing.

**Cause.** You're in Stream mode. Stream mode disables hardware triggers.

**Fix.** Switch to Buffer mode in the Mode dropdown. The trigger panel un-grays.

### Gotcha #6: Sample-rate and duration options are quantized

**Symptom.** You want 250 kHz but only see 100/200/500 kHz; you want 8 s but only see
5/10/20 s.

**Cause.** DSView constrains the available options based on the device's buffer size.
The U2Basic in particular has a small buffer; high rates × long durations don't fit.

**Fix.** Pick the next-available option. Drop sample rate before duration when forced
to choose — for this protocol, anything ≥ 100 kHz is fine.

### Gotcha #7: Where's t=0 in the zoom view?

**Symptom.** You zoom in to see a burst, but the time labels start at +99.90 ms, not 0.

**Cause.** The default zoom-in view doesn't pan to the trigger automatically; you're
seeing whatever section your scroll position landed on.

**Fix.** Scroll left until you see the red `T` trigger marker at the start. The trigger
fires at sample position `trigger pos` from the header (visible in DSView's status), but
absolute time on the timeline is measured from the beginning of the capture buffer, not
the trigger.

### Gotcha #8: First-activation noise on brand-new hilts

Noise on a brand-new hilt's very first activation is almost always the missing 10 kΩ
pull-up — see Gotcha #2. With the pull-up in place the captures come out clean. If you
hit first-activation noise, check the pull-up before anything else.

---

## Appendix A: What the protocol looks like on the wire

For reference / sanity-checking, here's what one Savi's command frame looks like
captured at 1 MHz. (Captured from real traces: hilts send 2 preambles per command.)

```
   ┌─────┐         ┌─────┐         ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
HIGH│     └─────────┘     └─────────┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └────
    ↑                ↑                ↑                              ↑
    └─ ~16.4 ms ─────┴─ ~16.4 ms ─────┴── 8 data bits (~1-2.5 ms each, MSB first)
       LOW preamble   LOW preamble        ~500 µs HIGH between bits

Bit = 1: ~1.2 ms LOW
Bit = 0: ~2.4 ms LOW
Anything > 3.75 ms LOW: preamble (reset)
```

**Measured timing (across Savi's captures on a stock blade):**

| Element | Width |
|---------|-------|
| Preamble LOW | ~17,900 µs |
| Bit-0 LOW | ~2,500 µs |
| Bit-1 LOW | ~1,250 µs |
| Inter-bit HIGH gap | ~500 µs |
| Inter-frame idle (between commands) | ~740 ms during steady-state on |

---

