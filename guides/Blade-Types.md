# Blade Types — GE Lightsaber Blades

A reference for describing Galaxy's Edge lightsaber blades without conflating the
two things that actually vary.

## Two independent axes: controller type and LED board

Describe a blade by (a) its controller and (b) its LED board. Don't conflate them.

**Controller types (what drives the LEDs):**

1. **Neopixel** — Neopixel controller + Neopixel (addressable) LEDs.
2. **Stock** — the standard GE blade controller.
3. **Enhanced** — an aftermarket enhanced controller swapped in; the LED PCB stays
   stock, only the controller changes.

**LED board:**

- **RGB blades** — the vast majority. RGB LEDs; can show any color; work in any hilt.
- **Single-color blades** — the LED board has ONLY one color of LED, no RGB.
  "Single-color" means physically **white** LEDs, **red** LEDs, or **green** LEDs —
  that is the entire meaning. Not a firmware limit; a hardware one.

## There is no "Savi blade" vs "Legacy blade"

All standard RGB blades are identical from a board perspective — any length,
interchangeable across all hilts. "Savi's blade" is just the nickname for the 31"
blade that ships with the Savi's Workshop experience; Legacy sets usually bundle the
same blade. The `savis-` / `legacy-` prefix in capture filenames refers to the
**HILT's protocol family, NOT the blade**.

## The ONLY physical single-color blades (3)

- **Ahsoka** — white LED blade
- **The Stranger** — red LED blade
- **Yoda saber** — green LED blade

No RGB LEDs, so each can only ever show its one color. Everything else is RGB.

## Shin Hati / Baylan Skoll blades are RGB — the orange is FIRMWARE, not hardware

The Shin/Baylan blades are **normal RGB blades**. They work in any hilt and can show
blue, green, red, etc. They are NOT single-color.

What's special is code, not the LED board. Stock RGB blades have a color-fold limit:
even with an orange kyber crystal a stock blade shows **yellow**, and a teal crystal
shows **blue** (see the stock-blade rendering section of [`CATALOG.md`](../CATALOG.md)). The Shin/Baylan blades carry **modified
firmware that unlocks orange** — with two catches:

- They still won't show **teal** — only orange is unlocked, not the full fold.
- Orange only renders when the blade is on **its own Shin/Baylan hilt**. In a Savi's
  hilt, even with an orange crystal, a Shin/Baylan blade still shows yellow.

So "the orange blade" is stock-hardware RGB running special firmware, paired with a
hilt that triggers the orange path.

## Consequence for the gate-PWM finding (2026-08-22)

The ~15.7 kHz gate PWM carrier measured on the Baylan/Shin orange blade vs ~5917 Hz
on a stock RGB blade is therefore a **blade-firmware** difference (the Shin/Baylan
blade's modified controller code) — NOT single-color-vs-RGB, and NOT per-arbitrary
-blade. Stock RGB blades cluster at ~5917–5952 Hz. See the electrical-architecture
section of [`CATALOG.md`](../CATALOG.md).
