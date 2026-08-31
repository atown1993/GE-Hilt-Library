import pandas as pd, json, html, os

# Self-contained: regenerates docs/ (the GitHub Pages site) from data/hilt-timings.csv.
# Usage:  python scripts/build_pages.py   (run from anywhere; paths resolve to repo root)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC  = os.path.join(REPO, "data", "hilt-timings.csv")   # source of truth
DOCS = os.path.join(REPO, "docs")
os.makedirs(DOCS, exist_ok=True)

df = pd.read_csv(SRC)
# serve a copy of the source CSV alongside the page for the download button
df.to_csv(os.path.join(DOCS, "hilt-timings.csv"), index=False)

DISPLAY=[("hilt","Hilt"),("color","Color"),("opcode_family","Family"),("platform","Platform"),
 ("index","Idx"),("ignite_byte","Ignite"),("refresh_byte","Refresh"),("extinguish_byte","Extinguish"),
 ("clash_byte","Clash"),("ignition_ms","Ignition (ms)"),("extdelay_ms","Ext Delay (ms)"),
 ("extinguish_ms","Extinguish (ms)"),("refresh_cadence_ms","Cadence (ms)"),("cadence_n","n"),
 ("capture_date","Captured"),("notes","Notes")]
keys=[k for k,_ in DISPLAY]; heads=[h for _,h in DISPLAY]
rows=[[("" if pd.isna(r[k]) else r[k]) for k in keys] for _,r in df.iterrows()]
DATA_JSON=json.dumps({"heads":heads,"keys":keys,"rows":rows}, default=str)

PWM=[["Red","0xA1","off","99.4%","off","Red"],["Green","0xA4","99.4%","off","off","Green"],
 ["Blue","0xA6","off","off","99.7%","Blue"],["Yellow","0xA3","59.8%","59.8%","off","Yellow"],
 ["Orange","0xA2","59.5%","59.5%","off","YELLOW (folded)"],["Purple","0xA7","off","59.8%","60.1%","Purple"],
 ["White","0xA0","44.0%","43.5%","44.0%","White"],["Teal","0xA5","off","off","99.7%","BLUE (folded)"]]
def pwm_rows_html():
    out=""
    for r in PWM:
        out+="<tr>"+"".join(f"<td>{html.escape(c)}</td>" for c in r)+"</tr>"
    return out

STYLE = """
:root{
  --bg:#f7f8fa; --card:#ffffff; --ink:#1a2230; --muted:#5b6472; --line:#e2e6ec;
  --accent:#1f3864; --savi:#e7f0fa; --savi-bar:#3b6fb0; --leg:#fbeee6; --leg-bar:#c07a44;
  --chip:#eef1f6;
}
:root:not([data-theme=light]){}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --bg:#0f141b; --card:#161d27; --ink:#e6ebf2; --muted:#95a0b0; --line:#26303d;
  --accent:#9db8e0; --savi:#16283d; --savi-bar:#4c86cf; --leg:#33241a; --leg-bar:#d08a52; --chip:#1d2632;
}}
:root[data-theme=dark]{
  --bg:#0f141b; --card:#161d27; --ink:#e6ebf2; --muted:#95a0b0; --line:#26303d;
  --accent:#9db8e0; --savi:#16283d; --savi-bar:#4c86cf; --leg:#33241a; --leg-bar:#d08a52; --chip:#1d2632;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.5;font-size:15px}
.wrap{max-width:1200px;margin:0 auto;padding:28px 20px 60px}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
h1{font-size:26px;margin:0 0 4px;letter-spacing:-.01em}
.tag{color:var(--muted);margin:0 0 20px;font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 18px;margin:16px 0}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:6px 0 14px}
#q{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;
  background:var(--card);color:var(--ink);font-size:14px}
.btn{display:inline-flex;align-items:center;gap:7px;padding:9px 14px;border:1px solid var(--accent);
  border-radius:8px;background:var(--accent);color:#fff;text-decoration:none;font-size:14px;font-weight:600;cursor:pointer}
.count{color:var(--muted);font-size:13px;white-space:nowrap}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:13px}
thead th{position:sticky;top:0;background:var(--accent);color:#fff;text-align:left;padding:9px 10px;
  white-space:nowrap;cursor:pointer;user-select:none;font-weight:600}
thead th:hover{filter:brightness(1.08)}
th .ar{opacity:.5;font-size:11px;margin-left:3px}
tbody td{padding:8px 10px;border-top:1px solid var(--line);vertical-align:top}
tbody tr.savi td{background:var(--savi)} tbody tr.leg td{background:var(--leg)}
td.notes{min-width:340px;max-width:520px;white-space:normal;color:var(--muted);font-size:12px}
.mono{font-variant-numeric:tabular-nums;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.fambar{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:6px;vertical-align:middle}
h2{font-size:18px;margin:26px 0 2px} .sub{color:var(--muted);font-size:13px;margin:0 0 12px}
.pwm td:first-child,.pwm th:first-child{text-align:left}
.pwm td{text-align:center}
.legend{font-size:13px;color:var(--muted)}
.legend .k{display:inline-flex;align-items:center;margin-right:16px}
footer{color:var(--muted);font-size:12.5px;margin-top:30px;border-top:1px solid var(--line);padding-top:16px}
a{color:var(--accent)}
"""

