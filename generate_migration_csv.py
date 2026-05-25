#!/usr/bin/env python3
"""Export the migration plan to CSVs for the content team and for redirects.

Reads data/migration_plan.json and writes:
  - SOTSI_Migration_Content.csv  : content-team view (copy/media/SEO focus)
  - SOTSI_Migration_Redirects.csv: 301 map for every drop/consolidate-loser

UTF-8-BOM so Excel/Sheets honour accents on open. Stdlib only.
This is the bridge to the content pipeline (edit JSON <-> CSV <-> MCP).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "migration_plan.json"
CONTENT_CSV   = ROOT / "SOTSI_Migration_Content.csv"
REDIRECTS_CSV = ROOT / "SOTSI_Migration_Redirects.csv"

CONTENT_COLS = [
    "slug", "title", "group", "brand", "category", "verdict", "phase", "sprint", "status",
    "url_old", "new_path",
    "copy", "hero_media", "images", "video", "seo_title", "seo_desc", "redirects",
    "hours_content", "hours_media", "assignee_role",
    "dependencies", "consolidate_into", "notes",
]


def write_bom_csv(path, header, rows):
    """Write a CSV with UTF-8 BOM (Excel-friendly)."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def build():
    plan = json.load(open(DATA, encoding="utf-8"))
    pages = plan["pages"]

    # Content CSV — every buildable page (skip pure drops; they have no content work)
    content_rows = []
    for p in pages:
        if p["verdict"] == "drop":
            continue
        ck = p["content_checklist"]
        content_rows.append([
            p["slug"], p["title"], p.get("group", ""), p["brand"], p["category"], p["verdict"],
            p["phase"], p["sprint"], p["status"], p["url"], p["new_path"],
            "x" if ck["copy"] else "", "x" if ck["hero_media"] else "",
            "x" if ck["images"] else "", "x" if ck["video"] else "",
            "x" if ck["seo_title"] else "", "x" if ck["seo_desc"] else "",
            "x" if ck["redirects"] else "",
            p["role_hours"].get("content", 0), p["role_hours"].get("media", 0),
            p["assignee_role"], "; ".join(p["dependencies"]),
            p["consolidate_into"] or "", p["notes"],
        ])
    gpri = {"principales": 0, "programas": 1, "contenido": 2, "sistema": 3}
    write_bom_csv(CONTENT_CSV, CONTENT_COLS,
                  sorted(content_rows, key=lambda r: (gpri.get(r[2], 9), r[7], r[0])))  # group, sprint, slug

    # Redirects CSV — every drop + every consolidate-loser
    red_rows = []
    for p in pages:
        loser = (p["verdict"] == "drop") or (p["verdict"] == "consolidate" and p["consolidate_into"])
        if not loser:
            continue
        target = "/" + p["consolidate_into"] if p["consolidate_into"] else "(definir destino relevante)"
        red_rows.append([p["url"], target, p["verdict"], p["notes"]])
    write_bom_csv(REDIRECTS_CSV, ["url_old", "redirect_to_301", "reason", "notes"],
                  sorted(red_rows, key=lambda r: r[0]))

    print(f"Wrote {CONTENT_CSV.name} ({len(content_rows)} filas de contenido)")
    print(f"Wrote {REDIRECTS_CSV.name} ({len(red_rows)} redirects 301)")


if __name__ == "__main__":
    build()
