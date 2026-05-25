#!/usr/bin/env python3
"""Build the SOTSI/UHF -> Webflow migration tracking dashboard.

Reads data/migration_plan.json (the editable source of truth) and renders a
self-contained, on-brand static dashboard for the whole team:
  - KPI header (% done, hours by role, blocked, in-progress, done)
  - role-hour progress bars + sprint tiles
  - filterable board (Tabulator) by status / sprint / verdict / brand / category
  - per-page slide panel (old->new URL, content checklist, hours, notes, links)
  - Team Guide tab (brand rules + content workflow + Definition of Done)

Output: migration_dashboard.html  (copied to team.html for GitHub Pages /team)
Stdlib only. No pip, no API key. Re-runnable / idempotent (except timestamp).
"""
import json
import html
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT     = Path(__file__).resolve().parent
DATA_IN  = ROOT / "data" / "migration_plan.json"
HTML_OUT = ROOT / "migration_dashboard.html"
COPY_TO  = ROOT / "team.html"

ROLES = ["design", "content", "media", "build", "review"]
ROLE_ES = {"design": "Diseño", "content": "Contenido", "media": "Video/Imagen",
           "build": "Build Webflow", "review": "Revisión"}
STATUSES = ["backlog", "design", "content", "build", "review", "done", "blocked"]
VERDICTS = ["keep", "improve", "rebuild", "consolidate", "drop"]


# ── data + rollups ─────────────────────────────────────────────────────────────

def load_plan(path):
    """Read migration_plan.json and return the parsed dict."""
    return json.load(open(path, encoding="utf-8"))


def page_hours(p):
    """Sum of all role hours for a single page."""
    return round(sum(p["role_hours"].get(r, 0) for r in ROLES), 2)


def compute_meta(pages, sprints):
    """Rebuild the meta rollups from the pages array (never trust stored values)."""
    buildable = [p for p in pages if p["verdict"] != "drop"]
    done = [p for p in pages if p["status"] == "done"]
    role_total = {r: round(sum(p["role_hours"].get(r, 0) for p in buildable), 1) for r in ROLES}
    role_done  = {r: round(sum(p["role_hours"].get(r, 0) for p in done), 1) for r in ROLES}
    total_h = round(sum(role_total.values()), 1)
    done_h  = round(sum(role_done.values()), 1)
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_pages": len(pages),
        "buildable_pages": len(buildable),
        "by_status": {s: sum(1 for p in pages if p["status"] == s) for s in STATUSES},
        "by_verdict": dict(Counter(p["verdict"] for p in pages)),
        "by_brand": dict(Counter(p["brand"] for p in pages)),
        "by_sprint": dict(Counter(p["sprint"] for p in pages)),
        "role_total": role_total,
        "role_done": role_done,
        "total_hours": total_h,
        "done_hours": done_h,
        "hours_remaining": round(total_h - done_h, 1),
        "pct_done": round(len(done) / len(pages) * 100, 1) if pages else 0,
    }


# ── fragment renderers ──────────────────────────────────────────────────────────

def kpi_cards(m):
    """Five KPI cards for the header strip."""
    in_prog = sum(m["by_status"].get(s, 0) for s in ["design", "content", "build", "review"])
    cards = [
        ("done",    f'{m["pct_done"]}%', "Avance", f'{m["by_status"]["done"]} de {m["total_pages"]} páginas'),
        ("hours",   f'{m["hours_remaining"]:g}h',  "Horas restantes", f'de {m["total_hours"]:g}h totales'),
        ("prog",    str(in_prog),        "En progreso", "design / content / build / review"),
        ("blocked", str(m["by_status"]["blocked"]), "Bloqueadas", "necesitan decisión"),
        ("pages",   str(m["buildable_pages"]),      "Páginas a construir", f'{m["by_verdict"].get("drop",0)} drops (solo redirect)'),
    ]
    out = []
    for key, val, label, sub in cards:
        out.append(
            f'<div class="kpi kpi-{key}"><div class="kpi-val">{val}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>')
    return "\n".join(out)


