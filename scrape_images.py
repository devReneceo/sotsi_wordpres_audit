#!/usr/bin/env python3
"""
SOTSI image scraper — descarga fotos REALES del sitio WordPress viejo para la
migración a Webflow.

Por qué: el nuevo sitio (template Shimma en Webflow) necesita imágenes reales de
marca. Regla dura del brandbook: FOTOS REALES, NUNCA IA. SOTSI = montaña/agua,
UHF = humanos. Este script baja los `<img>` y `og:image` de las páginas del sitio
viejo, los guarda localmente y deja un manifiesto para subirlos luego a Webflow
(via `asset_tool > upload_image_by_url`, que necesita URL pública → ver hosting).

Stdlib only — sin pip. Respeta Crawl-delay (default 3s) como el resto del proyecto.

Reusa las URLs ya crawleadas en `data/seo_audit_2026-05-29.json` (campo og_image +
la lista de páginas), así no re-descubre el sitemap.

Uso:
    python3 scrape_images.py --pages /,about,/get-started   # solo esas páginas
    python3 scrape_images.py --group principales            # páginas del grupo (migration_plan.json)
    python3 scrape_images.py --all --limit 40               # primeras 40 del audit
    python3 scrape_images.py --og-only                      # solo og:image de cada página (rápido)

Salida:
    assets/img/<slug>/<archivo>          imágenes descargadas
    assets/img/manifest.json             {archivo_local, src_url, page, kind, bytes}
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from html.parser import HTMLParser

BASE = "https://seatofthesoul.com"
UA = "Mozilla/5.0 (compatible; SOTSI-ImageScraper/1.0; +migration)"
AUDIT_JSON = "data/seo_audit_2026-05-29.json"
PLAN_JSON = "data/migration_plan.json"
OUT_DIR = os.path.join("assets", "img")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")
# extensiones de imagen reales (ignora svg de iconos/sprites por defecto)
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
# patrones de archivos a saltar (iconos, logos de plugin, sprites, spam)
SKIP_PATTERNS = ("icon", "sprite", "logo-", "favicon", "emoji", "loader",
                 "placeholder", "spinner", "1x1", "pixel", "casino", "bet")


class ImgParser(HTMLParser):
    """Extrae src de <img> (incluye data-src/lazyload y el primer candidato de srcset)."""

    def __init__(self):
        super().__init__()
        self.srcs = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        a = dict(attrs)
        # orden de preferencia para lazy-load themes de WP
        cand = (a.get("src") or a.get("data-src") or a.get("data-lazy-src")
                or a.get("data-original"))
        srcset = a.get("srcset") or a.get("data-srcset")
        if srcset:
            # toma el candidato de mayor resolución (último) del srcset
            parts = [p.strip().split(" ")[0] for p in srcset.split(",") if p.strip()]
            if parts:
                cand = parts[-1]
        if cand:
            self.srcs.append(cand)


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def slugify(page_url):
    path = urllib.parse.urlparse(page_url).path.strip("/")
    return path.replace("/", "_") or "home"


def is_real_image(u):
    low = u.lower()
    if not low.split("?")[0].endswith(IMG_EXT):
        return False
    if any(p in low for p in SKIP_PATTERNS):
        return False
    return True


def load_audit_pages():
    """Devuelve [(url, og_image)] desde el audit; status 200, HTML."""
    if not os.path.exists(AUDIT_JSON):
        sys.exit(f"No existe {AUDIT_JSON}. Corre seo_audit.py primero.")
    data = json.load(open(AUDIT_JSON))
    out = []
    for r in data.get("records", []):
        if r.get("status") == 200:
            out.append((r.get("final_url") or r.get("url"), r.get("og_image") or ""))
    return out


def group_slugs(group):
    """Slugs de migration_plan.json para un grupo de prioridad."""
    if not os.path.exists(PLAN_JSON):
        return set()
    data = json.load(open(PLAN_JSON))
    pages = data.get("pages", data) if isinstance(data, dict) else data
    slugs = set()
    for p in pages:
        if p.get("group") == group:
            if p.get("slug"):
                slugs.add(p["slug"])
            u = p.get("url") or p.get("old_url") or ""
            if u:
                slugs.add(slugify(u))
    return slugs


def download(src_url, page_url, manifest, kind="content"):
    src_url = urllib.parse.urljoin(page_url, src_url)
    if not src_url.startswith("http"):
        return False
    slug = slugify(page_url)
    folder = os.path.join(OUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    fname = os.path.basename(urllib.parse.urlparse(src_url).path) or "img"
    dest = os.path.join(folder, fname)
    if os.path.exists(dest):  # idempotente
        return False
    try:
        body, ctype = fetch(src_url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  ! fallo {src_url}: {e}")
        return False
    if not ctype.startswith("image") and not src_url.lower().endswith(IMG_EXT):
        return False
    with open(dest, "wb") as f:
        f.write(body)
    manifest.append({
        "file": dest, "src_url": src_url, "page": page_url,
        "kind": kind, "bytes": len(body),
    })
    print(f"  + {dest} ({len(body)//1024} KB)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", help="lista de paths separados por coma (/,about,...)")
    ap.add_argument("--group", help="grupo de migration_plan.json (principales/...)")
    ap.add_argument("--all", action="store_true", help="todas las páginas del audit")
    ap.add_argument("--og-only", action="store_true", help="solo og:image por página")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=3.0)
    args = ap.parse_args()

    audit = load_audit_pages()
    audit_map = {u: og for u, og in audit}

    # decide el set de páginas objetivo
    if args.pages:
        targets = []
        for p in args.pages.split(","):
            p = p.strip()
            full = p if p.startswith("http") else urllib.parse.urljoin(BASE + "/", p.lstrip("/"))
            targets.append(full)
    elif args.group:
        slugs = group_slugs(args.group)
        targets = [u for u, _ in audit if slugify(u) in slugs]
        print(f"Grupo '{args.group}': {len(targets)} páginas")
    elif args.all:
        targets = [u for u, _ in audit]
    else:
        sys.exit("Especifica --pages, --group o --all. Ver --help.")

    if args.limit:
        targets = targets[: args.limit]

    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else []
    seen_before = len(manifest)

    for i, page in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {page}")
        # 1) og:image (suele ser la imagen destacada/hero)
        og = audit_map.get(page, "")
        if og and is_real_image(og):
            download(og, page, manifest, kind="og")
        # 2) imágenes de contenido (salvo --og-only)
        if not args.og_only:
            try:
                html, ctype = fetch(page)
            except Exception as e:  # noqa: BLE001
                print(f"  ! no se pudo leer la página: {e}")
                continue
            if "html" in ctype:
                parser = ImgParser()
                try:
                    parser.feed(html.decode("utf-8", "ignore"))
                except Exception:  # noqa: BLE001
                    pass
                uniq = []
                for s in parser.srcs:
                    full = urllib.parse.urljoin(page, s)
                    if is_real_image(full) and full not in uniq:
                        uniq.append(full)
                for s in uniq:
                    download(s, page, manifest, kind="content")
        # guarda manifiesto incremental + delay cortés
        json.dump(manifest, open(MANIFEST, "w"), indent=1, ensure_ascii=False)
        if i < len(targets):
            time.sleep(args.delay)

    new = len(manifest) - seen_before
    print(f"\nListo. {new} imágenes nuevas · {len(manifest)} totales en {MANIFEST}")
    print("Siguiente: clasificar (montaña-agua vs humanos), descartar IA, hospedar "
          "en URL pública (GCS/GitHub Pages) y subir a Webflow con upload_image_by_url.")


if __name__ == "__main__":
    main()
