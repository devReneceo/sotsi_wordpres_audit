#!/usr/bin/env python3
"""
build_blogs_import_csv.py — Genera el CSV de import de Blogs para Webflow (DEV).

Pipeline (stdlib-only, sin API key, resumable):
  1. Lee data/posts_extracted.json -> filtra los 167 auto_keep.
  2. Excluye los 3 ya migrados en el piloto (WP ids 21752, 21765, 21600).
  3. Fetch en vivo del WP REST API (/wp-json/wp/v2/posts/{id}?_embed) con caché
     en data/wp_cache/{id}.json (rerun = cero requests).
  4. Limpia content.rendered al RichText de Webflow (p/h2-h4/ul/ol/li/strong/b/
     em/i/a/blockquote/br; quita iframe/script/figure/img/clases/ids).
  5. Escribe blogs-webflow-import.csv con las 10 columnas EXACTAS de Jose.

Salida -> blogs-webflow-import.csv  (importar en Designer: Blogs -> Import)
Webflow re-hospeda las imagenes (URLs de WP) al importar.
"""
import json, os, re, sys, time, html, urllib.request, urllib.error, ssl, csv
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "data", "posts_extracted.json")
CACHE = os.path.join(BASE, "data", "wp_cache")
OUT = os.path.join(BASE, "blogs-webflow-import.csv")
LOG = os.path.join(BASE, "data", "blogs_import_build.log")

PILOT_IDS = {21752, 21765, 21600}          # ya migrados (no duplicar)
API = "https://seatofthesoul.com/wp-json/wp/v2/posts/{id}?_embed"
DELAY = 1.5                                  # segundos entre requests nuevos
UA = {"User-Agent": "Mozilla/5.0 SOTSI-blog-migration"}

# Columnas exactas del template de Jose + Video Link (campo nuevo en la coleccion)
COLUMNS = ["Blog Title", "Slug", "Short Description", "Blog Thumbnail Image",
           "Blog Banner Image", "Editor Name", "Editor Image", "Category Name",
           "Blog Single Description", "Video Link", "Blog Rich Text"]

ALLOWED = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "b",
           "em", "i", "a", "blockquote", "br"}
DROP_TREE = {"script", "style", "iframe", "figure", "img", "ins", "video",
             "audio", "form", "noscript", "svg", "picture", "source", "table"}