def role_bars(m):
    """Progress bars: done hours vs total hours per role."""
    out = []
    for r in ROLES:
        tot = m["role_total"][r] or 0
        dn  = m["role_done"][r] or 0
        pct = round(dn / tot * 100) if tot else 0
        out.append(
            f'<div class="bar-row"><div class="bar-head"><span>{ROLE_ES[r]}</span>'
            f'<span class="bar-num">{dn:g} / {tot:g}h</span></div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div></div>')
    return "\n".join(out)


def sprint_tiles(pages, sprints, m):
    """One tile per sprint: label, goal, page count, mini progress."""
    out = []
    for s in sprints:
        sid = s["id"]
        sp = [p for p in pages if p["sprint"] == sid]
        done = sum(1 for p in sp if p["status"] == "done")
        hrs = round(sum(page_hours(p) for p in sp if p["verdict"] != "drop"), 1)
        pct = round(done / len(sp) * 100) if sp else 0
        label = html.escape(s["label"])
        goal = html.escape(s["goal"])
        out.append(
            f'<div class="sprint-tile"><div class="sprint-id">{label}</div>'
            f'<div class="sprint-goal">{goal}</div>'
            f'<div class="sprint-meta"><span>{len(sp)} págs</span><span>{hrs:g}h</span>'
            f'<span>{done}/{len(sp)} done</span></div>'
            f'<div class="bar-track sm"><div class="bar-fill" style="width:{pct}%"></div></div></div>')
    return "\n".join(out)


def team_guide():
    """Static Team Guide tab: brand rules + content workflow + Definition of Done."""
    swatches = [
        ("Midnight Navy", "#0E1631"), ("Cosmic Purple", "#3C1951"),
        ("Pure White", "#FFFFFF"), ("Soft Periwinkle", "#D2CCFD"),
        ("Light Lilac", "#E7D4F1"), ("Luminous Yellow", "#FFEB45"),
        ("Golden Yellow", "#FED457"),
    ]
    chips = "".join(
        f'<div class="sw"><span class="sw-box" style="background:{hx}"></span>'
        f'<span class="sw-name">{n}</span><span class="sw-hex">{hx}</span></div>'
        for n, hx in swatches)
    return f"""
<div class="guide">
  <details open class="g-card"><summary>1 · Reglas de marca</summary>
    <div class="g-body">
      <p><b>Dos marcas, un sistema.</b> SOTSI = Midnight Navy + naturaleza (montañas/agua,
      <u>nunca</u> arena). UHF = Cosmic Purple + rostros humanos, close-ups diversos.</p>
      <div class="sw-grid">{chips}</div>
      <p><b>Tipografía:</b> Títulos = <i>Canela</i> (serif) · Cuerpo = <i>Jost</i> (sans) ·
      Acento = <i>WorldDiscovery One</i> (script, solo frases emotivas, sin números).</p>
      <p><b>Regla dura:</b> fotos/video <b>reales, NUNCA IA</b>; alta resolución; crop intencional;
      esquinas redondeadas; whitespace generoso; tono calmado y claro, sin urgencia.</p>
      <p class="g-ref">Detalle completo en <code>BRAND_REFERENCE.md</code>.</p>
    </div>
  </details>
  <details class="g-card"><summary>2 · Flujo de producción de contenido (por página)</summary>
    <div class="g-body"><ol>
      <li><b>Leer la página vieja</b> en WordPress (columna URL del board).</li>
      <li><b>Escribir el copy nuevo</b> con la voz de marca (claro, profundo, sin urgencia).</li>
      <li><b>Conseguir/solicitar media real</b> — foto o video (no IA), regla de marca correcta.</li>
      <li><b>Construir en Webflow</b> sobre los componentes globales (nav/footer/tokens).</li>
      <li><b>SEO:</b> title 30–65 car., meta description 120–160, 1 H1, alt text, 3+ links internos.</li>
      <li><b>Mapear el 301 redirect</b> de la URL vieja a la nueva (o al survivor si se consolida).</li>
    </ol>
    <p>El contenido se exporta a CSV (<code>SOTSI_Migration_Plan.csv</code>) y se edita vía
    Claude Code + MCP sobre <code>data/migration_plan.json</code>.</p></div>
  </details>
  <details class="g-card"><summary>3 · Definition of Done (checklist por página)</summary>
    <div class="g-body"><ul>
      <li><b>copy</b> — texto nuevo escrito y revisado, sin fechas muertas/cohortes cerradas.</li>
      <li><b>hero_media</b> — imagen/video hero real (no IA), ≥ alta resolución, crop intencional.</li>
      <li><b>images</b> — imágenes de cuerpo colocadas, con alt text.</li>
      <li><b>video</b> — video embebido donde aplique (video &gt; foto cuando sea posible).</li>
      <li><b>seo_title</b> / <b>seo_desc</b> — meta dentro de rango.</li>
      <li><b>redirects</b> — 301 de URL vieja registrado en el mapa.</li>
      <li>Responsive 320/375/768/1024/1440 · links/forms OK · sign-off Joel+Jose.</li>
    </ul></div>
  </details>
</div>"""


