#!/usr/bin/env python3
"""
Multi-channel timing analyzer for GE Hilt 8-channel captures.

Extracts three-phase timings (Ignition, Extinguish Delay, Extinguish)
from a .dsl with all 8 channels enabled.

Default channel map (see the electrical-architecture section of CATALOG.md) — override per capture with
--data-ch / --segments / --gates when the physical hookup differs (DSLogic
case markings differ from connector-block numbering; a wrong map silently
mislabels every result — see Session Notes 2026-05-09). The active map is
printed in each file's output header so a mislabel is visible, not silent.
  CH0  = Hilt DATA
  CH4  = Segment 4 (tip)
  CH5  = Segment 3
  CH6  = Segment 2
  CH7  = Segment 1 (hilt end)
  CH8  = Green RGB gate
  CH9  = Red RGB gate
  CH10 = Blue RGB gate

Timing definitions (measured purely on blade side, immune to hilt noise):
  Ignition (ms)         - wave duration: first segment-enable HIGH to last
                          segment-enable HIGH (visible blade light-up time).
  Extinguish Delay (ms) - time from extinguish byte (0x4X/0x5X) on CH0 to
                          first segment-enable transitioning LOW (audio-tail
                          period during which the blade stays lit).
  Extinguish (ms)       - wave duration: first segment LOW to last segment
                          LOW (visible blade fade-out time).
"""
import sys, os, zipfile, configparser, tempfile, shutil, argparse

PREAMBLE_US = 3750
BITSPLIT_US = 1875
DEFAULT_DATA_CH = 0
DEFAULT_SEGMENT_CHANNELS = [7, 6, 5, 4]  # seg1 (hilt end) .. seg4 (tip)
DEFAULT_GATE_CHANNELS = {8: "Green", 9: "Red", 10: "Blue"}


def parse_dsl_full(dsl_path):
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(dsl_path) as z:
            z.extractall(tmp)
        cfg = configparser.ConfigParser()
        with open(os.path.join(tmp, "header")) as f:
            cfg.read_file(f)
        h = cfg["header"]
        total_samples = int(h["total samples"])
        rate_str = h["samplerate"].strip()
        if rate_str.endswith("MHz"):
            sample_rate = int(float(rate_str.replace("MHz", "").strip()) * 1_000_000)
        elif rate_str.endswith("kHz"):
            sample_rate = int(float(rate_str.replace("kHz", "").strip()) * 1_000)
        else:
            sample_rate = int(rate_str.replace("Hz", "").strip())
        trigger_pos = int(h.get("trigger pos", 0))
        chan_data = {}
        for entry in os.listdir(tmp):
            if entry.startswith("L-") and os.path.isdir(os.path.join(tmp, entry)):
                ch = int(entry.split("-")[1])
                with open(os.path.join(tmp, entry, "0"), "rb") as f:
                    chan_data[ch] = f.read()
        return sample_rate, trigger_pos, total_samples, chan_data
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def unpack(packed, n):
    out = bytearray(n)
    for i in range(n):
        out[i] = (packed[i >> 3] >> (i & 7)) & 1
    return out


def find_low_pulses(samples, sample_rate):
    us = 1_000_000 / sample_rate
    n = len(samples)
    i = 0
    pulses = []
    while i < n:
        if samples[i] == 0:
            s = i
            while i < n and samples[i] == 0:
                i += 1
            pulses.append((s, i, (i - s) * us))
        else:
            i += 1
    return pulses


def decode_frames(pulses):
    frames = []
    i = 0
    while i < len(pulses):
        if pulses[i][2] > PREAMBLE_US:
            j = i
            pre = 0
            while j < len(pulses) and pulses[j][2] > PREAMBLE_US:
                pre += 1
                j += 1
            if pre >= 2 and j + 8 <= len(pulses):
                bits = pulses[j:j+8]
                if all(p[2] <= PREAMBLE_US for p in bits):
                    byte = 0
                    for p in bits:
                        bit = 1 if p[2] < BITSPLIT_US else 0
                        byte = (byte << 1) | bit
                    frames.append((pulses[i][0], byte))
                    i = j + 8
                    continue
        i += 1
    return frames


