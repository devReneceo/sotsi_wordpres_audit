#!/usr/bin/env python3
"""
Build the SOTSI SEO client deliverable dashboard from the audit JSON.

Inputs:
    data/seo_audit_YYYY-MM-DD.json   ← required (from seo_audit.py)

Output:
    seo_dashboard.html               ← single self-contained file, no build step

The dashboard mirrors migration_dashboard.html's UHF style (Jost + Cormorant
Garamond) for visual consistency in the client-facing deliverable.

Bilingual ESP/EN labels (toggle in-page) per [[joel-working-style]].
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "seo_dashboard.html")


def load_latest_audit() -> dict:
    """Pick the most recent seo_audit_*.json so the dashboard always renders the
    freshest crawl without command-line plumbing."""
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("seo_audit_") and f.endswith(".json") and ".progress" not in f]
    if not files:
        print("no seo_audit_*.json in data/ — run seo_audit.py first", file=sys.stderr)
        sys.exit(1)
    files.sort()
    path = os.path.join(DATA_DIR, files[-1])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def summarize(records: list[dict]) -> dict:
    """Build the rollup numbers shown in the overview cards."""
    by_sev = Counter(r["audit_severity"] for r in records)
    by_sitemap = Counter(r["sitemap"] for r in records)
    track_ga4 = sum(1 for r in records if r["ga4_ids"])
    track_ua = sum(1 for r in records if r["ua_ids"])
    track_fb = sum(1 for r in records if r["fb_pixel_ids"])
    track_gtm = sum(1 for r in records if r["gtm_ids"])
    track_hj = sum(1 for r in records if r["hotjar_ids"])
    no_h1 = sum(1 for r in records if r["h1_count"] == 0 and r["status"] == 200)
    no_meta = sum(1 for r in records if not r["meta_description"] and r["status"] == 200)
    title_len_bad = sum(1 for r in records if r["title"] and (r["title_len"] < 25 or r["title_len"] > 65))
    total_imgs = sum(r["imgs_total"] for r in records)
    no_alt = sum(r["imgs_no_alt"] for r in records)
    word_counts = sorted([r["word_count_approx"] for r in records if r["word_count_approx"] > 0])
    median_words = word_counts[len(word_counts) // 2] if word_counts else 0
    errors = [r for r in records if r["status"] != 200]
    unique_ga4 = sorted({r["ga4_ids"] for r in records if r["ga4_ids"]})
    unique_ua = sorted({r["ua_ids"] for r in records if r["ua_ids"]})
    unique_fb = sorted({r["fb_pixel_ids"] for r in records if r["fb_pixel_ids"]})
    return {
        "by_sev": by_sev,
        "by_sitemap": by_sitemap,
        "track": {"GA4": (track_ga4, unique_ga4), "UA": (track_ua, unique_ua),
                  "GTM": (track_gtm, []), "FB Pixel": (track_fb, unique_fb),
                  "Hotjar": (track_hj, [])},
        "gaps": {"no_h1": no_h1, "no_meta_desc": no_meta, "title_len_bad": title_len_bad,
                 "imgs_no_alt": no_alt, "imgs_total": total_imgs},
        "median_words": median_words,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────────────
# HTML rendering — keep it self-contained: inline CSS + JS, vanilla DOM,
# no build step. CSP-friendly with nonce if you embed in WP later.
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es" data-lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SOTSI — SEO Audit · seatofthesoul.com</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --font:'Jost',system-ui,sans-serif; --hed:'Cormorant Garamond',Georgia,serif;
    --bg:#f7f5f2; --surface:#ffffff; --ink:#1c2333; --muted:#6b7280;
    --border:#e6e4df; --accent:#405189; --gold:#c19a4a;
    --green:#067a68; --amber:#c08a1f; --red:#b8341c; --grey:#7a748f;
  }}
  *{{box-sizing:border-box}}
  body{{font-family:var(--font);background:var(--bg);color:var(--ink);line-height:1.5;margin:0;-webkit-font-smoothing:antialiased}}
  h1,h2,h3{{font-family:var(--hed);font-weight:600;letter-spacing:.2px;margin:0}}
  a{{color:var(--accent)}}
  /* Layout */
  .hero{{background:linear-gradient(135deg,var(--ink) 0%,#2a3247 100%);color:#fff;padding:48px 32px 56px;border-bottom:4px solid var(--gold)}}
  .hero-inner{{max-width:1240px;margin:0 auto;display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap}}
  .hero h1{{font-size:clamp(28px,4vw,42px);color:#fff;line-height:1.1}}
  .hero .crumb{{font-size:12px;letter-spacing:2.5px;text-transform:uppercase;color:var(--gold);font-weight:600;margin-bottom:10px}}
  .hero .meta{{color:#cbd1e0;font-size:14px;margin-top:8px}}
  .lang{{display:flex;gap:0;border:1px solid rgba(255,255,255,.25);border-radius:999px;overflow:hidden;font-size:12px;font-weight:600}}
  .lang button{{background:transparent;border:none;color:#cbd1e0;padding:6px 14px;cursor:pointer;font-family:inherit;letter-spacing:.06em}}
  .lang button.on{{background:var(--gold);color:var(--ink)}}
  .wrap{{max-width:1240px;margin:0 auto;padding:32px}}
  /* Cards */
  .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:32px}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px 20px;box-shadow:0 1px 2px rgba(14,22,49,.04)}}
  .card .lbl{{font-size:10.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}}
  .card .v{{font-family:var(--hed);font-weight:700;font-size:36px;line-height:1;margin:6px 0 4px;color:var(--ink)}}
  .card .s{{font-size:12.5px;color:var(--muted)}}
  .card.warn .v{{color:var(--red)}}
  .card.ok .v{{color:var(--green)}}
  .card.notice .v{{color:var(--amber)}}
  /* Tabs */
  .tabs{{display:flex;gap:0;border-bottom:1px solid var(--border);margin-bottom:18px;overflow-x:auto;scrollbar-width:thin}}
  .tab{{background:none;border:none;padding:11px 18px;font-family:var(--font);font-size:13.5px;font-weight:600;color:var(--muted);cursor:pointer;position:relative;letter-spacing:.02em;white-space:nowrap}}
  .tab:hover{{color:var(--ink)}}
  .tab.on{{color:var(--accent)}}
  .tab.on::after{{content:"";position:absolute;left:14px;right:14px;bottom:-1px;height:2.5px;background:var(--accent);border-radius:2px}}
  /* Panels */
  .panel{{display:none}}
  .panel.on{{display:block}}
  /* Filters */
  .filters{{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}}
  .filters input,.filters select{{border:1px solid var(--border);border-radius:8px;padding:7px 11px;font-family:inherit;font-size:13px;background:#fff}}
  .filters input:focus,.filters select:focus{{outline:2px solid rgba(64,81,137,.2);border-color:var(--accent)}}
  .filters .count{{margin-left:auto;font-size:12px;color:var(--muted)}}
  /* Tables */
  table{{width:100%;border-collapse:collapse;background:var(--surface);border-radius:10px;overflow:hidden;border:1px solid var(--border);font-size:13px}}
  th{{background:#fafaf7;text-align:left;padding:10px 12px;font-weight:600;color:var(--muted);text-transform:uppercase;font-size:10.5px;letter-spacing:.06em;border-bottom:1px solid var(--border);cursor:pointer;user-select:none}}
  th.sort-asc::after{{content:" ▲";color:var(--accent)}}
  th.sort-desc::after{{content:" ▼";color:var(--accent)}}
  td{{padding:10px 12px;border-bottom:1px solid #f3f1ed;vertical-align:top}}
  tr:hover td{{background:#fcfaf6}}
  td.url{{font-family:'Courier New',monospace;font-size:11.5px;color:var(--accent);max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  td.title{{max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  td.notes{{font-size:11.5px;color:var(--muted);max-width:260px}}
  .sev{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:700;letter-spacing:.06em}}
  .sev.CRITICAL{{background:#ffd8d2;color:var(--red)}}
  .sev.HIGH{{background:#fde2c8;color:var(--red)}}
  .sev.MEDIUM{{background:#fdefc8;color:var(--amber)}}
  .sev.LOW{{background:#d2f5ee;color:var(--green)}}
  /* Tracking grid */
  .track-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-bottom:24px}}
  .track-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px}}
  .track-card.present{{border-left:4px solid var(--green)}}
  .track-card.absent{{border-left:4px solid var(--grey)}}
  .track-card.legacy{{border-left:4px solid var(--red)}}
  .track-card .name{{font-weight:700;font-size:14px;color:var(--ink);margin-bottom:6px}}
  .track-card .stat{{font-size:12.5px;color:var(--muted)}}
  .track-card .id{{font-family:'Courier New',monospace;font-size:11.5px;color:var(--accent);margin-top:6px;word-break:break-all}}
  /* Issue cards (Issues tab) */
  .issue-list{{display:flex;flex-direction:column;gap:10px}}
  .issue-row{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap}}
  .issue-row .meta{{display:flex;flex-direction:column;gap:3px}}
  .issue-row .meta b{{font-size:14px;color:var(--ink)}}
  .issue-row .n{{font-family:var(--hed);font-size:30px;font-weight:700;color:var(--accent);line-height:1}}
  /* i18n */
  [data-en]{{display:none}}
  body[data-lang="en"] [data-en]{{display:inline}}
  body[data-lang="en"] [data-es]{{display:none}}
  /* Compact / responsive */
  @media(max-width:760px){{
    .wrap{{padding:18px}}
    .hero{{padding:36px 18px 40px}}
    table{{font-size:12px}}
    .card .v{{font-size:28px}}
  }}
</style>
</head>
<body data-lang="es">
<header class="hero">
  <div class="hero-inner">
    <div>
      <div class="crumb">SOTSI · SEO Audit</div>
      <h1>seatofthesoul.com</h1>
      <p class="meta">
        <span data-es>Auditoría técnica del sitio WordPress activo · {n_urls} URLs revisadas · {audit_date}</span>
        <span data-en>Technical audit of the live WordPress site · {n_urls} URLs reviewed · {audit_date}</span>
      </p>
    </div>
    <div class="lang" role="tablist">
      <button id="lang-es" class="on" onclick="setLang('es')">ES</button>
      <button id="lang-en" onclick="setLang('en')">EN</button>
    </div>
  </div>
</header>

<main class="wrap">

  <!-- Overview cards -->
  <section class="cards">
    <div class="card"><div class="lbl"><span data-es>URLs totales</span><span data-en>Total URLs</span></div><div class="v">{n_urls}</div><div class="s"><span data-es>páginas + posts + chapters</span><span data-en>pages + posts + chapters</span></div></div>
    <div class="card warn"><div class="lbl"><span data-es>Crítico + alto</span><span data-en>Critical + high</span></div><div class="v">{n_crit_high}</div><div class="s"><span data-es>requieren atención inmediata</span><span data-en>need immediate attention</span></div></div>
    <div class="card notice"><div class="lbl"><span data-es>Sin meta description</span><span data-en>Missing meta description</span></div><div class="v">{n_no_meta}</div><div class="s"><span data-es>{pct_no_meta}% del sitio</span><span data-en>{pct_no_meta}% of the site</span></div></div>
    <div class="card notice"><div class="lbl"><span data-es>Sin H1</span><span data-en>Missing H1</span></div><div class="v">{n_no_h1}</div><div class="s"><span data-es>incluyendo home page</span><span data-en>including the home page</span></div></div>
    <div class="card warn"><div class="lbl"><span data-es>Imágenes sin alt</span><span data-en>Images without alt</span></div><div class="v">{n_no_alt}</div><div class="s"><span data-es>de {n_imgs_total} totales ({pct_no_alt}%)</span><span data-en>of {n_imgs_total} total ({pct_no_alt}%)</span></div></div>
    <div class="card ok"><div class="lbl"><span data-es>Cobertura tracking</span><span data-en>Tracking coverage</span></div><div class="v">{pct_tracking}%</div><div class="s">GA4 + FB Pixel</div></div>
  </section>

  <!-- Tabs -->
  <nav class="tabs" role="tablist">
    <button class="tab on" data-tab="overview"><span data-es>Resumen</span><span data-en>Overview</span></button>
    <button class="tab" data-tab="pages">📄 <span data-es>Páginas ({n_pages})</span><span data-en>Pages ({n_pages})</span></button>
    <button class="tab" data-tab="posts">📝 <span data-es>Blog posts ({n_posts})</span><span data-en>Blog posts ({n_posts})</span></button>
    <button class="tab" data-tab="issues">🔍 <span data-es>Issues por tipo</span><span data-en>Issues by type</span></button>
    <button class="tab" data-tab="tracking">🎯 <span data-es>Tracking</span><span data-en>Tracking</span></button>
    <button class="tab" data-tab="analytics">📈 <span data-es>Analytics (pendiente)</span><span data-en>Analytics (pending)</span></button>
  </nav>

  <!-- Overview panel -->
  <section class="panel on" data-p="overview">
    <h2 style="margin-bottom:14px"><span data-es>Estado general del sitio</span><span data-en>Overall site health</span></h2>
    <p style="max-width:760px;color:var(--muted);margin-bottom:18px">
      <span data-es>Auditoría realizada el {audit_date} contra {n_urls} URLs descubiertas en el sitemap. Lo que sigue son los hallazgos principales priorizados por impacto SEO.</span>
      <span data-en>Audit performed on {audit_date} against {n_urls} URLs discovered in the sitemap. The findings below are prioritized by SEO impact.</span>
    </p>
    <div class="issue-list">{issue_rows}</div>
  </section>

  <!-- Pages panel -->
  <section class="panel" data-p="pages">
    <div class="filters">
      <input id="f-pages" placeholder="Buscar URL o título…" oninput="filterTable('t-pages', this.value)">
      <select id="sv-pages" onchange="filterSeverity('t-pages', this.value)">
        <option value="">Severity: todas</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>
      <span class="count" id="c-pages">{n_pages} pages</span>
    </div>
    <div style="overflow:auto;max-height:70vh">
      <table id="t-pages">
        <thead><tr>
          <th data-key="audit_severity">Severity</th>
          <th data-key="url">URL</th>
          <th data-key="title">Title</th>
          <th data-key="word_count_approx">Words</th>
          <th data-key="h1_count">H1</th>
          <th data-key="imgs_no_alt">No-alt imgs</th>
          <th data-key="audit_notes">Notes</th>
        </tr></thead>
        <tbody>{rows_pages}</tbody>
      </table>
    </div>
  </section>

  <!-- Posts panel -->
  <section class="panel" data-p="posts">
    <div class="filters">
      <input id="f-posts" placeholder="Buscar URL o título…" oninput="filterTable('t-posts', this.value)">
      <select id="sv-posts" onchange="filterSeverity('t-posts', this.value)">
        <option value="">Severity: todas</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>
      <span class="count" id="c-posts">{n_posts} posts</span>
    </div>
    <div style="overflow:auto;max-height:70vh">
      <table id="t-posts">
        <thead><tr>
          <th data-key="audit_severity">Severity</th>
          <th data-key="url">URL</th>
          <th data-key="title">Title</th>
          <th data-key="word_count_approx">Words</th>
          <th data-key="h1_count">H1</th>
          <th data-key="imgs_no_alt">No-alt imgs</th>
          <th data-key="audit_notes">Notes</th>
        </tr></thead>
        <tbody>{rows_posts}</tbody>
      </table>
    </div>
  </section>

  <!-- Issues by type -->
  <section class="panel" data-p="issues">
    <h2 style="margin-bottom:14px"><span data-es>Issues agrupados por tipo</span><span data-en>Issues grouped by type</span></h2>
    <p style="color:var(--muted);max-width:760px;margin-bottom:18px">
      <span data-es>Cada issue ya se convirtió en una task en 22d-trello, asignada por surface (Christopher=SEO, Joel/Jose=tech, Luna=content). Total estimado: {total_hours}h.</span>
      <span data-en>Each issue was already converted into a task in 22d-trello, assigned by surface (Christopher=SEO, Joel/Jose=tech, Luna=content). Total estimate: {total_hours}h.</span>
    </p>
    <div class="issue-list">{issue_rows_full}</div>
  </section>

  <!-- Tracking panel -->
  <section class="panel" data-p="tracking">
    <h2 style="margin-bottom:14px"><span data-es>Stack de tracking instalado</span><span data-en>Tracking stack installed</span></h2>
    <div class="track-grid">{track_cards}</div>
    <h3 style="margin:18px 0 8px;font-family:var(--font);font-size:14px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em">
      <span data-es>Recomendaciones para Webflow</span><span data-en>Webflow migration recommendations</span>
    </h3>
    <ul style="line-height:1.7;color:var(--ink)">
      <li><span data-es><b>Solo GA4</b> — Universal Analytics dejó de procesar datos en julio 2023, no hay razón para migrar el código viejo.</span><span data-en><b>GA4 only</b> — Universal Analytics stopped processing data in July 2023; no reason to carry the legacy code.</span></li>
      <li><span data-es><b>Confirmar Facebook Pixel</b> con el cliente — ¿la cuenta de ads sigue activa? ¿qué eventos de conversión necesitamos?</span><span data-en><b>Confirm Facebook Pixel</b> with client — is the ad account still active? what conversion events do we need?</span></li>
      <li><span data-es><b>Implementar Google Tag Manager</b> en Webflow — unifica todos los tags (GA4, FB Pixel, futuros) en un solo contenedor mantenible.</span><span data-en><b>Implement Google Tag Manager</b> in Webflow — unifies all tags (GA4, FB Pixel, future ones) into one maintainable container.</span></li>
      <li><span data-es><b>Verificar Google Search Console</b> — ninguna meta de verificación detectada; conectar la propiedad para poder ver impressions, clicks y queries reales.</span><span data-en><b>Verify Google Search Console</b> — no verification meta detected; connect the property to see real impressions, clicks, queries.</span></li>
    </ul>
  </section>

  <!-- Analytics placeholder -->
  <section class="panel" data-p="analytics">
    <h2 style="margin-bottom:14px"><span data-es>Análisis de tráfico real (pendiente)</span><span data-en>Real traffic analysis (pending)</span></h2>
    <p style="color:var(--muted);max-width:760px;margin-bottom:24px">
      <span data-es>Para mostrar al cliente cuánto tráfico tuvo cada página / post hace falta el export de Google Analytics 4 y Search Console. Una vez subido el CSV, esta vista cruza el rendimiento real con los hallazgos técnicos del audit.</span>
      <span data-en>To show the client how much traffic each page/post received, the Google Analytics 4 and Search Console exports are needed. Once you upload the CSV, this view crosses real performance with the technical audit findings.</span>
    </p>
    <div class="track-grid">
      <div class="track-card absent">
        <div class="name">Google Analytics 4</div>
        <div class="stat"><span data-es>Pendiente:</span><span data-en>Pending:</span></div>
        <ul style="margin:8px 0 0 18px;font-size:12.5px;color:var(--muted);line-height:1.6">
          <li>Reports → Engagement → <b>Pages and screens</b></li>
          <li><span data-es>Rango: últimos 90 días</span><span data-en>Range: last 90 days</span></li>
          <li><span data-es>Exportar como CSV</span><span data-en>Export as CSV</span></li>
        </ul>
      </div>
      <div class="track-card absent">
        <div class="name">Google Search Console</div>
        <div class="stat"><span data-es>Pendiente:</span><span data-en>Pending:</span></div>
        <ul style="margin:8px 0 0 18px;font-size:12.5px;color:var(--muted);line-height:1.6">
          <li>Performance → Search results → <b>Pages</b></li>
          <li><span data-es>Rango: últimos 3 meses</span><span data-en>Range: last 3 months</span></li>
          <li><span data-es>Métricas: clicks, impressions, CTR, position</span><span data-en>Metrics: clicks, impressions, CTR, position</span></li>
          <li><span data-es>Exportar como CSV</span><span data-en>Export as CSV</span></li>
        </ul>
      </div>
    </div>
  </section>

  <footer style="margin-top:40px;padding-top:18px;border-top:1px solid var(--border);color:var(--muted);font-size:11.5px">
    <span data-es>Audit generado por <code>seo_audit.py</code> · datos crudos en <code>data/seo_audit_{audit_date}.csv</code> · Tasks ya creadas en 22d-trello</span>
    <span data-en>Audit generated by <code>seo_audit.py</code> · raw data in <code>data/seo_audit_{audit_date}.csv</code> · Tasks already created in 22d-trello</span>
  </footer>
</main>

<script>
  /* Tabs */
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('on'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('on'));
    t.classList.add('on');
    document.querySelector('.panel[data-p="' + t.dataset.tab + '"]').classList.add('on');
  }}));

  /* Language toggle */
  function setLang(l) {{
    document.body.dataset.lang = l;
    document.getElementById('lang-es').classList.toggle('on', l === 'es');
    document.getElementById('lang-en').classList.toggle('on', l === 'en');
  }}

  /* Filter table by text */
  function filterTable(tid, q) {{
    q = (q || '').toLowerCase();
    const tbl = document.getElementById(tid);
    let shown = 0;
    tbl.querySelectorAll('tbody tr').forEach(tr => {{
      const txt = tr.textContent.toLowerCase();
      const ok = !q || txt.includes(q);
      tr.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    const cId = 'c-' + tid.split('-')[1];
    const c = document.getElementById(cId);
    if (c) c.textContent = shown + ' shown';
  }}
  function filterSeverity(tid, sev) {{
    const tbl = document.getElementById(tid);
    let shown = 0;
    tbl.querySelectorAll('tbody tr').forEach(tr => {{
      const trSev = tr.dataset.sev;
      const ok = !sev || trSev === sev;
      tr.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    const cId = 'c-' + tid.split('-')[1];
    const c = document.getElementById(cId);
    if (c) c.textContent = shown + ' shown';
  }}

  /* Sortable headers */
  document.querySelectorAll('table th').forEach(th => th.addEventListener('click', () => {{
    const key = th.dataset.key;
    if (!key) return;
    const tbody = th.closest('table').querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const asc = !th.classList.contains('sort-asc');
    th.parentNode.querySelectorAll('th').forEach(x => x.classList.remove('sort-asc', 'sort-desc'));
    th.classList.add(asc ? 'sort-asc' : 'sort-desc');
    rows.sort((a, b) => {{
      const av = a.dataset[key] || '';
      const bv = b.dataset[key] || '';
      const an = Number(av), bn = Number(bv);
      const numeric = !isNaN(an) && !isNaN(bn) && av !== '' && bv !== '';
      const cmp = numeric ? an - bn : av.localeCompare(bv);
      return asc ? cmp : -cmp;
    }});
    rows.forEach(r => tbody.appendChild(r));
  }}));
</script>
</body>
</html>
"""