# ── HTML template ────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SOTSI + UHF · Plan de Migración Webflow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- Canela is a licensed font; Cormorant Garamond is the temporary web fallback -->
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator.min.css" rel="stylesheet">
<script src="https://unpkg.com/tabulator-tables@6.2.1/dist/js/tabulator.min.js"></script>
<style>
:root{
  --navy:#0E1631; --purple:#3C1951; --white:#FFFFFF;
  --periwinkle:#D2CCFD; --lilac:#E7D4F1; --lum-yellow:#FFEB45; --gold-yellow:#FED457;
  --bg:#f6f5fc; --surface:#fff; --text:#1a1730; --muted:#7a748f; --border:#e4e0f0;
  --success:#0ab39c; --danger:#f06548;
  --r:12px; --shadow:0 1px 3px rgba(14,22,49,.08); --shadow-h:0 8px 28px rgba(14,22,49,.16);
  --font:'Jost',system-ui,sans-serif; --hed:'Cormorant Garamond',Georgia,serif;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--hed);font-weight:600;letter-spacing:.2px}
a{color:var(--purple)}
.wrap{max-width:1320px;margin:0 auto;padding:0 24px}

/* header */
header.top{background:linear-gradient(135deg,var(--navy) 0%,var(--purple) 100%);color:#fff;padding:34px 0 30px;position:relative;overflow:hidden}
header.top::after{content:"";position:absolute;top:-40px;right:-30px;width:240px;height:240px;border-radius:50%;background:radial-gradient(circle,rgba(255,235,69,.22),transparent 70%)}
.brandline{display:flex;align-items:center;gap:14px;font-size:13px;letter-spacing:3px;text-transform:uppercase;opacity:.8}
.dot{width:8px;height:8px;border-radius:50%;background:var(--lum-yellow)}
header.top h1{font-size:clamp(28px,4vw,46px);color:#fff;margin:10px 0 4px}
header.top h1 em{color:var(--lum-yellow);font-style:italic}
.sub{opacity:.82;font-size:15px;max-width:680px}
.gen{position:absolute;right:24px;bottom:14px;font-size:12px;opacity:.6}

/* kpis */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(184px,1fr));gap:16px;margin:-26px 0 8px;position:relative;z-index:2}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:18px 20px;box-shadow:var(--shadow)}
.kpi-val{font-family:var(--hed);font-size:34px;font-weight:700;line-height:1;color:var(--navy)}
.kpi-done .kpi-val{color:var(--success)} .kpi-blocked .kpi-val{color:var(--danger)}
.kpi-label{font-weight:600;margin-top:6px;font-size:14px}
.kpi-sub{color:var(--muted);font-size:12px;margin-top:2px}

/* panels */
section.block{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:22px;margin:18px 0;box-shadow:var(--shadow)}
.block h2{font-size:22px;color:var(--navy);margin-bottom:14px}
.cols2{display:grid;grid-template-columns:1.1fr 1fr;gap:24px}
@media(max-width:880px){.cols2{grid-template-columns:1fr}}

/* bars */
.bar-row{margin-bottom:12px}
.bar-head{display:flex;justify-content:space-between;font-size:13px;font-weight:500;margin-bottom:5px}
.bar-num{color:var(--muted)}
.bar-track{height:9px;background:#ece9f6;border-radius:6px;overflow:hidden}
.bar-track.sm{height:6px;margin-top:8px}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--purple),#6a3a8f);border-radius:6px;transition:width .4s}

