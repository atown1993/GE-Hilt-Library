#!/usr/bin/env python3
"""
GE Lightsaber Hilt Protocol Decoder for DSView .dsl files.

Protocol (measured from the captures in this repo):
  - Idle: HIGH
  - Command: 3 preamble pulses, then 8 data bits, MSB first
  - Preamble pulse: ~16.4ms LOW + ~500us HIGH gap
  - Bit 1: ~1.2ms LOW + ~500us HIGH gap
  - Bit 0: ~2.4ms LOW + ~500us HIGH gap
  - Decision: pulse > 3750us = preamble, > 1875us = bit 0, else bit 1

Channel: by default the DATA line is read from probe 0 (L-0/0 inside the .dsl).
Multi-channel rigs put DATA on another probe (e.g. CH7); pass --channel N to
decode probe N instead. The .dsl stores each probe as L-<channel>/0.
"""
import sys, os, zipfile, configparser, tempfile, shutil, argparse

PREAMBLE_US = 3750   # > this = preamble
BITSPLIT_US = 1875   # > this = bit 0, else bit 1


def parse_dsl(dsl_path, channel=0):
    """Extract .dsl into a temp dir, return (total_samples, sample_rate_hz, trigger_pos, packed bytes for `channel`)."""
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
        elif rate_str.endswith("Hz"):
            sample_rate = int(float(rate_str.replace("Hz", "").strip()))
        else:
            sample_rate = int(rate_str)
        trigger_pos = int(h.get("trigger pos", 0))
        chan_path = os.path.join(tmp, f"L-{channel}", "0")
        if not os.path.exists(chan_path):
            raise SystemExit(f"ERROR: channel {channel} not found in {os.path.basename(dsl_path)} "
                             f"(expected internal file L-{channel}/0). total probes = {h.get('total probes','?')}.")
        with open(chan_path, "rb") as f:
            packed = f.read()
        return total_samples, sample_rate, trigger_pos, packed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def unpack_bits(packed, n_samples):
    """Unpack bit-packed channel data. DSView stores 1 bit/sample, 8 samples/byte, LSB-first."""
    out = bytearray(n_samples)
    for i in range(n_samples):
        byte = packed[i >> 3]
        out[i] = (byte >> (i & 7)) & 1
    return out


def find_low_pulses(samples, sample_rate):
    us_per_sample = 1_000_000 / sample_rate
    n = len(samples)
    i = 0
    while i < n:
        if samples[i] == 0:
            start = i
            while i < n and samples[i] == 0:
                i += 1
            end = i
            yield (start, end, (end - start) * us_per_sample)
        else:
            i += 1


def decode_pulses(pulses):
    frames = []
    i = 0
    while i < len(pulses):
        if pulses[i][2] > PREAMBLE_US:
            preamble_count = 0
            j = i
            while j < len(pulses) and pulses[j][2] > PREAMBLE_US:
                preamble_count += 1
                j += 1
            if preamble_count >= 2 and j + 8 <= len(pulses):
                data_bits = pulses[j:j+8]
                if all(p[2] <= PREAMBLE_US for p in data_bits):
                    byte = 0
                    for p in data_bits:
                        bit = 1 if p[2] < BITSPLIT_US else 0
                        byte = (byte << 1) | bit
                    frames.append((pulses[i][0], byte, data_bits, preamble_count))
                    i = j + 8
                    continue
        i += 1
    return frames


_SAVI_COLORS = ['White','Red','Orange','Yellow','Green','Cyan','Blue','Purple']


def _color_or_idx(lo):
    if 0 <= lo < 8:
        return _SAVI_COLORS[lo]
    return f"idx {lo}"


def label(byte):
    hi = byte & 0xF0
    lo = byte & 0x0F
    if hi == 0x20:
        return f"Savi Ignite ({_color_or_idx(lo)})"
    if hi == 0x40:
        return f"Savi Extinguish ({_color_or_idx(lo)})"
    if hi == 0x80:
        return f"Savi Post-Off (sub-idx {lo})"
    if hi == 0xA0:
        return f"Savi Refresh ({_color_or_idx(lo)})"
    if hi == 0xC0:
        return f"Savi Clash (sub-idx {lo})"
    if hi == 0xE0:
        return f"Savi Disable (sub-idx {lo})"
    if hi == 0x30:
        return f"Legacy Ignite (idx {lo})"
    if hi == 0x50:
        return f"Legacy Extinguish (idx {lo})"
    if hi == 0xB0:
        return f"Legacy Refresh (idx {lo})"
    if hi == 0xD0:
        return f"Legacy Clash (sub-idx {lo})"
    if hi == 0x60:
        return f"Red Flicker Low (lvl {lo})"
    if hi == 0x70:
        return f"Red Flicker High (lvl {lo})"
    return f"Reserved / unknown (0x{byte:02X})"


def decode_file(dsl_path, channel=0):
    print(f"\n{'='*70}")
    print(f"FILE: {os.path.basename(dsl_path)}   (DATA = CH{channel})")
    print('='*70)
    total_samples, sample_rate, trigger_pos, packed = parse_dsl(dsl_path, channel)
    print(f"  Sample rate: {sample_rate/1000:.0f} kHz   Total samples: {total_samples:,}   Trigger@{trigger_pos:,}")

    samples = unpack_bits(packed, total_samples)
    pulses = list(find_low_pulses(samples, sample_rate))
    print(f"  LOW pulses found: {len(pulses)}")

    frames = decode_pulses(pulses)
    print(f"  Command frames decoded: {len(frames)}")
    print()
    print(f"  {'#':>3}  {'t (ms)':>10}  {'preamb':>6}  {'byte':>4}  description")
    print(f"  {'-'*3}  {'-'*10}  {'-'*6}  {'-'*4}  {'-'*40}")
    us_per_sample = 1_000_000 / sample_rate
    for i, (start, byte, bits, preambles) in enumerate(frames):
        t_ms = (start - trigger_pos) * us_per_sample / 1000
        print(f"  {i+1:>3}  {t_ms:>+10.2f}  {preambles:>6}   0x{byte:02X}  {label(byte)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="GE Hilt DATA-line protocol decoder for DSView .dsl files.")
    ap.add_argument("captures", nargs="+", help=".dsl capture files")
    ap.add_argument("-c", "--channel", type=int, default=0,
                    help="probe/channel carrying the hilt DATA line (default 0; 8-ch rig often uses 7)")
    args = ap.parse_args()
    for path in args.captures:
        decode_file(path, args.channel)