def render_row(rec: dict) -> str:
    """One <tr> per URL, with data-sev so we can filter by severity in pure JS."""
    sev = rec["audit_severity"]
    url = rec["url"]
    title = (rec["title"] or "—").replace("<", "&lt;").replace(">", "&gt;")
    notes = (rec["audit_notes"] or "—").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<tr data-sev="{sev}" '
        f'data-audit_severity="{["LOW","MEDIUM","HIGH","CRITICAL"].index(sev)}" '
        f'data-url="{url}" data-title="{title}" '
        f'data-word_count_approx="{rec["word_count_approx"]}" '
        f'data-h1_count="{rec["h1_count"]}" '
        f'data-imgs_no_alt="{rec["imgs_no_alt"]}" '
        f'data-audit_notes="{notes}">'
        f'<td><span class="sev {sev}">{sev}</span></td>'
        f'<td class="url" title="{url}"><a href="{url}" target="_blank" rel="noopener">{url}</a></td>'
        f'<td class="title" title="{title}">{title}</td>'
        f'<td>{rec["word_count_approx"]}</td>'
        f'<td>{rec["h1_count"]}</td>'
        f'<td>{rec["imgs_no_alt"]}/{rec["imgs_total"]}</td>'
        f'<td class="notes">{notes}</td>'
        f'</tr>'
    )