/* sprint tiles */
.sprints{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.sprint-tile{border:1px solid var(--border);border-left:4px solid var(--gold-yellow);border-radius:10px;padding:14px 16px;background:#fbfaff}
.sprint-id{font-family:var(--hed);font-size:17px;font-weight:600;color:var(--navy)}
.sprint-goal{font-size:12.5px;color:var(--muted);margin:6px 0 10px;min-height:34px}
.sprint-meta{display:flex;gap:12px;font-size:12px;color:var(--text);font-weight:500}

/* tabs */
.tabs{display:flex;gap:4px;margin:22px 0 0;flex-wrap:wrap}
.tab-btn{border:none;background:transparent;font-family:var(--font);font-size:14px;font-weight:600;color:var(--muted);padding:11px 18px;cursor:pointer;border-radius:10px 10px 0 0}
.tab-btn.active{color:var(--purple);background:var(--surface);border:1px solid var(--border);border-bottom:2px solid var(--surface);margin-bottom:-1px}
.tab-panel{display:none}.tab-panel.active{display:block}

/* filters */
.filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.filters select,.filters input{font-family:var(--font);font-size:13px;padding:8px 10px;border:1px solid var(--border);border-radius:8px;background:#fff;color:var(--text)}
.filters input{min-width:200px}
.f-clear{background:var(--navy);color:#fff;border:none;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer}
.f-count{margin-left:auto;color:var(--muted);font-size:13px}

/* badges */
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:.3px}
.st-backlog{background:#eceaf4;color:#6d6788}.st-design{background:#e6e1fb;color:#5b3b9e}
.st-content{background:#efe2f7;color:#7d2f9e}.st-build{background:#dde3f5;color:#2f4593}
.st-review{background:#fff2c9;color:#8a6a00}.st-done{background:#d2f5ee;color:#067a68}
.st-blocked{background:#fde0da;color:#b8341c}
.vd-keep{background:#d2f5ee;color:#067a68}.vd-improve{background:#dbe9ff;color:#2f5aa8}
.vd-rebuild{background:#fff2c9;color:#8a6a00}.vd-consolidate{background:#eceaf4;color:#6d6788}
.vd-drop{background:#fde0da;color:#b8341c}
.br-sotsi{background:var(--navy);color:#fff}.br-uhf{background:var(--purple);color:#fff}
.br-both{background:linear-gradient(90deg,var(--navy),var(--purple));color:#fff}

/* slide panel */
.overlay{position:fixed;inset:0;background:rgba(14,22,49,.4);opacity:0;pointer-events:none;transition:.25s;z-index:40}
.overlay.open{opacity:1;pointer-events:auto}
.panel{position:fixed;top:0;right:0;height:100%;width:min(560px,92vw);background:#fff;box-shadow:var(--shadow-h);transform:translateX(100%);transition:transform .28s cubic-bezier(.16,1,.3,1);z-index:50;overflow-y:auto}
.panel.open{transform:translateX(0)}
.panel-head{background:linear-gradient(135deg,var(--navy),var(--purple));color:#fff;padding:22px 24px}
.panel-head h3{color:#fff;font-size:24px}
.panel-close{position:absolute;top:16px;right:18px;background:rgba(255,255,255,.15);border:none;color:#fff;width:32px;height:32px;border-radius:50%;font-size:18px;cursor:pointer}
.panel-body{padding:22px 24px}
.pb-sec{margin-bottom:20px}
.pb-sec h4{font-family:var(--font);font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px}
.url-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px}
.url-row code{background:#f3f1fa;padding:4px 8px;border-radius:6px;word-break:break-all}
.arrow{color:var(--gold-yellow);font-weight:700}
.ck-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.ck{display:flex;align-items:center;gap:8px;font-size:13px}
.ck .box{width:16px;height:16px;border-radius:4px;border:2px solid var(--border)}
.ck.on .box{background:var(--success);border-color:var(--success)}
.hrs-tbl{width:100%;border-collapse:collapse;font-size:13px}
.hrs-tbl td{padding:5px 4px;border-bottom:1px solid var(--border)}
.hrs-tbl tr:last-child td{border-top:2px solid var(--navy);border-bottom:none;font-weight:700}
.notes{background:#fbfaff;border:1px solid var(--border);border-radius:8px;padding:12px;font-size:13px;white-space:pre-wrap}
.lk-btn{display:inline-block;background:var(--gold-yellow);color:var(--navy);text-decoration:none;font-weight:600;font-size:13px;padding:8px 14px;border-radius:8px;margin-right:8px}

/* guide */
.guide{max-width:840px}
.g-card{border:1px solid var(--border);border-radius:10px;margin-bottom:12px;background:#fbfaff}
.g-card summary{cursor:pointer;font-family:var(--hed);font-size:19px;font-weight:600;color:var(--navy);padding:14px 18px}
.g-body{padding:0 18px 16px;font-size:14px}
.g-body p{margin:8px 0}.g-body ol,.g-body ul{margin:8px 0 8px 20px}.g-body li{margin:4px 0}
.g-ref{color:var(--muted);font-size:12.5px}
.sw-grid{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.sw{display:flex;align-items:center;gap:7px;font-size:12px;border:1px solid var(--border);border-radius:8px;padding:5px 9px;background:#fff}
.sw-box{width:18px;height:18px;border-radius:4px;border:1px solid rgba(0,0,0,.1)}
.sw-hex{color:var(--muted);font-family:monospace}
code{font-family:ui-monospace,Menlo,monospace;font-size:.92em}
footer{text-align:center;color:var(--muted);font-size:12px;padding:30px 0 40px}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <div class="brandline"><span class="dot"></span>Seat of the Soul · Universal Human · 22D Marketing</div>
  <h1>Plan de Migración a <em>Webflow</em></h1>
  <div class="sub">Tablero de trabajo del equipo — qué se mantiene, mejora, reconstruye o elimina, con horas por rol y avance por sprint.</div>
  <div class="gen">Actualizado: __GENERATED_AT__</div>
</div></header>

<div class="wrap">
  <div class="kpis">__KPI_CARDS__</div>

  <div class="tabs">
    <button class="tab-btn active" data-tab="overview">Resumen</button>
    <button class="tab-btn" data-tab="board">Board (110)</button>
    <button class="tab-btn" data-tab="guide">Guía del equipo</button>
  </div>

  <div class="tab-panel active" id="tab-overview">
    <section class="block"><h2>Sprints</h2><div class="sprints">__SPRINT_TILES__</div></section>
    <section class="block"><h2>Horas por rol — avance</h2>__ROLE_BARS__
      <p style="color:var(--muted);font-size:12.5px;margin-top:10px">Barras = horas <b>done</b> sobre horas totales estimadas (excluye drops, que solo llevan 301 redirect).</p>
    </section>
  </div>

  <div class="tab-panel" id="tab-board">
    <section class="block">
      <div class="filters">
        <input id="f-search" placeholder="Buscar título o slug…">
        <select id="f-status"><option value="">Estatus: todos</option></select>
        <select id="f-sprint"><option value="">Sprint: todos</option></select>
        <select id="f-verdict"><option value="">Veredicto: todos</option></select>
        <select id="f-brand"><option value="">Marca: todas</option></select>
        <select id="f-cat"><option value="">Categoría: todas</option></select>
        <button class="f-clear" id="f-clear">Limpiar</button>
        <span class="f-count" id="f-count"></span>
      </div>
      <div id="board"></div>
    </section>
  </div>

  <div class="tab-panel" id="tab-guide">
    <section class="block"><h2>Guía del equipo</h2>__TEAM_GUIDE__</section>
  </div>
</div>

<div class="overlay" id="overlay"></div>
<aside class="panel" id="panel"><div id="panel-content"></div></aside>

<footer>SOTSI + UHF · generado por <code>build_migration_dashboard.py</code> · data en <code>data/migration_plan.json</code></footer>

<script>
const PAGES = __PAGES_JSON__;
const SPRINTS = __SPRINTS_JSON__;
const ROLES = ["design","content","media","build","review"];
const ROLE_ES = {design:"Diseño",content:"Contenido",media:"Video/Imagen",build:"Build Webflow",review:"Revisión"};
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const cap = s => s ? s[0].toUpperCase()+s.slice(1) : s;
const pageHours = p => ROLES.reduce((a,r)=>a+(p.role_hours[r]||0),0);

/* tabs */
document.querySelectorAll(".tab-btn").forEach(b=>b.onclick=()=>{
  document.querySelectorAll(".tab-btn").forEach(x=>x.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(x=>x.classList.remove("active"));
  b.classList.add("active");
  document.getElementById("tab-"+b.dataset.tab).classList.add("active");
  if(b.dataset.tab==="board" && window.table){ setTimeout(()=>window.table.redraw(true),30); }
});

/* filters: populate selects */
function opts(id, vals, labelFn){
  const sel=document.getElementById(id);
  vals.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=labelFn?labelFn(v):v;sel.appendChild(o);});
}
opts("f-status",[...new Set(PAGES.map(p=>p.status))].sort(),cap);
opts("f-sprint",[...new Set(PAGES.map(p=>p.sprint))].sort((a,b)=>a-b),v=>"Sprint "+v);
opts("f-verdict",[...new Set(PAGES.map(p=>p.verdict))].sort(),cap);
opts("f-brand",[...new Set(PAGES.map(p=>p.brand))].sort(),v=>v.toUpperCase());
opts("f-cat",[...new Set(PAGES.map(p=>p.category))].sort());

/* tabulator board */
const badge=(cls,txt)=>`<span class="badge ${cls}">${esc(txt)}</span>`;
const table=new Tabulator("#board",{
  data:PAGES, layout:"fitColumns", height:"calc(100vh - 300px)", reactiveData:false,
  columns:[
    {title:"Estatus",field:"status",width:108,formatter:c=>badge("st-"+c.getValue(),cap(c.getValue()))},
    {title:"Título",field:"title",minWidth:200,formatter:c=>`<b>${esc(c.getValue())}</b><br><span style="color:#7a748f;font-size:11px">/${esc(c.getData().slug)}</span>`},
    {title:"Marca",field:"brand",width:78,hozAlign:"center",formatter:c=>badge("br-"+c.getValue(),c.getValue().toUpperCase())},
    {title:"Categoría",field:"category",width:130},
    {title:"Veredicto",field:"verdict",width:118,formatter:c=>badge("vd-"+c.getValue(),cap(c.getValue()))},
    {title:"Sprint",field:"sprint",width:74,hozAlign:"center"},
    {title:"Checklist",field:"slug",width:96,hozAlign:"center",formatter:c=>{
       const ck=c.getData().content_checklist;const keys=Object.keys(ck);const n=keys.filter(k=>ck[k]).length;
       const pct=Math.round(n/keys.length*100);
       return `<div style="font-size:11px">${n}/${keys.length}</div><div class="bar-track sm" style="margin-top:3px"><div class="bar-fill" style="width:${pct}%"></div></div>`;}},
    {title:"Horas",field:"slug",width:72,hozAlign:"right",formatter:c=>pageHours(c.getData())+"h"},
  ],
});
window.table=table;
table.on("rowClick",(e,row)=>openPanel(row.getData()));

function applyFilters(){
  const q=document.getElementById("f-search").value.toLowerCase();
  const f={status:"f-status",sprint:"f-sprint",verdict:"f-verdict",brand:"f-brand",category:"f-cat"};
  table.setFilter(d=>{
    if(q && !(d.title.toLowerCase().includes(q)||d.slug.toLowerCase().includes(q))) return false;
    for(const [field,id] of Object.entries(f)){
      const v=document.getElementById(id).value;
      if(v!=="" && String(d[field])!==String(v)) return false;
    }
    return true;
  });
  setTimeout(()=>{document.getElementById("f-count").textContent="Mostrando "+table.getDataCount("active")+" de "+PAGES.length;},50);
}
["f-search","f-status","f-sprint","f-verdict","f-brand","f-cat"].forEach(id=>{
  const el=document.getElementById(id);el.addEventListener(id==="f-search"?"input":"change",applyFilters);});
document.getElementById("f-clear").onclick=()=>{
  ["f-search","f-status","f-sprint","f-verdict","f-brand","f-cat"].forEach(id=>document.getElementById(id).value="");applyFilters();};
applyFilters();

/* slide panel */
const overlay=document.getElementById("overlay"),panel=document.getElementById("panel");
function closePanel(){overlay.classList.remove("open");panel.classList.remove("open");}
overlay.onclick=closePanel;
document.addEventListener("keydown",e=>{if(e.key==="Escape")closePanel();});

function openPanel(d){
  const ck=d.content_checklist;
  const ckHtml=Object.keys(ck).map(k=>`<div class="ck ${ck[k]?"on":""}"><span class="box"></span>${k}</div>`).join("");
  const hrsRows=ROLES.map(r=>`<tr><td>${ROLE_ES[r]}</td><td style="text-align:right">${d.role_hours[r]||0}h</td></tr>`).join("");
  const links=[];
  if(d.links.figma)links.push(`<a class="lk-btn" href="${esc(d.links.figma)}" target="_blank">Figma ↗</a>`);
  if(d.links.webflow)links.push(`<a class="lk-btn" href="${esc(d.links.webflow)}" target="_blank">Webflow ↗</a>`);
  const cons=d.consolidate_into?`<div class="pb-sec"><h4>Se consolida en</h4><code>/${esc(d.consolidate_into)}</code></div>`:"";
  panel.innerHTML=`
   <div class="panel-head">
     <button class="panel-close" onclick="closePanel()">×</button>
     <div style="display:flex;gap:6px;margin-bottom:8px">
       ${badge("br-"+d.brand,d.brand.toUpperCase())} ${badge("vd-"+d.verdict,cap(d.verdict))} ${badge("st-"+d.status,cap(d.status))}
     </div>
     <h3>${esc(d.title)}</h3>
   </div>
   <div class="panel-body">
     <div class="pb-sec"><h4>URL  vieja → nueva</h4>
       <div class="url-row"><code>${esc(d.url.replace("https://",""))}</code><span class="arrow">→</span><code>${esc(d.new_path)}</code></div></div>
     <div class="pb-sec"><h4>Categoría / Sprint / Arquetipo</h4>
       <div style="font-size:13px">${esc(d.category)} · Sprint ${d.sprint} · ${esc(d.archetype)}</div></div>
     ${cons}
     <div class="pb-sec"><h4>Content checklist</h4><div class="ck-grid">${ckHtml}</div></div>
     <div class="pb-sec"><h4>Horas estimadas por rol</h4>
       <table class="hrs-tbl">${hrsRows}<tr><td>Total</td><td style="text-align:right">${pageHours(d)}h</td></tr></table></div>
     ${d.notes?`<div class="pb-sec"><h4>Notas</h4><div class="notes">${esc(d.notes)}</div></div>`:""}
     ${links.length?`<div class="pb-sec"><h4>Enlaces</h4>${links.join("")}</div>`:""}
     <div class="pb-sec"><h4>Slug</h4><code>${esc(d.slug)}</code></div>
   </div>`;
  overlay.classList.add("open");panel.classList.add("open");
}
</script>
</body>
</html>
"""


def main():
    plan = load_plan(DATA_IN)
    pages = plan["pages"]
    sprints = plan["sprints"]
    meta = compute_meta(pages, sprints)

    out = (HTML_TEMPLATE
           .replace("__GENERATED_AT__", meta["generated_at"])
           .replace("__KPI_CARDS__", kpi_cards(meta))
           .replace("__ROLE_BARS__", role_bars(meta))
           .replace("__SPRINT_TILES__", sprint_tiles(pages, sprints, meta))
           .replace("__TEAM_GUIDE__", team_guide())
           .replace("__PAGES_JSON__", json.dumps(pages, ensure_ascii=False))
           .replace("__SPRINTS_JSON__", json.dumps(sprints, ensure_ascii=False)))

    HTML_OUT.write_text(out, encoding="utf-8")
    COPY_TO.write_text(out, encoding="utf-8")
    print(f"Wrote {HTML_OUT.name} + {COPY_TO.name}  "
          f"({meta['total_pages']} páginas, {meta['pct_done']}% done, "
          f"{meta['by_status']['blocked']} bloqueadas, {meta['total_hours']:g}h totales)")


if __name__ == "__main__":
    main()