def first_low_to_high_sustained(samples, start, end, min_run_us, sample_rate):
    """Find first LOW->HIGH transition in [start, end) where the channel
    then stays HIGH for at least min_run_us. Returns the transition sample
    index, or None."""
    min_run = int(min_run_us * sample_rate / 1_000_000)
    n = min(end, len(samples))
    i = start
    while i < n and samples[i] == 1:
        i += 1
    while i < n:
        if samples[i] == 1 and samples[i-1] == 0:
            j = i
            while j < n and samples[j] == 1:
                j += 1
            if j - i >= min_run:
                return i
            i = j
        else:
            i += 1
    return None


def first_high_to_low_sustained(samples, start, end, min_run_us, sample_rate):
    """Legacy strict-transition detector. Brittle against PWM fluctuations.
    Kept for reference; production code should use first_duty_drop_below."""
    min_run = int(min_run_us * sample_rate / 1_000_000)
    n = min(end, len(samples))
    i = start
    while i < n:
        if samples[i] == 0 and samples[i-1] == 1:
            j = i
            while j < n and samples[j] == 0:
                j += 1
            if j - i >= min_run:
                return i
            i = j
        else:
            i += 1
    return None


def first_duty_drop_below(samples, start, end, threshold, window_ms, sample_rate):
    """Slide a window of `window_ms` ms forward from `start`. Return the
    sample index of the first window-start where duty_cycle < threshold.
    Robust against brief PWM glitches during fade-out. Returns None if
    duty never drops below threshold in [start, end]."""
    win = int(window_ms * sample_rate / 1000)
    step = max(win // 20, 1)  # ~5% of window, fine-grained scan
    n = min(end, len(samples))
    i = start
    while i + win <= n:
        if gate_pwm_duty(samples, i, i + win) < threshold:
            return i
        i += step
    return None


def gate_pwm_duty(samples, start, end):
    if end <= start:
        return 0.0
    return sum(samples[start:end]) / (end - start)


def analyze(dsl_path, data_ch=DEFAULT_DATA_CH,
            seg_channels=None, gate_channels=None):
    seg_channels = seg_channels or DEFAULT_SEGMENT_CHANNELS
    gate_channels = gate_channels or DEFAULT_GATE_CHANNELS
    rate, trig, total, chans = parse_dsl_full(dsl_path)
    us_per_sample = 1_000_000 / rate
    ms = lambda s: (s - trig) * us_per_sample / 1000

    ch0 = unpack(chans[data_ch], total)
    pulses = find_low_pulses(ch0, rate)
    frames = decode_frames(pulses)

    ext_byte_idx = None
    for start_idx, byte in frames:
        hi = byte & 0xF0
        if hi in (0x40, 0x50):
            ext_byte_idx = start_idx

    seg = {ch: unpack(chans[ch], total) for ch in seg_channels}
    gates = {ch: unpack(chans[ch], total) for ch in gate_channels}

    print()
    print(f"=== {os.path.basename(dsl_path)} ===")
    print(f"Sample rate: {rate/1e6:.1f} MHz   Trigger@{trig}   Buffer: {total/rate:.2f}s")
    gates_str = ", ".join(f"CH{c}={n}" for c, n in gate_channels.items())
    print(f"Channel map: DATA=CH{data_ch}   segments={['CH%d' % c for c in seg_channels]}   gates=[{gates_str}]")
    print()
    print("Protocol bytes:")
    for s, b in frames:
        print(f"  {ms(s):+8.2f} ms  0x{b:02X}")

    seg_up_at = {}
    for ch in seg_channels:
        seg_up_at[ch] = first_low_to_high_sustained(seg[ch], 0, total, 50_000, rate)
    print()
    print("Ignition wave (first sustained LOW->HIGH per segment):")
    for ch in seg_channels:
        a = seg_up_at[ch]
        if a is None:
            print(f"  CH{ch}: (no activation)")
        else:
            print(f"  CH{ch}: {ms(a):+8.2f} ms")
    if all(seg_up_at[c] is not None for c in seg_channels):
        first_up = min(seg_up_at[c] for c in seg_channels)
        last_up = max(seg_up_at[c] for c in seg_channels)
        ignition_ms = (last_up - first_up) * us_per_sample / 1000
    else:
        ignition_ms = None

    seg_down_at = {}
    ext_delay_ms = None
    ext_duration_ms = None
    if ext_byte_idx is not None:
        for ch in seg_channels:
            seg_down_at[ch] = first_duty_drop_below(
                seg[ch], ext_byte_idx, total, 0.5, 50, rate)
        print()
        print(f"Extinguish wave (first sustained HIGH->LOW per segment, after ext byte at {ms(ext_byte_idx):+.2f} ms):")
        for ch in seg_channels:
            d = seg_down_at[ch]
            if d is None:
                print(f"  CH{ch}: (stays high)")
            else:
                delta = (d - ext_byte_idx) * us_per_sample / 1000
                print(f"  CH{ch}: {ms(d):+8.2f} ms (+{delta:.1f} ms after ext)")
        drops = [seg_down_at[c] for c in seg_channels if seg_down_at[c] is not None]
        if drops:
            first_drop = min(drops)
            last_drop = max(drops)
            ext_delay_ms = (first_drop - ext_byte_idx) * us_per_sample / 1000
            ext_duration_ms = (last_drop - first_drop) * us_per_sample / 1000
    else:
        print()
        print("(No extinguish byte found on CH0 - skipping extinguish timing.)")

    print()
    print("Gate PWM duty (200ms window starting 50ms after blade fully lit):")
    if ignition_ms is not None and ext_byte_idx is not None:
        sample_start = max(seg_up_at[c] for c in seg_channels) + int(0.05 * rate)
        sample_end = min(sample_start + int(0.2 * rate), ext_byte_idx)
        for ch, name in gate_channels.items():
            d = gate_pwm_duty(gates[ch], sample_start, sample_end)
            print(f"  CH{ch} ({name}): {d*100:5.1f}%")

    print()
    print("=" * 50)
    print("THREE-PHASE TIMING RESULT:")
    print(f"  Ignition:         {f'{ignition_ms:.0f} ms' if ignition_ms is not None else 'n/a'}")
    print(f"  Extinguish Delay: {f'{ext_delay_ms:.0f} ms' if ext_delay_ms is not None else 'n/a'}")
    print(f"  Extinguish:       {f'{ext_duration_ms:.0f} ms' if ext_duration_ms is not None else 'n/a'}")
    print("=" * 50)


def parse_gates(text):
    out = {}
    for part in text.split(","):
        ch, name = part.split(":")
        out[int(ch)] = name
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="GE Hilt 8-channel timing analyzer")
    ap.add_argument("captures", nargs="+", help=".dsl capture files")
    ap.add_argument("--data-ch", type=int, default=DEFAULT_DATA_CH,
                    help=f"hilt DATA channel (default {DEFAULT_DATA_CH})")
    ap.add_argument("--segments", default=",".join(map(str, DEFAULT_SEGMENT_CHANNELS)),
                    help="segment channels, seg1(hilt end)..seg4(tip) (default %(default)s)")
    ap.add_argument("--gates", default=",".join(f"{c}:{n}" for c, n in DEFAULT_GATE_CHANNELS.items()),
                    help="gate channels as ch:Name,... (default %(default)s)")
    args = ap.parse_args()
    segs = [int(x) for x in args.segments.split(",")]
    gates = parse_gates(args.gates)
    for p in args.captures:
        analyze(p, data_ch=args.data_ch, seg_channels=segs, gate_channels=gates)
