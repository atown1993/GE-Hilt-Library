# Savi's Workshop Gen2 — Gen2 hilt + the new addressable blade (session 2)

Captured 2026-10-11 on the home bench. The blade was opened; its hilt-connector ring was
bypassed with leads so the hilt (via a Savi's test connector and a breadboard, 10 kΩ pull-up
data → V+) drives the blade's control board directly while the analyzer taps both sides.

Channel map (fixed by soldered leads, same for every file here):

| CH | Signal |
|---|---|
| CH0 | **strip IN1** — the LED strip's data input (the blade MCU's output net) |
| CH1 | **hilt DATA** — the hilt's data wire into the blade (ring pad "IO" / control-board pad "LIN") |
| CH2 | hilt V+ (flat in every take; disabled from the clash take onward) |

Decode with [`tools/led_frames.py`](../../tools/led_frames.py) (`--ch 0` or `--ch 1`); it prints
per-frame bit counts — a frame with ≠ 1440 bits dropped a sample (happens at 5 MHz and in
DSView stream mode) and its values are left-shifted, so exclude it. 10 MHz buffer-mode takes are
clean. For the Gen1-hilt file, decode the hilt line with `tools/decode_dsl.py -c 1`.

| File | What |
|---|---|
| `purple/…-strip-frame-50MHz` | one LED frame at 50 MHz — the bit timings |
| `purple/…-hiltline-vs-strip-10MHz` | hilt DATA and strip IN1 side by side: the same stream |
| `purple/…-wake-4MHz` | 30 s idle → blade on: no handshake, straight to frames (ignition animation) |
| `purple/…-connect-1MHz`, `…-connect-2-1MHz` | blade V+ applied: the connect handshake, twice |
| `purple/…-ign-10MHz` | hilt idle minutes → blade on → off: handshake + ignite + extinguish, bit-perfect |
| `purple/…-clash-5MHz` | two clashes |
| `purple/…-burn-5MHz` | 6.7 s steady burn: the twinkle cycle |
| `purple/…-twist-5MHz`, `…-twist-2-10MHz` (stream, 50 s) | the twist "laser shot", 12 shots in total |
| `gen1-hilt-purple/…-ign-4MHz` | a **Gen1** Savi's hilt driving the Gen2 blade |

Findings: `CATALOG.md` §16. This is session two of a multi-session capture; one crystal
(purple) so far.

## Session three — 2026-10-13: the cracked crystals

Same rig. All takes **DSView stream mode, 10 MHz, CH0 + CH1, no trigger** (CH2 off). Bit values
decode cleanly from either channel; in the `ben-solo-cracked/` set the CH0 lead had gone marginal
(runt pulses → 50–75 % of frames drop a bit), so **decode CH1** there — it is the same stream.
`tools/frame_timeline.py FILE.dsl` prints a 0.5 s colour timeline (`CH=1 python3 …` for the hilt wire).

| File | What |
|---|---|
| `kylo-cracked/…-full` (50 s) | off → ignite → burn → ~11 clashes → twist to blue → blue burn → off; the first take, hilt asleep 2 days: full handshake |
| `kylo-cracked/…-wake` | hilt asleep ~10 min → blade on: full handshake again |
| `kylo-cracked/…-ign`, `…-burn` (50 s), `…-clash`, `…-twist`, `…-twist-2`, `…-cyc` (13 clashes incl. a double), `…-idle` | the standard set |
| `ben-solo-cracked/…-wake`, `…-ign`, `…-burn` (50 s), `…-clash`, `…-twist`, `…-cyc`, `…-idle` | the standard set |
| `ben-solo-cracked/…-sleep` (50 s) | two off → 9 s → sleep-message → on cycles |
| `gen1-hilt-kylo-cracked/…-ign` | a **Gen1** Savi's hilt with the Kylo cracked crystal: legacy bytes, then `0x80` ×2 + the disconnect sound |

Findings: `CATALOG.md` §17.

## Session four — 2026-10-19: red, yellow, and the stab effect

Same rig plus a second, short analyzer ground lead at the strip's GND pad beside its data input
(it stops the strip-input channel dropping bits at 10 MHz). All takes **DSView stream mode, 10 MHz,
CH0 + CH1, no trigger**; decode CH1.

| File | What |
|---|---|
| `red/…-wake`, `…-ign`, `…-burn`, `…-clash`, `…-twist` (50 s), `…-twist-2` (re-ignites after twists), `…-cyc` (50 s, 15 strikes), `…-idle` | the standard set, plain red crystal |
| `yellow/…-wake`, `…-ign`, `…-burn`, `…-clash`, `…-twist` (50 s), `…-cyc` (50 s), `…-idle` | the standard set, plain yellow crystal |
| `red/…-stab`, `yellow/…-stab`, `purple/…-stab`, `kylo-cracked/…-stab`, `kylo-cracked/…-stab-blue` (twist to blue first), `ben-solo-cracked/…-stab` | the **stab** effect: blade on → three or four forward thrusts stopped abruptly → off |

Findings: `CATALOG.md` §18.