VOID = {"br"}


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class Cleaner(HTMLParser):
    """Reescribe HTML de WP al subset RichText de Webflow."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.drop_depth = 0          # dentro de un subarbol a descartar

    def handle_starttag(self, tag, attrs):
        if self.drop_depth:
            if tag in DROP_TREE:
                self.drop_depth += 1
            return
        if tag in DROP_TREE:
            self.drop_depth = 1
            return
        if tag == "h1":
            tag = "h2"            # nunca H1 en el cuerpo
        if tag in ALLOWED:
            if tag == "a":
                href = dict(attrs).get("href", "")
                href = html.escape(href, quote=True)
                self.out.append(f'<a href="{href}">' if href else "<a>")
            elif tag in VOID:
                self.out.append("<br>")
            else:
                self.out.append(f"<{tag}>")
        # cualquier otro tag (div/span/section/figcaption...) -> unwrap

    def handle_endtag(self, tag):
        if self.drop_depth:
            if tag in DROP_TREE:
                self.drop_depth -= 1
            return
        if tag == "h1":
            tag = "h2"
        if tag in ALLOWED and tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.drop_depth:
            return
        self.out.append(html.escape(data, quote=False))

    def result(self):
        return "".join(self.out)


def clean_richtext(raw):
    c = Cleaner()
    c.feed(raw)
    h = c.result()
    # quitar parrafos/encabezados vacios que quedan al borrar iframes/imgs
    h = re.sub(r"<(p|h2|h3|h4|li|blockquote)>\s*(?:<br>)?\s*</\1>", "", h)
    # colapsar espacios
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n{3,}", "\n\n", h)
    # quitar "The post ... appeared first on ..." (firma WP) si aparece
    h = re.sub(r"<p>The post .*?appeared first on.*?</p>", "", h, flags=re.S)
    return h.strip()


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "")


def first_sentence(text, limit=170):
    text = re.sub(r"\s+", " ", text).strip()
    m = re.search(r"(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
    return s


def series_of(title):
    t = (title or "").lower()
    if "soul feast" in t:
        return "Soul Feast"
    if "soul snack" in t:
        return "Soul Snack"
    if "soul seed" in t:
        return "Soul Seed"
    if "wisdom wednesday" in t:
        return "Wisdom Wednesday"
    return "Article"


def fetch(pid):
    """Devuelve el JSON del post (cacheado)."""
    cpath = os.path.join(CACHE, f"{pid}.json")
    if os.path.exists(cpath):
        with open(cpath, encoding="utf-8") as f:
            return json.load(f), True
    ctx = ssl.create_default_context()
    req = urllib.request.Request(API.format(id=pid), headers=UA)
    with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
        j = json.load(r)
    with open(cpath, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False)
    return j, False


def youtube_url(j):
    """Extrae la URL de YouTube del cuerpo (iframe embed) -> URL watch."""
    c = j.get("content", {}).get("rendered", "")
    m = re.search(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_\-]+)", c)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    # vimeo fallback
    mv = re.search(r"player\.vimeo\.com/video/(\d+)", c)
    if mv:
        return f"https://vimeo.com/{mv.group(1)}"
    return ""


def featured_url(j):
    emb = (j.get("_embedded") or {}).get("wp:featuredmedia")
    if emb and isinstance(emb, list) and emb[0].get("source_url"):
        return emb[0]["source_url"], (emb[0].get("alt_text") or "")
    return (j.get("jetpack_featured_media_url") or ""), ""


def build_row(post, j):
    title = html.unescape(j["title"]["rendered"]).strip()
    slug = j.get("slug") or post.get("slug") or ""
    body = clean_richtext(j["content"]["rendered"])
    excerpt = strip_tags(html.unescape(j.get("excerpt", {}).get("rendered", "")))
    excerpt = re.sub(r"\s+", " ", excerpt).replace("[…]", "").replace("[...]", "").strip()
    img, alt = featured_url(j)
    short = first_sentence(excerpt, 200) if excerpt else first_sentence(strip_tags(body), 200)
    single = first_sentence(excerpt or strip_tags(body), 160)
    return {
        "Blog Title": title,
        "Slug": slug,
        "Short Description": short,
        "Blog Thumbnail Image": img,
        "Blog Banner Image": img,
        "Editor Name": "Gary Zukav",
        "Editor Image": "",
        "Category Name": series_of(title),
        "Blog Single Description": single,
        "Video Link": youtube_url(j),
        "Blog Rich Text": body,
    }


def main():
    os.makedirs(CACHE, exist_ok=True)
    open(LOG, "w").close()
    posts = json.load(open(SRC, encoding="utf-8"))["posts"]
    keeps = [p for p in posts if p.get("auto_verdict") == "auto_keep"
             and int(p["id"]) not in PILOT_IDS]
    log(f"Keeps a migrar: {len(keeps)} (167 - {len(PILOT_IDS)} piloto)")

    rows, fetched, cached, errors = [], 0, 0, []
    for i, p in enumerate(keeps, 1):
        pid = int(p["id"])
        try:
            j, from_cache = fetch(pid)
            if from_cache:
                cached += 1
            else:
                fetched += 1
            rows.append(build_row(p, j))
            if i % 20 == 0 or not from_cache:
                log(f"  {i}/{len(keeps)} id={pid} "
                    f"{'cache' if from_cache else 'LIVE'} :: {rows[-1]['Blog Title'][:50]}")
            if not from_cache:
                time.sleep(DELAY)
        except Exception as e:
            errors.append((pid, repr(e)))
            log(f"  ERROR id={pid}: {e!r}")

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    log(f"\nDONE. filas={len(rows)}  (live={fetched} cache={cached})  errores={len(errors)}")
    log(f"CSV -> {OUT}")
    if errors:
        log("IDS con error: " + ", ".join(str(e[0]) for e in errors))


if __name__ == "__main__":
    main()