def render_track_card(name: str, count: int, total: int, ids: list[str], is_legacy: bool = False) -> str:
    if count == 0:
        cls = "absent"
        body = '<div class="stat">Not detected</div>'
    elif is_legacy:
        cls = "legacy"
        body = f'<div class="stat">{count}/{total} pages — <b>LEGACY (sunset)</b></div>'
        if ids:
            body += f'<div class="id">{"|".join(ids)}</div>'
    else:
        cls = "present"
        body = f'<div class="stat">{count}/{total} pages</div>'
        if ids:
            body += f'<div class="id">{"|".join(ids)}</div>'
    return f'<div class="track-card {cls}"><div class="name">{name}</div>{body}</div>'


def render_issue_row(name_es: str, name_en: str, count: int, hours: float, surface: str) -> str:
    color = {"tech": "#405189", "seo": "#c19a4a", "content": "#067a68", "mixed": "#7a748f"}.get(surface, "#7a748f")
    return (
        f'<div class="issue-row">'
        f'<div class="meta">'
        f'<b><span data-es>{name_es}</span><span data-en>{name_en}</span></b>'
        f'<span style="color:var(--muted);font-size:12px">→ <span style="color:{color};font-weight:600">{surface}</span> · ~{hours}h</span>'
        f'</div>'
        f'<div class="n">{count}</div>'
        f'</div>'
    )