TABLE_JS = """
const D = __DATA__;
const numCols = new Set(['index','ignite_byte','refresh_byte','extinguish_byte','clash_byte',
  'ignition_ms','extdelay_ms','extinguish_ms','refresh_cadence_ms','cadence_n']);
let sortCol=-1, sortDir=1;
const famIdx = D.keys.indexOf('opcode_family');
const tbody = document.getElementById('tb');
const thead = document.getElementById('th');
const q = document.getElementById('q');
const cnt = document.getElementById('cnt');

D.heads.forEach((h,i)=>{
  const th=document.createElement('th'); th.innerHTML=h+'<span class="ar"></span>';
  th.onclick=()=>{ sortDir = sortCol===i?-sortDir:1; sortCol=i; render(); };
  thead.appendChild(th);
});
function cmp(a,b,key){
  if(numCols.has(key)){ const x=parseFloat(a),y=parseFloat(b);
    const ax=isNaN(x),ay=isNaN(y); if(ax&&ay)return 0; if(ax)return 1; if(ay)return -1; return x-y; }
  return String(a).localeCompare(String(b));
}
function render(){
  const term=q.value.trim().toLowerCase();
  let rows=D.rows.map((r,i)=>r);
  if(term) rows=rows.filter(r=>r.some(c=>String(c).toLowerCase().includes(term)));
  if(sortCol>=0){ const key=D.keys[sortCol];
    rows=rows.slice().sort((r1,r2)=>sortDir*cmp(r1[sortCol],r2[sortCol],key)); }
  tbody.innerHTML='';
  rows.forEach(r=>{
    const tr=document.createElement('tr');
    const fam=String(r[famIdx]); tr.className = fam==='Savi'?'savi':'leg';
    r.forEach((c,ci)=>{
      const td=document.createElement('td'); const key=D.keys[ci];
      if(key==='notes'){ td.className='notes'; td.textContent=c; }
      else if(key==='opcode_family'){ const bar=fam==='Savi'?'var(--savi-bar)':'var(--leg-bar)';
        td.innerHTML='<span class="fambar" style="background:'+bar+'"></span>'+c; }
      else if(numCols.has(key)||/byte/.test(key)){ td.className='mono'; td.textContent=c; }
      else td.textContent=c;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  thead.querySelectorAll('.ar').forEach((s,i)=> s.textContent = i===sortCol?(sortDir>0?'▲':'▼'):'');
  cnt.textContent = rows.length+' of '+D.rows.length+' rows';
}
q.addEventListener('input',render);
render();
"""

BODY = f"""
<div class="wrap">
  <h2 class="sr-only">Interactive reference table of Galaxy's Edge lightsaber hilt protocol bytes and timings, sortable and searchable, with a color-to-PWM table.</h2>
  <h1>GE-Hilt-Library — Hilt Timings</h1>
  <p class="tag">A firsthand reference of how Galaxy's Edge hilts drive stock blades: protocol bytes and measured timings, one row per hilt/color. Every value measured on the bench.</p>

  <div class="controls">
    <input id="q" type="text" placeholder="Search hilt, color, byte, note…" aria-label="Search table">
    <span id="cnt" class="count"></span>
    <a class="btn" href="./hilt-timings.csv" download>⬇ Download CSV</a>
  </div>
  <div class="legend" style="margin-bottom:10px">
    <span class="k"><span class="fambar" style="background:var(--savi-bar)"></span>Savi opcode family (0xAx)</span>
    <span class="k"><span class="fambar" style="background:var(--leg-bar)"></span>Legacy opcode family (0xBx)</span>
    &nbsp;· click any column header to sort
  </div>
  <div class="scroll">
    <table><thead><tr id="th"></tr></thead><tbody id="tb"></tbody></table>
  </div>

  <h2>Color → gate PWM duty (Savi's, stock blade)</h2>
  <p class="sub">PWM carrier 5917–5952 Hz across all colors; brightness set by duty cycle. Note the orange→yellow and teal→blue folds on a stock blade.</p>
  <div class="scroll">
    <table class="pwm"><thead><tr>
      <th>Kyber</th><th>Hilt byte</th><th>Green (CH8)</th><th>Red (CH9)</th><th>Blue (CH10)</th><th>Stock-blade visible</th>
    </tr></thead><tbody>{pwm_rows_html()}</tbody></table>
  </div>

  <footer>
    <strong>All data firsthand</strong>, measured from physical hilts with stock Galaxy's Edge blades —
    nothing copied from or compared against any other dataset. Captures &amp; measurements licensed
    <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
    Have a hilt to add? See the repo's submission template — send a raw capture, we do the rest.<br><br>
    Not affiliated with Disney / Lucasfilm. Galaxy's Edge, Savi's Workshop and the named hilts are their
    products; names identify which physical product a row came from.
  </footer>
</div>
"""

# --- docs/index.html (GitHub Pages: fetches ./hilt-timings.csv is NOT used; data embedded at build for zero-fetch reliability) ---
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GE-Hilt-Library — Hilt Timings</title>
<style>{STYLE}</style></head>
<body>{BODY}
<script>{TABLE_JS.replace('__DATA__', DATA_JSON)}</script>
</body></html>"""
open(os.path.join(DOCS,"index.html"),"w").write(page)

print("regenerated docs/index.html + docs/hilt-timings.csv from data/hilt-timings.csv (%d rows)" % len(df))
