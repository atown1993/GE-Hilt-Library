import os, re, glob

HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(HERE)
CAP=os.path.join(REPO,"captures")
RATE=re.compile(r'-(\d+(?:\.\d+)?(?:M|k)Hz)-')
DATE=re.compile(r'(\d{4}-\d{2}-\d{2})\.dsl$')

def meta(fn):
    r=RATE.search(fn); d=DATE.search(fn)
    return (r.group(1) if r else "—"), (d.group(1) if d else "—")

def rows_for(files):
    out=[]
    for f in sorted(files):
        rate,date=meta(os.path.basename(f))
        out.append((os.path.basename(f), rate, date))
    return out

def section(title, groups):
    L=[f"## {title}\n"]
    for name in sorted(groups):
        files=groups[name]
        if not files: continue
        L.append(f"### {name}  ·  {len(files)} capture(s)\n")
        L.append("| Capture file | Rate | Date |")
        L.append("|---|---|---|")
        for fn,rate,date in rows_for(files):
            rel=f"{name_dir[name]}/{fn}"
            L.append(f"| [`{fn}`]({rel}) | {rate} | {date} |")
        L.append("")
    return "\n".join(L)

# collect
savis={}; legacy={}; validation=[]
name_dir={}
for f in glob.glob(os.path.join(CAP,"savis","*","*.dsl")):
    color=os.path.basename(os.path.dirname(f)).capitalize()
    savis.setdefault(color,[]).append(f); name_dir[color]=f"savis/{color.lower()}"
for f in glob.glob(os.path.join(CAP,"legacy","*","*.dsl")):
    hilt=os.path.basename(os.path.dirname(f))
    disp=hilt.replace("-"," ").title()
    legacy.setdefault(disp,[]).append(f); name_dir[disp]=f"legacy/{hilt}"
for f in glob.glob(os.path.join(CAP,"validation","*.dsl")):
    validation.append(f)

total=sum(len(v) for v in savis.values())+sum(len(v) for v in legacy.values())+len(validation)

head=f"""# Capture Index

{total} firsthand `.dsl` captures, all recorded on the bench with stock Galaxy's Edge
blades. Open them in [DSView](https://www.dreamsourcelab.com/), or decode with
[`tools/decode_dsl.py`](../tools/decode_dsl.py). Protocol details are in
[`CATALOG.md`](../CATALOG.md); per-hilt bytes and timings in
[`data/hilt-timings.csv`](../data/hilt-timings.csv).

Files are named `<family>-<hilt>-<action>-<rate>-<date>.dsl`. Actions include
`ignite-clash-ext` (a full arc), `steadyburn`, `clashcycle`, `fullcycle`,
`colorchange`, and `flicker` variants.

*This index is generated from the capture tree by `scripts/build_index.py`.*

---

"""
body = section("Savi's Workshop (by kyber color)", savis) + "\n---\n\n" \
     + section("Legacy character hilts", legacy)
if validation:
    name_dir["Rig validation & channel-mapping"]="validation"
    body += "\n---\n\n## Rig validation & channel-mapping  ·  %d capture(s)\n\n" % len(validation)
    body += "| Capture file | Rate | Date |\n|---|---|---|\n"
    for fn,rate,date in rows_for(validation):
        body += f"| [`{fn}`](validation/{fn}) | {rate} | {date} |\n"

open(os.path.join(CAP,"INDEX.md"),"w").write(head+body+"\n")
print(f"wrote captures/INDEX.md — {total} captures, {len(savis)} Savi colors, {len(legacy)} Legacy hilts, {len(validation)} validation")
