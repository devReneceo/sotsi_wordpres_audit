#!/usr/bin/env python3
"""Build the SOTSI/UHF -> Webflow migration tracking dashboard.

Reads:
  - data/migration_plan.json   (editable source of truth: 110 pages + sprints)
  - data/page_plans.json       (optional per-page action plans, keyed by slug)

Renders a self-contained, on-brand, BILINGUAL (ES/EN) static dashboard:
  - KPI header, role-hour bars, sprint tiles, priority-group cards
  - filterable board (Tabulator) with a per-row "view old WordPress page" button
  - per-page slide panel (old->new URL, checklist, hours, notes, links, open-plan)
  - per-page PLAN modal (mini admin dashboard): AI context, section map
    (old skeleton -> new skeleton -> Webflow block), per-section hours + checkboxes,
    and Shimma template analysis. Currently populated for Home.
  - Team Guide tab (brand rules + workflow + Definition of Done)

The dynamic rendering + i18n live in dashboard_src/app.js; styling in
dashboard_src/styles.css. Both are inlined here so the output is a single file.

Output: migration_dashboard.html  (copied to team.html for GitHub Pages /team)
Stdlib only. No pip, no API key. Re-runnable / idempotent (except timestamp).
"""
import json
from datetime import datetime
from pathlib import Path

ROOT      = Path(__file__).resolve().parent
DATA_IN   = ROOT / "data" / "migration_plan.json"
PLANS_IN  = ROOT / "data" / "page_plans.json"
CSS_IN    = ROOT / "dashboard_src" / "styles.css"
JS_IN     = ROOT / "dashboard_src" / "app.js"
HTML_OUT  = ROOT / "migration_dashboard.html"
COPY_TO   = ROOT / "team.html"


def load_json(path, default=None):
    """Read a JSON file; return default if it does not exist."""
    if not path.exists():
        return default
    return json.load(open(path, encoding="utf-8"))


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
<style>__CSS__</style>
</head>
<body>
<header class="top"><div class="wrap">
  <div class="lang-toggle">
    <button data-lang="es" class="active">ES</button><button data-lang="en">EN</button>
  </div>
  <div class="brandline"><span class="dot"></span><span data-i18n="h.brandline">Seat of the Soul · Universal Human · 22D Marketing</span></div>
  <h1 data-i18n-html="h.title_html">Plan de Migración a <em>Webflow</em></h1>
  <div class="sub" data-i18n="h.sub">Tablero de trabajo del equipo.</div>
  <div class="gen"><span data-i18n="h.updated">Actualizado:</span> __GENERATED_AT__</div>
</div></header>

<div class="wrap">
  <div class="kpis" id="kpis"></div>

  <div class="tabs">
    <button class="tab-btn active" data-tab="overview" data-i18n="tab.overview">Resumen</button>
    <button class="tab-btn" data-tab="board" data-i18n="tab.board">Board</button>
    <button class="tab-btn" data-tab="guide" data-i18n="tab.guide">Guía del equipo</button>
  </div>

  <div class="tab-panel active" id="tab-overview">
    <section class="block"><h2 data-i18n="ov.plans_title">Planes de página</h2>
      <p style="color:var(--muted);font-size:12.5px;margin-bottom:12px" data-i18n="ov.plans_note"></p>
      <div class="groups" id="plans-list"></div>
    </section>
    <section class="block"><h2 data-i18n="ov.groups_title">Grupos de prioridad</h2><div class="groups" id="group-summary"></div>
      <p style="color:var(--muted);font-size:12.5px;margin-top:10px" data-i18n="ov.groups_note"></p>
    </section>
    <section class="block"><h2 data-i18n="ov.sprints_title">Sprints</h2><div class="sprints" id="sprint-tiles"></div></section>
    <section class="block"><h2 data-i18n="ov.roles_title">Horas por rol</h2><div id="role-bars"></div>
      <p style="color:var(--muted);font-size:12.5px;margin-top:10px" data-i18n="ov.roles_note"></p>
    </section>
  </div>

  <div class="tab-panel" id="tab-board">
    <section class="block">
      <div class="filters">
        <input id="f-search" data-i18n-ph="f.search_ph" placeholder="Buscar…">
        <select id="f-group"></select>
        <select id="f-status"></select>
        <select id="f-sprint"></select>
        <select id="f-verdict"></select>
        <select id="f-brand"></select>
        <select id="f-cat"></select>
        <button class="f-clear" id="f-clear" data-i18n="f.clear">Limpiar</button>
        <span class="f-count" id="f-count"></span>
      </div>
      <div id="board"></div>
    </section>
  </div>

  <div class="tab-panel" id="tab-guide">
    <section class="block"><h2 data-i18n="g.title">Guía del equipo</h2><div class="guide" id="guide"></div></section>
  </div>
</div>

<div class="overlay" id="overlay"></div>
<aside class="panel" id="panel"></aside>

<div class="modal-ov" id="modal-ov"></div>
<div class="modal" id="modal">
  <div class="modal-head">
    <button class="modal-close" onclick="closePlan()">×</button>
    <div class="ey" id="modal-ey"></div>
    <h2 id="modal-title"></h2>
    <div class="mh-sub" id="modal-sub"></div>
  </div>
  <div class="modal-body" id="modal-body"></div>
</div>

<footer>SOTSI + UHF · generado por <code>build_migration_dashboard.py</code> · data en <code>data/migration_plan.json</code> + <code>data/page_plans.json</code></footer>

<script>
const PAGES = __PAGES_JSON__;
const SPRINTS = __SPRINTS_JSON__;
const PLANS = __PLANS_JSON__;
</script>
<script>__APP_JS__</script>
</body>
</html>
"""


def main():
    plan = load_json(DATA_IN)
    pages = plan["pages"]
    sprints = plan["sprints"]
    page_plans = load_json(PLANS_IN, default={}) or {}
    css = CSS_IN.read_text(encoding="utf-8")
    app_js = JS_IN.read_text(encoding="utf-8")

    out = (HTML_TEMPLATE
           .replace("__CSS__", css)
           .replace("__GENERATED_AT__", datetime.now().strftime("%Y-%m-%d %H:%M"))
           .replace("__PAGES_JSON__", json.dumps(pages, ensure_ascii=False))
           .replace("__SPRINTS_JSON__", json.dumps(sprints, ensure_ascii=False))
           .replace("__PLANS_JSON__", json.dumps(page_plans, ensure_ascii=False))
           .replace("__APP_JS__", app_js))

    HTML_OUT.write_text(out, encoding="utf-8")
    COPY_TO.write_text(out, encoding="utf-8")

    planned = [s for s in page_plans if s != "_comment"]
    done = sum(1 for p in pages if p["status"] == "done")
    pct = round(done / len(pages) * 100, 1) if pages else 0
    print(f"Wrote {HTML_OUT.name} + {COPY_TO.name}  "
          f"({len(pages)} páginas, {pct}% done, "
          f"{len(planned)} con plan: {', '.join(planned) or '—'})")


if __name__ == "__main__":
    main()