def main():
    data = load_latest_audit()
    records = data["records"]
    summary = summarize(records)
    n_urls = len(records)
    n_pages = sum(1 for r in records if r["sitemap"] == "page")
    n_posts = sum(1 for r in records if r["sitemap"] == "post")
    n_chapters = sum(1 for r in records if r["sitemap"] == "chapters")
    n_crit_high = summary["by_sev"].get("CRITICAL", 0) + summary["by_sev"].get("HIGH", 0)
    n_no_meta = summary["gaps"]["no_meta_desc"]
    n_no_h1 = summary["gaps"]["no_h1"]
    n_no_alt = summary["gaps"]["imgs_no_alt"]
    n_imgs_total = summary["gaps"]["imgs_total"]
    pct_no_meta = round(n_no_meta / n_urls * 100, 0) if n_urls else 0
    pct_no_alt = round(n_no_alt / n_imgs_total * 100, 0) if n_imgs_total else 0
    pct_tracking = round(summary["track"]["GA4"][0] / n_urls * 100, 0) if n_urls else 0
    audit_date = data["audited_at"][:10]

    page_records = [r for r in records if r["sitemap"] in ("page", "chapters")]
    post_records = [r for r in records if r["sitemap"] == "post"]
    rows_pages = "\n".join(render_row(r) for r in page_records)
    rows_posts = "\n".join(render_row(r) for r in post_records)

    # Tracking cards — summary["track"][k] is a (count, ids) tuple
    def tc(name, key, legacy=False):
        cnt, ids = summary["track"][key]
        return render_track_card(name, cnt, n_urls, ids, is_legacy=legacy)
    track_cards = "".join([
        tc("Google Analytics 4", "GA4"),
        tc("Universal Analytics (UA)", "UA", legacy=True),
        tc("Google Tag Manager", "GTM"),
        tc("Facebook Pixel", "FB Pixel"),
        tc("Hotjar", "Hotjar"),
    ])

    # Issue rows — derived from the artisan command's plan (mirror the priorities)
    issues_def = [
        ("Sin meta description", "Missing meta descriptions", n_no_meta, 27.8, "seo"),
        ("Imágenes sin alt", "Images missing alt text", sum(1 for r in records if r["imgs_no_alt"] > 0), 31.4, "content"),
        ("Títulos fuera de rango (25–65)", "Titles outside 25–65 chars", summary["gaps"]["title_len_bad"], 10.8, "seo"),
        ("Sin H1", "Missing H1", n_no_h1, 9.4, "tech"),
        ("Universal Analytics legacy (sunset)", "Universal Analytics legacy (sunset)", summary["track"]["UA"][0], 1.0, "tech"),
        ("Confirmar Facebook Pixel con cliente", "Confirm FB Pixel with client", summary["track"]["FB Pixel"][0], 0.5, "seo"),
        ("HTTP errors (404 / 5xx)", "HTTP errors (404 / 5xx)", len(summary["errors"]), 0.6, "tech"),
    ]
    issue_rows = "\n".join(render_issue_row(*x) for x in issues_def[:4])  # top 4 for overview
    issue_rows_full = "\n".join(render_issue_row(*x) for x in issues_def)
    total_hours = round(sum(x[3] for x in issues_def), 1)

    html = HTML_TEMPLATE.format(
        n_urls=n_urls, audit_date=audit_date,
        n_pages=n_pages, n_posts=n_posts,
        n_crit_high=n_crit_high, n_no_meta=n_no_meta, n_no_h1=n_no_h1,
        n_no_alt=n_no_alt, n_imgs_total=n_imgs_total,
        pct_no_meta=int(pct_no_meta), pct_no_alt=int(pct_no_alt), pct_tracking=int(pct_tracking),
        rows_pages=rows_pages, rows_posts=rows_posts,
        track_cards=track_cards, issue_rows=issue_rows, issue_rows_full=issue_rows_full,
        total_hours=total_hours,
    )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"→ {OUT}  ({len(html):,} chars · {n_urls} URLs rendered)")


if __name__ == "__main__":
    main()
