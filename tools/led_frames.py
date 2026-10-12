#!/usr/bin/env python3
"""led_frames.py — decode WS2812-style LED frames from a DSView .dsl capture.

usage: led_frames.py FILE.dsl [--ch N] [--frames K] [--one-ns 600] [--gap-us 50]
Prints per-channel edge summary, then for --ch: frame table (t, bits, LEDs, distinct triplets).
"""
import sys, zipfile, re, argparse, numpy as np
ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--ch',type=int,default=0)
ap.add_argument('--frames',type=int,default=12); ap.add_argument('--one-ns',type=float,default=600)
ap.add_argument('--gap-us',type=float,default=50); ap.add_argument('--min-ns',type=float,default=150)
a=ap.parse_args()
z=zipfile.ZipFile(a.file); h=z.read('header').decode(errors='ignore')
n=int(re.search(r'total samples = (\d+)',h).group(1)); rate=re.search(r'samplerate = ([\d.]+) ?([kM])Hz',h)
fs=float(rate.group(1))*(1e6 if rate.group(2)=='M' else 1e3)
probes=sorted({int(x.split('/')[0][2:]) for x in z.namelist() if x.startswith('L-')})
print(f'{a.file}: {rate.group(0)}  samples={n}  span={n/fs:.3f}s  probes={probes}')
def load(ch):
    names=sorted([x for x in z.namelist() if x.startswith(f'L-{ch}/')],key=lambda s:int(s.split('/')[1]))
    raw=b''.join(z.read(x) for x in names); return np.unpackbits(np.frombuffer(raw,dtype=np.uint8),bitorder='little')[:n]
for ch in probes:
    b=load(ch); d=np.diff(b.astype(np.int8)); r=np.flatnonzero(d==1); fl=np.flatnonzero(d==-1)
    if len(r)==0 and len(fl)==0: print(f'  CH{ch}: flat {"HIGH" if b[0] else "LOW"}'); continue
    if len(fl) and (len(r)==0 or fl[0]<r[0]): fl=fl[1:]
    k=min(len(r),len(fl)); hw=(fl[:k]-r[:k])/fs*1e6
    lo=np.diff(r[:k])/fs*1e6-hw[:k-1] if k>1 else np.array([])
    print(f'  CH{ch}: high%={b.mean()*100:.2f} edges={len(r)}/{len(fl)} first={r[0]/fs*1e3:.2f}ms last={(fl[-1] if len(fl) else r[-1])/fs*1e3:.2f}ms  '
          f'HIGH us: min={hw.min():.2f} med={np.median(hw):.2f} max={hw.max():.1f}  LOW us: med={np.median(lo) if lo.size else 0:.2f} max={lo.max() if lo.size else 0:.1f}')
b=load(a.ch); d=np.diff(b.astype(np.int8)); r=np.flatnonzero(d==1); fl=np.flatnonzero(d==-1)
if len(fl) and (len(r)==0 or fl[0]<r[0]): fl=fl[1:]
k=min(len(r),len(fl)); r=r[:k]; fl=fl[:k]; hw=(fl-r)/fs*1e9
gap=np.diff(r)/fs*1e6; cut=np.flatnonzero(gap>=a.gap_us); starts=np.concatenate(([0],cut+1)); ends=np.concatenate((cut+1,[k]))
print(f'\nCH{a.ch} frames (gap>={a.gap_us}us): {len(starts)}')
prev=None
for fi,(s,e) in enumerate(zip(starts,ends)):
    seg=hw[s:e]; v=seg[seg>=a.min_ns]; bits=''.join('1' if w>a.one_ns else '0' for w in v)
    by=[int(bits[i:i+8],2) for i in range(0,len(bits)-7,8)]; trip=[tuple(by[i:i+3]) for i in range(0,len(by)-2,3)]
    u={}
    for t in trip: u[t]=u.get(t,0)+1
    top=sorted(u.items(),key=lambda x:-x[1])[:4]
    t0=r[s]/fs*1e3; per=f'+{t0-prev:.1f}' if prev is not None else ''
    if fi<a.frames or fi>=len(starts)-2:
        print(f'  f{fi:3d} t={t0:9.3f}ms {per:>8} bits={len(v):5d} leds={len(v)/24:6.2f} dur={(fl[e-1]-r[s])/fs*1e3:.2f}ms  top={top}')
    elif fi==a.frames: print('  ...')
    prev=t0
