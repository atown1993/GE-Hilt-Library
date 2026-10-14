#!/usr/bin/env python3
"""frame_timeline.py FILE.dsl [OUT.npy] — Gen2 blade LED-frame timeline: decodes CH0 frames (GRB, 55 LEDs),
drops frames with a bit count != 1440, saves (t, 165 bytes) rows to OUT.npy and prints 0.5 s windows of
mean/max G,R,B and lit-LED count. Written 2026-10-13 for the cracked-crystal takes."""
import zipfile,re,sys,os,numpy as np,collections
CH=int(os.environ.get('CH','0'))  # CH=1 to decode the hilt line instead (identical stream in frame mode)
z=zipfile.ZipFile(sys.argv[1]);h=z.read('header').decode(errors='ignore')
n=int(re.search(r'total samples = (\d+)',h).group(1));fs=10e6
names=sorted([x for x in z.namelist() if x.startswith(f'L-{CH}/')],key=lambda s:int(s.split('/')[1]))
b=np.unpackbits(np.frombuffer(b''.join(z.read(x) for x in names),dtype=np.uint8),bitorder='little')[:n]
d=np.diff(b.astype(np.int8));r=np.flatnonzero(d==1);fl=np.flatnonzero(d==-1)
if fl[0]<r[0]: fl=fl[1:]
k=min(len(r),len(fl));r=r[:k];fl=fl[:k];hw=(fl-r)/fs*1e9
gap=np.diff(r)/fs*1e6;cut=np.flatnonzero(gap>=50);st=np.concatenate(([0],cut+1));en=np.concatenate((cut+1,[k]))
frames=[]
for s,e in zip(st,en):
    v=hw[s:e];v=v[v>=150]
    if len(v)!=1440: frames.append((r[s]/fs,len(v),None));continue
    bits=(v>600).astype(int);by=bits.reshape(180,8).dot(1<<np.arange(7,-1,-1));t=by[:165].reshape(55,3)
    frames.append((r[s]/fs,1440,t))
good=[f for f in frames if f[2] is not None]
print(f'frames={len(frames)} good={len(good)} dropbit={len(frames)-len(good)}')
np.save(sys.argv[2] if len(sys.argv)>2 else '/tmp/frames.npy',np.array([(t,)+tuple(tr.flatten()) for t,_,tr in good]))
w=collections.OrderedDict()
for t,_,tr in good: w.setdefault(int(t*2),[]).append(tr)
for k,v in w.items():
    a=np.stack(v);m=a.mean((0,1));mx=a.max((0,1));lit=(a.sum(2)>0).sum(1).mean()
    print(f'{k/2:6.1f}s n={len(v):3d} mean G{m[0]:5.1f} R{m[1]:5.1f} B{m[2]:5.1f}  max G{mx[0]:3d} R{mx[1]:3d} B{mx[2]:3d} lit={lit:4.1f}')
