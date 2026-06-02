# Plan — Themes (variantes de color) + Migración SOTSI → Webflow

> Generado 2026-06-01 (planner agent). Sitio de trabajo: **DEV** `6a1d0762d6ddc2456edd8403`.
> NUNCA tocar PROD `6a182f372e1313bdfbeeee21` (build de Jose). MCP `webflow-sotsi` en solo-lectura;
> todo cambio a DEV con aprobación de Joel por cambio. Brandbook fuente: `input/Sotsi_and_UHF_Brand_Guidelines.pdf` + `BRAND_REFERENCE.md`.

## Dependencias
```
F4 Imágenes (scraper + hosting) ─┐
                                 ├─→ F2 Home (necesita fotos + copy)
F3 Copy/SEO/CTA ─────────────────┘
F1 Sistema de temas (variable modes) ──→ se aplica debajo de todo
F5 i18n ES/EN ──→ última, depende de contenido estable
```
F1 y F4 son paralelizables desde ya y desbloquean F2. F3 alimenta F2. F5 al final.

## Decisiones bloqueantes de Joel
| # | Decisión | Recomendación |
|---|---|---|
| D1 | ¿Cuántos temas? | 3 modes: **SOTSI Navy** (default) · **UHF Purple** · **Light Airy** |
| D2 | Canela Trial → licenciar o sustituir | comprar Canela **o** Fraunces/Cormorant (libre) |
| D3 | Commerce + Membership ¿sí/no? | si no hay tienda → quitar carrito; Member = newsletter/comunidad |
| D4 | Webflow Localize (pago ~$9–29/mes) | confirmar presupuesto; si no → subcarpeta `/es` |
| D5 | 3 vs 4 pilares en Programs | 4 pilares (Authentic Power · Emotional Awareness · Responsible Choice · Spiritual Partnership) |

## FRENTE 1 — Sistema de temas (PRIORIDAD)
Selector de tema que cambia **bg / botón / texto** vía **Variable Modes** de Webflow sobre la colección Color (`collection-551453a6-815f-7416-9003-49a7da8266c8`, hoy `modes:[]`). Typography/Spacing ya usan modes responsivos → patrón probado.

**Vía A (recomendada "for now"):** N modes aplicados a `body`/wrappers; Joel cambia el mode en el Designer y compara en vivo. Cero código, reversible, DEV-only.
**Vía B (switcher en vivo de cara al usuario):** requiere atributos custom + JS que togglea clase en `body`. Frágil → posponer.

Tokens que varían por tema:
| Variable | SOTSI Navy | UHF Purple | Light Airy |
|---|---|---|---|
| Body/Section BG | `#0E1631` | `#3C1951` | `#FFFFFF`/Periwinkle `#D2CCFD` |
| Heading/Primary text | White | White | `#0E1631` |
| Accent/Button | Luminous `#FFEB45` | Luminous `#FFEB45` | Golden `#FED457` |
| Stroke/secundario | `#3C1951` | `#0E1631` | Lilac `#E7D4F1` |
No varían: tipografía, spacing, weights, radios.

Tareas: (1) sanear tokens — consolidar ~6 navy duplicados + limpiar 3 hardcodes (About Section bg white, Body Text Light 1 #121212, Hero Title rgba); (2) crear 3 modes vía `variable_tool`; (3) valores por mode; (4) aplicar default a `body`; (5) duplicar Home en 3 stagings para comparar.
DoD: cambiar el mode en `body` reskinea el Home completo; ningún color "pegado".

## FRENTE 2 — Migración páginas viejas → Webflow (Home primero)
Fuente: `data/migration_plan.json` + `data/page_plans.json`. El Home no se rediseña, se rellena (12 bloques Shimma).
Sprint 1: limpieza global (logo SOTSI, quitar promo/Flowzai, títulos SEO "Shimma", decidir carrito D3) + Home sección por sección (~46.5h):
Hero(reconstruir, video real, CTA no `/products`) · About(mejorar) · Programs/Courses(D5) · Member(D3) · Benefits 3 cards · Expert→**Gary & Linda** (Linda memorial, sign-off) · Events(CMS) · Testimonials(CMS, aprobados) · Articles(blogs) · Ticker CTA+Footer.
Luego resto de `principales`: about, about-gary-zukav, about-linda-francis, books, events-and-programs, get-started, connect, faqs, media, podcast, newsletter.
DoD por página: copy aprobado · fotos reales · SEO title+desc · CTA real · 301 mapeado · sin Shimma · responsive 320/768/1024/1440.

## FRENTE 3 — Copy / SEO / CTA
Insumos: copy de Jose (conservar Hero/Programs), `posts_extracted.json` (voz real), `seo_audit` (269/308 sin meta desc, 90 sin H1), `BRAND_REFERENCE.md` (voz calma, sin urgencia).
Agentes/skills: **`brand-voice`** (calibrar tono) → **`seo-specialist` + `seo`** (meta titles/desc, H1, CTA) → **`content-engine`/`article-writing`** (solo blog, fase posterior).
Flujo: por sección del Home, paquete `{headline, body, CTA, seo_title, seo_desc}` en JSON (stdlib, sin API pago) que Joel revisa y pega. Testimonios/Linda = sign-off cliente.

## FRENTE 4 — Imágenes (scraper stdlib + hosting + upload)
`asset_tool > upload_image_by_url` necesita **URL pública** → paso de hosting obligatorio.
Hosting: bucket GCS ya usado (`storage.googleapis.com/22d-trello-assets-.../`) **o** GitHub Pages del repo.
Pipeline: (1) `scrape_images.py` stdlib recorre seatofthesoul.com (sitemap del audit), descarga `<img>`+`og:image`, Crawl-delay 3 → `assets/img/<slug>/`; (2) extraer brandbook PDF (pdfimages/Chrome headless) → `assets/img/brand/`; (3) clasificar por regla dura SOTSI=montaña/agua, UHF=humanos, descartar IA; (4) hosting; (5) `upload_image_by_url` a DEV.
Riesgo: fotos del WP viejo pueden tener licencia stock → revisión legal pre-PROD.

## FRENTE 5 — i18n ES/EN (fase posterior)
Locale English en DEV `enabled:false`. **Webflow Localize = pago (D4)**.
Con Localize: habilitar locale Spanish, traducir estático + CMS por campo, switch nativo. Sin Localize: subcarpeta `/es` duplicada (más mantenimiento). Después de que Home/`principales` estén estables.

## Calendario
| Sprint | Foco | Frentes |
|---|---|---|
| 1 | Cimientos + Home aprobado | F1·F4·F3·F2 |
| 2 | Marca core + Fundadores | F2·F3·F4 |
| 3 | Programas/landings + commerce | F2·D3·D5 |
| 4 | Funnels + contenido + blog | F2·F3 |
| 5 | Legal + 301 + QA + i18n + go-live | F5·QA·D2·launch |

## PRIMER PASO (esta sesión)
Arrancar F1 read-only: auditar la colección Color (variables exactas, hardcodes, navy duplicados) y entregar (a) plan de consolidación, (b) limpieza de 3 hardcodes, (c) tabla de valores por mode lista para `variable_tool`. Joel decide D1 y abre Designer → se crean los modes con aprobación.
En paralelo (sin bloqueos): escribir `scrape_images.py` (stdlib) para F4.
