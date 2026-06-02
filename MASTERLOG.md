# SOTSI WordPress Audit — Masterlog

> Este es el **MASTERLOG** del proyecto SOTSI (renombrado de `WORK_LOG.md` el 2026-05-25).
> Registro maestro de toda la auditoría + migración a Webflow.

**Site:** seatofthesoul.com
**Repo:** devReneceo/sotsi_wordpres_audit
**Live URL:** https://devreneceo.github.io/sotsi_wordpres_audit/

---

## Session · 2026-06-02 — Webflow DEV: **publicado** + fix hover Cursos, SEO en bloque, Testimonials reales, **piloto de Blogs (3 posts reales migrados)**

> Continuación directa. Se **publicó el DEV** al subdominio (`https://seat-of-the-soul-institut-71acdf22a9cd2.webflow.io`) y se iteró con feedback visual de Joel. Sigue sin dominio propio; PROD intacto.

### Fixes visuales
- **Hover de los cards de Cursos**: el título (`Class Card Title`) usaba variable de color **oscura** y quedaba ilegible sobre el panel morado del hover; la descripción (`Class Card Details Text`) ya era blanca. Fix: `style_tool > update_style` color del título → **misma variable blanca** (`a46866f5-…-9236ff27be47`). Legible en todos los breakpoints.

### SEO en bloque (Data API `update_page_settings`)
- Reemplazados los títulos/descripciones heredados **"… - Shimma - Webflow Ecommerce Website Template"** por copy SOTSI en **14 páginas** (Home + About, Courses, Events, Blog, Contact Us, Team, Products, Checkout, Checkout PayPal, Order Confirmation, 404, Password, Home Copy). Patrón título: `<Página> | Seat of the Soul Institute`. OG hereda (`titleCopied/descriptionCopied: true`).
- **Dejadas fuera a propósito:** 7 páginas-plantilla CMS (título = binding dinámico `{{wf name}}`; tocarlo por API rompe el binding → editar en Designer) y utility pages License/Changelog/Style Guide (candidatas a borrar). **"Home Copy"** (`/home-copy`) es un duplicado publicado de Jose → recomendado borrar/draft.

### Testimonials — límite técnico del MCP (importante)
- La sección es un **Slider nativo de Webflow** (`SliderWrapper/SliderMask/SliderSlide`). **El MCP NO puede: (a) crear `SliderSlide` nuevos ni duplicar slides, (b) asignar la colección a un Collection List** (al crear un CMSCollection queda sin fuente; `get_bindable_sources` solo devuelve campos de página, ningún CMS). → Ni expandir el slider ni bindear CMS por API; ambas requieren la UI del Designer.
- Hecho: se **ocultaron las fotos demo** (caras aleatorias que no eran Jay-Z/Oprah/Paulo, `set_visibility:false` en los 3 Image Wrap). Quedan **3 testimonios reales sin foto** (curados: Jay-Z, Oprah, Paulo Coelho).
- **Para los 8 (hand-off Jose, 5 min):** en Designer, duplicar slides ×5 y editar, **o** agregar Collection List → fuente *Testimonials* → bindear quote/name/`author-title` → ordenar por *Display Order*. (CMS Testimonials ya tiene 8 reales: Oprah, Maya Angelou, Paulo Coelho, Gwyneth Paltrow, Lewis Howes, Jay-Z, Julianne Hough, André Duqum; `photo` null en todos.)

### 🚀 Piloto de migración de Blogs — 3 posts reales (pipeline validado end-to-end)
Colección **Blogs** (`6a1d0762d6ddc2456edd840d`). Campos: name/slug/short-description/blog-single-description/blog-image/blog-banner-image/editor-name/category-name/blog-rich-text. **Faltan `published-on` (fecha) y `seo-description`** (los debe agregar Jose; sin fecha no hay orden cronológico a escala).

Pipeline ejecutado:
1. Selección de 3 keep reales del triage (`data/posts_extracted.json`): **Soul Feast #73 (Linda Part 3)**, **Soul Snack #83 (control→authentic power)**, **Soul Feast #82 (Creator or Victim?)**.
2. Fetch de body completo + imagen destacada del **WP REST API en vivo** (`/wp-json/wp/v2/posts/{id}?_embed`), con delay.
3. Subida de las 3 imágenes reales de Gary Zukav a assets Webflow (`asset_tool > upload_image_by_url`).
4. Limpieza de RichText (HTMLParser stdlib: deja p/h2-h4/ul/li/strong/em/b/i/a; quita script/style/clases/ids).
5. `data_cms_tool > create_collection_items` (×3) — **imagen va como `{"url": <cdn>}`, NO `fileId`** (el `fileId` da 400 "Expected value to have a 'url' field"). Webflow re-hospeda la imagen al crear el item.
6. `publish_collection_items` + publish del sitio. **Live en `/blog`.**

Item IDs creados: `6a1e7e341e88cddadeb1ad7b/7d/7f`. Aprendizajes guardados como memoria en el sistema del 22d-trello.

### Pendiente (próxima sesión Webflow)
- [ ] **Jose**: agregar campos `published-on` + `seo-description` a Blogs; arreglar Testimonials (slider→8 o Collection List); títulos SEO de las 7 plantillas CMS en Designer; borrar Home Copy + utility pages.
- [ ] **Migración Blogs completa**: borrar 4 demo, migrar los 164 restantes con el pipeline validado (re-subir imágenes inline del body; mapear redirects de slug).
- [ ] Footer socials reales (FB/IG/X/YouTube). · Licenciar Canela antes de PROD.

---

## Session · 2026-06-01 (noche) — Webflow DEV: primera **edición real del Home** vía MCP Designer (limpieza Shimma/Flowzai + Testimonials reales)

> Primera sesión de **escritura sobre el canvas** del DEV (`6a1d0762d6ddc2456edd8403`) vía MCP `webflow-sotsi`. Antes solo se había leído/diagnosticado. Designer bridge conectado (App MCP lanzada en el Designer, pestaña en foreground). Cambios **guardados en Designer, NO publicados**.

### Conexión MCP (aclaración importante)
- **Data API (OAuth)**: conectada, funciona headless (sites/pages/cms).
- **Designer bridge**: requiere abrir la App MCP en el Designer con el link `…design.webflow.com?app=…` y mantener la pestaña activa. Sin eso, los Designer tools dan "Unable to connect to Webflow Designer".

### Audit completo del Home (12 bloques) — vía 2 subagentes (árboles de 70k+ chars)
- ✅ **Ya branded por Jose**: Hero ("Authentic Power"/Gary Zukav), About, Member Animation, Why Choose Us.
- 🔴 **Fugas de marca**: Navbar (mega-menú "Pages" con promo Shimma + www.flowzai.com + Templates + Get Template) y Footer (wordmark "Shimma" + "© Shimma | Designed by Flowzai").
- 🟡 Lorem ipsum leftover en Expert (3) y Coming Events (4).

### ⚠️ Corrección clave: "CMS vacío" era FALSO
El "No items found" que se ve en el **canvas de edición de componentes** del Designer es solo el estado vacío de esa vista — **el Designer no renderiza items CMS en component-edit**. Verificado vía Data API, las colecciones del DEV ya tienen **contenido real** (Jose las pobló):
| Colección | Items | Estado |
|---|---|---|
| Teams (fundadores) | 4 | Gary Zukav + Linda Francis (fotos reales + bios) + Sara Saii + Melissa Palacios |
| Courses | 5 | Spiritual Partnership, Authentic Power Guidelines, Beyond the Five Senses, Soul Themes, Emotional Awareness |
| Events | 4 | Create Authentic Power, Choose Love, Spiritual Partnership, An Evening with Gary Zukav |
| Testimonials | 8 | Oprah, Maya Angelou, Paulo Coelho, Gwyneth Paltrow, Lewis Howes, Jay-Z, Julianne Hough, André Duqum |
| **Blogs** | 4 | ⚠️ **DEMO** (genéricos yoga) — faltan los 167 reales |

IDs de colección DEV: Courses `…840b` · Events `…840c` · Blogs `…840d` · Teams `…840e` · Categories `…840f` · SKUs `…8410` · Products `…8411` · Testimonials `…8434`.

### Ediciones aplicadas hoy (Designer + Data API)
1. **Footer** (`443032c2…eec`): String `…f2c` "© Copyright - Shimma | Designed by " → "© 2026 Seat of the Soul Institute "; **removido** link Flowzai (`…f2d`); wordmark `…f41` "Shimma" → "Seat of the Soul".
2. **Navbar** (`b2bc2611…314b`): **removido** todo el DropdownWrapper "Pages" (`…53158`) = promo card Shimma + www.flowzai.com + columna Templates + CTAs Get Template + links demo (Style Guide/License/Changelog/404/Password); **removido** CTA móvil "get template" (`…188cd`). **Carrito ecommerce conservado** (`CommerceCartWrapper …257954`, decisión D3 abierta).
3. **Nav labels**: "classes"→"Courses", "events"→"Events", "blog"→"Blog". Nav final: Home · About · Courses · Events · Blog.
4. **Lorem ipsum**: removidos 3 en Expert (`…795/7a4/7b3`) + 4 en Coming Events (`…771e7/77232/7727d/772c8`).
5. **SEO Home** (Data API, page `…83e4`): title → "Seat of the Soul Institute | Authentic Power with Gary Zukav"; description SOTSI; OG hereda.
6. **Testimonials Section** (`dfd26041…505`): 3 slides demo (Maya Thompson/Elijah Carter/Sofia Martins) → **Jay-Z, Oprah Winfrey, Paulo Coelho** con sus quotes reales sobre *The Seat of the Soul* (display-order 1-3 del CMS).

Verificación: query final → 0 "Shimma" / 0 "Flowzai" en navbar y footer; carrito + nav reales intactos.

### Pendiente
- [ ] **Publicar el DEV** (webflow.io) para ver en vivo los cambios + el CMS renderizado (hoy todo en Designer sin publicar).
- [ ] **Blogs**: reemplazar los 4 demo por los 167 reales (migración grande; piloto 3-5 primero, subir imágenes con `asset_tool > upload_image_by_url`).
- [ ] **Testimonials**: (mejora) rebindear la sección del Home al CMS (8 items + fotos) en vez del slider estático de 3.
- [ ] **Footer socials**: fb/ig/x apuntan a homepages genéricas → poner URLs reales de SOTSI.
- [ ] **SEO**: las otras ~24 páginas heredan títulos "Shimma - … Template" (reemplazo bulk vía Data API `update_page_settings`).
- [ ] Licenciar **Canela** antes de publicar PROD (sigue como "Canela Trial").

---

## Session · 2026-06-01 (noche) — App `22d-trello`: **AI Project Memory System** (memory / journal / reports + context MD)

> App hermana (`/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`). Servicio Cloud Run `trello-22d`, proyecto `profound-yew-489203-b5`, `us-central1`. BD = Supabase PROD (local escribe a prod). Deploy `./deploy.sh`.

### Tarea (Joel)
Convertir el CRM en **AI-Native**: sobre el MCP existente (19 tools de KPIs/tareas/blogs), agregar **memoria persistente** para que Claude/ChatGPT recuerden contexto histórico entre conversaciones. Spec de 4 capas (Current State / Project Memory / Project Journal / AI Reports) + context endpoints en **Markdown** (no JSON).

### Decisiones (preguntadas a Joel)
- **project_id forward-compatible**: tabla `projects` con 1 fila (SOTSI id 1); las 3 tablas nuevas llevan `project_id` default a SOTSI. La app mono-proyecto queda intacta (no se tocó pages/tasks/blogs).
- **Summaries "ambas"**: `summarize_project_journal` devuelve digest determinístico (conteos por autor) **+** entradas crudas → el agente sintetiza (cero API, regla del proyecto).
- **Author del journal = user_id** (resuelto por nombre como el resto del MCP) con fallback a texto libre para gente fuera del equipo.

### Entregado
- **1 migración** `2026_06_01_000010_create_ai_memory_layers`: `projects` (+seed SOTSI), `project_memories` (title/memory/importance/tags json/created_by), `project_journal` (entry_date/author_id/author_name/content), `ai_reports` (report_type/title/content/generated_by).
- **4 modelos**: `Project` (DEFAULT_ID=1), `ProjectMemory`, `JournalEntry` (tabla `project_journal`), `AiReport`.
- **`Support/ProjectContext`** — renderer Markdown compartido (current-state brief, memory, journal raw, journal digest, latest report, brief combinado, search). DRY entre MCP y HTTP.
- **`Concerns/HandlesMemoryLayers`** (trait) — **11 MCP tools nuevas** (19 → **30**): `get_project_context`, `get_project_brief`, `get/save/search_project_memory`, `add/get/summarize_project_journal`, `save/get/get_latest` report. Mantiene `McpController` delgado (merge en `tools()` + fall-through en `callTool()`). Todas con `dry_run` donde escriben.
- **`ContextController`** + rutas `/ctx/{token}`, `/ctx/{token}/memory|journal|brief` (Markdown `text/plain`, token en path, para ChatGPT/Gemini que leen URLs).
- **MCP `instructions`** reescritas: brief-first para "¿cómo va?"; nota de avance → journal + update task + save memory.
- **`ProjectMemorySeeder`**: 9 memorias reales precargadas del masterlog (Canela Trial 🚨, foto-real-nunca-IA, DEV≠PROD, local=prod, secuencias PG, commerce abierto, triage 167/20, cero-API).
- **14 tests** nuevos (`MemoryLayersTest`) → **62/62 PHPUnit verdes**.

### Aplicado en PROD
- `migrate --force` + `db:seed --class=ProjectMemorySeeder` corridos contra **Supabase PROD** (tablas nuevas, aditivo). Verificado: 1 project, 9 memorias (4 high), insert/delete en journal OK → **secuencias Postgres sanas** (tablas nuevas, NO sufren el bug del port SQLite). `ProjectContext::briefMarkdown()` renderiza contra datos reales.
- **2 commits**: `feat: add-task loading feedback + inline card edit styling` (pendiente viejo) + `feat: AI Project Memory System …`. Push a `github.com/devReneceo/22d-trello` main. **Deploy a Cloud Run** ejecutado (el código nuevo de las tools entra en vivo con el deploy; la BD ya tenía las tablas por local=prod).

### Workflow nuevo para el agente
- *"¿Cómo va SOTSI?"* → `get_project_brief` (estado + memoria high + último reporte).
- *"Hoy terminé Contact Form y resolví ActiveCampaign"* → `add_journal_entry` + `update_task` + `save_project_memory` si hay decisión durable.

### Cómo regenerar / correr
```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello"
php artisan test --testsuite=Feature            # 62/62
php artisan migrate --force                       # crea las 4 tablas (Supabase prod)
php artisan db:seed --class=ProjectMemorySeeder --force
./deploy.sh                                       # publica el código nuevo de tools
# MCP en claude.ai: el conector /mcp/<token> ahora lista 30 tools tras el deploy.
# Context MD: https://trello-22d-…run.app/ctx/<SNAPSHOT_TOKEN>[/memory|/journal|/brief]
```

### Pendiente
- [ ] Tras deploy, **re-cargar el conector MCP en claude.ai** para que aparezcan las 11 tools nuevas (hoy mostraba 19).
- [ ] (Opcional) `save_ai_report` desde el botón "Resume project" del dashboard (persistir el reporte determinístico que hoy se calcula y se descarta).
- [ ] (Opcional) Si se re-portan datos de SQLite, recordar resetear secuencias también de las 4 tablas nuevas.
- [ ] Decidir BD de pruebas vs local=prod (sigue abierto del día).

---

## 2026-06-01 — Webflow DEV: disección del Home + auditoría de tokens (vía MCP solo-lectura)

Joel creó un sitio **DEV** (clon de PROD) para iterar sin tocar el de Jose. Se diagnosticó vía MCP `webflow-sotsi` en **solo-lectura** (Claude nunca ha creado ni editado ningún sitio Webflow).

**Sitios actuales en el workspace SOTSI** (`69fb10a1d207c46d49542bb8`):
| Sitio | Site ID | Nota |
|---|---|---|
| **DEV - Seat of the Soul Institute** | `6a1d0762d6ddc2456edd8403` | ⭐ sitio de trabajo (creado 6/01, clon de PROD) |
| **PRODUCTION - Seat of the Soul Institute** | `6a182f372e1313bdfbeeee21` | build real de Jose — NO tocar |
| **BACKUP INITIAL STATE** | `6a180e375d2eb885171037d3` | respaldo |
| 2 borradores viejos del AI Site Builder | `6a0421…632a`, `6a0424…12f1` | ignorar |

Template confirmado = **Shimma** (e-commerce yoga/wellness). Licencia single-use = OK duplicar para mismo cliente/proyecto (SOTSI). Todos en subdominio webflow.io, sin dominio propio, locale English `enabled:false`.

### Estructura del Home (DEV) — 12 bloques arriba→abajo
Hecho casi todo con **componentes** (no secciones nativas). Orden real:
`Navbar` (comp, con carrito ecommerce) · **Hero Section** (nativa — H1 "**Authentic Power**" + H2 "Spiritual Growth & Emotional Awareness with **Gary Zukav**"; animación de scroll de 5 frames "Hero Scroll Tigger", **NO el carrusel Swiper del WP viejo**) · **About Section** (nativa — "A Space to Reconnect with Your Soul") · **Tricker Text Section** (nativa, marquee) · `Member Animation Section` (comp) · `Why Choose Us Section` (comp — H3 "Learn, Reflect & Grow at Your Own Pace" + cards CMS) · `Expert Section` (comp — instructores → **rebuild a Gary & Linda**) · `Coming Events Section` (comp, CMS Events) · `Testimonials Section` (comp, CMS) · `Articles` (comp — últimos blogs CMS) · `Ticker` (comp — CTA marquee global) · `Footer` (comp).
- **Copy del hero YA es SOTSI** (Jose ya empezó). Cards salen vacías porque están **bindeadas al CMS**.
- 17 componentes en la librería: Button Fill/Outline, Footer, Navbar, Breadcrumb, Ticker, + las *Section* de arriba, Template Button/Info Bar (demo), About/Courses Hero.

### Tokens de diseño (5 colecciones de variables) — **re-skin de marca YA ~80% hecho**
Corrige el masterlog (que asumía crema/espresso del demo público). El DEV/PROD real ya tiene la paleta de marca:
- **Color:** Primary/Body BG/Section BG/Heading = navy `#0e1631` · BG Secondary/Stroke/Cosmic Purple = `#3c1951` · Luminous Yellow/Cursor = `#ffeb45` · White · Charcoal `#131313`.
- **Font Family:** **Jost** (sans/body) · **Canela Trial** (serif display/títulos) · Libre Caslon Condensed · FontAwesome (iconos).
- **Font Weight:** 300–700 (typos "Blod"/"Semi-Blod", cosméticos).
- **Typography + Spacing:** colecciones con **modos responsivos por breakpoint** (tipografía fluida) — el `body` los aplica. Template bien hecho.

### Auditoría de uso de tokens — sano, con deuda chica
Mayoría de estilos enlazan a variables (`body`, `About Title`, `Classes Heading` [usa Canela Trial], `Body Text 03`, `Blog/Event Post Hero`). Hardcodes encontrados: `About Section` bg `white` fijo · `Body Text Light 1` color `#121212` fijo · `Hero Title` `rgba(51,51,51,0)` + `font-size:20.42vw` (efecto display gigante intencional).

### Pendientes técnicos reales del template (orden)
1. **🚨 Licenciar Canela** — "Canela **Trial**" está aplicada a los títulos (`Classes Heading`); sale en vivo al publicar PROD. Comprar Canela o serif alternativa licenciada (Cormorant/Fraunces). Para DEV ok seguir.
2. **Consolidar ~6 tokens navy duplicados** (Heading Text Dark, Body Text 2, Section BG, BG colour, Body BG, Primary todos = `#0e1631`).
3. **Limpiar 3 hardcodes** de color (arriba).
4. **Decidir commerce + membership** — afecta carrito del Navbar y `Member Animation Section` (bloqueo abierto del masterlog).
5. Reemplazo global de títulos SEO "Shimma - Webflow Ecommerce Website Template" (heredado en las 25 páginas).

### Cómo retomar el MCP del Designer
Designer tools necesitan el sitio abierto en el Webflow Designer con la app MCP activa (pestaña en primer plano). Enlace DEV: `https://seat-of-the-soul-institut-71acdf22a9cd2.design.webflow.com?app=...`. Data API tools (pages/cms/sites) funcionan headless sin abrir el Designer.

### Ejecución (misma sesión, 2026-06-01) — plan + 3 frentes arrancados
Joel pidió: usar el brandbook para generar **variantes de color (themes)** en DEV con el motor de variables de Webflow, **migrar** el sitio viejo, **copy/SEO/CTA** adaptado al template, **imágenes** reales (scraping), e **i18n ES/EN** (fase posterior). Se usó el **planner agent**.

- **Brandbook guardado** en `input/Sotsi_and_UHF_Brand_Guidelines.pdf` (copia del de Downloads). Destilado ya existía en `BRAND_REFERENCE.md` (paleta: Navy #0E1631, Cosmic Purple #3C1951, Periwinkle #D2CCFD, Lilac #E7D4F1, Luminous #FFEB45, Golden #FED457; Canela+Jost; foto real nunca IA).
- **Plan maestro** → `PLAN_WEBFLOW_THEMES_Y_MIGRACION.md` (5 frentes, dependencias, 5 decisiones bloqueantes D1–D5, calendario por sprints).
- **F1 Themes — EJECUTADO en DEV (escritura autorizada).** En la colección Color (`collection-551453a6-815f-7416-9003-49a7da8266c8`) se crearon **2 modes nuevos**: `UHF Purple` (`mode-ab5bda08-034b-532e-ec95-dc60c355661f`) y `Light Airy` (`mode-f857eff4-7c7f-4152-5a91-4c53dde76031`); el base = SOTSI Navy. Valores asignados (solo lo que difiere del base): UHF → Body BG/Section BG/BG colour = `#3c1951`; Light → esas 3 = `#ffffff` + Luminous Yellow = `#fed457`. **NO se borró ningún token** (para no romper bindings). Se aplicó UHF al `body` para preview y se **revirtió** → DEV quedó en SOTSI Navy. El "dropdown de themes" = el **selector de Mode** nativo del panel Variables. **Pendiente para Light 100%:** mapear las variables de TEXTO por mode (el template reusa el mismo navy para fondo y texto → en Light el texto blanco de secciones oscuras quedaría invisible). SOTSI↔UHF ya cambian limpio.
- **F3 Copy — HECHO** → `COPY_HOME_SOTSI.md` (12 bloques ES/EN, conserva Hero de Jose, 4 pilares, fundadores Gary&Linda [Linda memorial 🔒], testimonios con placeholders, meta SEO, reglas CTA, 3 notas de voz). Generado por agente con `brand-voice`.
- **F4 Imágenes — script listo y probado** → `scrape_images.py` (stdlib, reusa URLs del `seo_audit`, respeta Crawl-delay, salta iconos/spam/IA). Modos: `--pages`, `--group principales`, `--all`, `--og-only`. Salida `assets/img/<slug>/` + `manifest.json`. Smoke test OK (bajó 1 foto real 187KB). Falta: correrlo sobre el Home, clasificar (montaña-agua vs humanos), hospedar en URL pública (GCS `22d-trello-assets` o GitHub Pages) y subir con `asset_tool > upload_image_by_url`.

**Decisiones abiertas (D1–D5):** D1 ¿3 themes? (recom. sí, ya montados) · D2 licenciar Canela vs Fraunces/Cormorant · D3 commerce+membership · D4 Webflow Localize (pago) para ES/EN · D5 3 vs 4 pilares.
**Próximo paso natural:** completar texto del theme Light, o correr `scrape_images.py --group principales`, o empezar a rellenar el Home (F2) con el copy ya listo.

---

## 2026-05-29 — Experimento Supabase Postgres (22d-trello) — LOCAL OK, prod pendiente

Migración exitosa de prueba SQLite → Supabase Postgres free tier ($0/mes) para el 22d-trello dashboard.

**Lo que YA funciona (local laptop):**
- Cuenta Supabase free tier (sin tarjeta, project ref `syepyikmnxxawyiplccw`, region `us-west-2`, Postgres 17.6)
- 22 tablas creadas en Supabase via `php artisan migrate --database=pgsql_supabase --force` (25 migrations OK, ~20s total)
- 451 rows portadas desde SQLite via `php artisan db:port-from-sqlite --target=pgsql_supabase` (100% integridad, comando idempotente)
- RLS habilitado en las 21 tablas públicas (defense in depth — el rol `postgres` de Laravel bypassea, pero la Data API queda bloqueada para `anon`/`authenticated`)
- Switch on-demand sin redeploy: `DB_CONNECTION=pgsql_supabase php artisan serve` — afecta solo ese proceso

**Cambios de código (commit-ready):**
- `config/database.php`: nuevo bloque `pgsql_supabase` que lee de `SUPABASE_DB_*` env vars
- `app/Console/Commands/PortFromSqlite.php`: comando one-shot reusable
- `.env` local: 5 vars `SUPABASE_DB_HOST/PORT/DATABASE/USERNAME/PASSWORD` (gitignored)

**⏳ PENDIENTE — Cutover prod a Supabase**

No urgente. Cuando se decida hacerlo:

1. **Cloud Run service `trello-22d`** — agregar 5 env vars (DB_HOST/PORT/DATABASE/USERNAME apuntando a Supabase; DB_PASSWORD desde Secret Manager). Cambiar `DB_CONNECTION=pgsql_supabase` OR sobrescribir DB_* directamente.
2. **Connection pooler en lugar de Direct** — para Cloud Run serverless usar Transaction pooler (port 6543) en vez de Direct (port 5432) que usamos local. Hay que sacar el URI exacto del Connect button → Connection pooling tab. Hostname será tipo `aws-X-us-west-2.pooler.supabase.com`.
3. **Cron de backup semanal** — Cloud Scheduler dispara Cloud Run job que hace `pg_dump $SUPABASE_URL > backup.sql && gsutil cp backup.sql gs://22d-trello-backups/` (costo ~$0.02/mes).
4. **Cron keep-alive** — proyecto Supabase free se pausa después de 7 días sin actividad. Cloud Scheduler con `SELECT 1` cada 6 días lo mantiene warm. Gratis.
5. **Rotar password Supabase** después del experimento (el actual quedó en transcript de Claude Code 2026-05-29).
6. **Decommission SQLite** — quitar `database/database.sqlite` del repo, simplificar `config/database.php`.

**Para regenerar el experimento (si Supabase se pausa o se pierde):**
```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello"
php artisan migrate --database=pgsql_supabase --force
php artisan db:port-from-sqlite --target=pgsql_supabase
# RLS:
php artisan tinker --execute="DB::connection('pgsql_supabase')->statement(\"DO \\\$\\\$ DECLARE t RECORD; BEGIN FOR t IN SELECT tablename FROM pg_tables WHERE schemaname='public' LOOP EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t.tablename); END LOOP; END \\\$\\\$;\");"
```

---

## 2026-05-29 — SEO audit live site + dashboard cliente + import a 22d-trello

Auditoría técnica complementaria al inventario (que ya cubría drafts / sitemap / categorías). Foco: on-page SEO + tracking pixels + indexación, para deliverable cliente.

**Pipeline nuevo:**
1. `seo_audit.py` — crawl stdlib del sitemap (post + page + chapters), respeta `Crawl-delay: 3` de robots.txt, extrae por URL: title, meta desc, H1/H2, canonical, OG/Twitter, JSON-LD types, robots meta, word count, imgs sin alt, internal/external links, page weight, status, **tracking IDs** (GA4 / UA / GTM / FB Pixel / Hotjar / GSC verification). Salida: `data/seo_audit_YYYY-MM-DD.{json,csv}`.
2. `php artisan seo:import-audit data/seo_audit_*.json` (en 22d-trello) — agrupa findings por issue type y los crea como Tasks asignadas por surface: **Christopher** (5) = SEO copy/meta, **Joel+Jose** (1,2) = tech (H1/canonical/schema/errors), **Luna** (3) = content (alt text).
3. `build_seo_dashboard.py` — produce `seo_dashboard.html` self-contained (Jost + Cormorant) con tabs ES/EN: Resumen · Pages · Posts · Issues · Tracking · Analytics (pendiente GA4+GSC CSV del cliente).

**Resultados crawl (308 URLs, 21.2 min):**
- Severity: CRITICAL=1 (404 en `/sg/garys-welcome-video/`) · HIGH=31 · MEDIUM=273 · LOW=3
- 269/308 (87%) sin meta description ← oportunidad masiva SEO
- 90/308 (29%) sin H1 (incluyendo home)
- 736/1245 (59%) imágenes sin alt text
- Tracking limpio: 1 GA4 `G-PZH9QMWR4R` · 1 FB Pixel `630056102333543` · **1 UA legacy `UA-200510356-1`** (sunset jul 2023 — debt) · 0 GTM · 0 Hotjar · 0 GSC verification meta detectada

**10 tasks creadas en 22d-trello DB** (~83h estimadas total):
- Luna: add alt text en 304 pages (31.4h, high)
- Christopher: meta descs 268 pages (27.8h) + 195 titles fix (10.8h) + FB pixel review (0.5h) + analytics doc (0.5h)
- Joel/Jose: missing H1 89 pages (9.4h) + UA cleanup (1h) + multiple H1 (0.8h) + 404 (0.6h)

**Pendiente:** Joel exporta GA4 (Reports → Engagement → Pages and screens, últimos 90d, CSV) + Search Console (Performance → Pages, últimos 3m, CSV). Cuando lleguen los CSVs joineo con audit para el panel Analytics del dashboard.

**Run again:**
```bash
python3 seo_audit.py --delay 3                                 # ~20 min
cd "../22d-trello" && php artisan seo:import-audit "../SOTSI-WordPress-Audit/data/seo_audit_$(date +%F).json"
cd "../SOTSI-WordPress-Audit" && python3 build_seo_dashboard.py
```

---

## How to regenerate everything (quick reference)

Three scripts, run in this order. Zero pip dependencies — stdlib Python 3 only. No API key required.

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"

# 1. Pull fresh blog post content from WordPress + classify each post.
#    Outputs: data/posts_extracted.json + BLOG_MIGRATION_TRIAGE.md
python3 extract_blog_data.py

# 2. Rebuild the web audit report (includes the Blog Migration Triage tab).
#    Outputs: SOTSI_Audit_Report.html
python3 audit_sotsi.py

# 3. Build the executive PDF for Christopher.
#    Outputs: SOTSI_Blog_Migration_Triage_Report.html (print-ready)
#             SOTSI_Blog_Migration_Triage_Report.pdf  (final deliverable)
python3 generate_triage_pdf.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="SOTSI_Blog_Migration_Triage_Report.pdf" \
  "file://$(pwd)/SOTSI_Blog_Migration_Triage_Report.html"

# 4. Build Christopher's CSV spreadsheets (Excel/Sheets/Numbers ready).
#    Outputs: SOTSI_Blog_Posts_Triage.csv   (all 187 posts, full detail)
#             SOTSI_Blog_Posts_Drops.csv    (slim view, 20 drops only)
#             SOTSI_Blog_SEO_QuickWins.csv  (167 keeps, worst-first by SEO score)
python3 generate_spreadsheet.py

# 5. Push the web report to GitHub Pages.
cp SOTSI_Audit_Report.html index.html
git add -A
git commit -m "update: refresh audit"
git push
```

GitHub Pages updates in ~1 minute after push.

### What each script does

| Script | Purpose | Inputs | Outputs |
|---|---|---|---|
| `extract_blog_data.py` | Pulls full blog post bodies from WP API, runs deterministic triage rules, emits machote MD | live WP REST API on seatofthesoul.com | `data/posts_extracted.json` (~480 KB), `BLOG_MIGRATION_TRIAGE.md` (~220 KB) |
| `audit_sotsi.py` | Builds the interactive web reporter with all tabs (Pages, Posts, Triage, Sitemap, etc.) | live WP API + `data/posts_extracted.json` | `SOTSI_Audit_Report.html` (~470 KB, self-contained) |
| `generate_triage_pdf.py` | Builds the executive print-ready HTML for Christopher | `data/posts_extracted.json` | `SOTSI_Blog_Migration_Triage_Report.html` (print-only) |
| `generate_spreadsheet.py` | Builds Christopher's CSVs (full triage + drops only + SEO quick wins) with deterministic SEO scoring | `data/posts_extracted.json` | `SOTSI_Blog_Posts_Triage.csv`, `SOTSI_Blog_Posts_Drops.csv`, `SOTSI_Blog_SEO_QuickWins.csv` |

### Common single-task flows

**Just refresh the web report after WordPress changes:**
```bash
python3 extract_blog_data.py && python3 audit_sotsi.py && cp SOTSI_Audit_Report.html index.html && git add -A && git commit -m "update: refresh" && git push
```

**Just regenerate Christopher's PDF (no web changes):**
```bash
python3 extract_blog_data.py && python3 generate_triage_pdf.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="SOTSI_Blog_Migration_Triage_Report.pdf" "file://$(pwd)/SOTSI_Blog_Migration_Triage_Report.html"
```

---

## Session · 2026-04-30

### Task: Full WordPress site audit for Christopher's request

Christopher asked:
- Total active/live pages (most important)
- Total inactive/draft pages if easy to find
- Breakdown: main nav pages vs blog posts

---

### What was built

#### 1. Python scraper (`audit_sotsi.py`)
- Pulls data from WP REST API (`/wp-json/wp/v2/pages`, `/wp-json/wp/v2/posts`)
- Parses sitemap XML (`wp-sitemap.xml` → 11 nested sitemaps)
- Scrapes main navigation links from HTML
- Generates a self-contained HTML report

**Results pulled:**
| Metric | Count |
|---|---|
| Active / Live Pages | 110 |
| Blog Posts (published) | 166 |
| Draft Pages (WP Admin) | 35 |
| Draft Posts (WP Admin) | 17 |
| Main Nav Links | 14 |
| Sitemap URLs | 820 |

---

#### 2. HTML Report — Tabs

| Tab | Description |
|---|---|
| **Executive Summary** | Category + year breakdown of the 110 active pages. Click any category row → modal with filtered table |
| **Main Navigation** | 14 nav links with iframe preview panel (slide-in, loading spinner) |
| **Active Pages** | All 110 published pages — Tabulator table with virtual scroll. Click row → right-side preview panel |
| **Classification** | 110 pages classified into 5 categories with filter buttons |
| **Draft Pages** | 35 draft pages + 17 draft posts from WP Admin |
| **Blog Posts** | 166 published posts — sorted newest first |
| **Sitemap Breakdown** | 11 sitemap tiles, click to expand and browse URLs inline |

---

#### 3. Page Classification (5 categories)

| Category | Description |
|---|---|
| **Main Site** | Core brand/nav pages (About, Podcast, Books, etc.) |
| **Program / Event** | Registration, waitlists, questionnaires, SPP/APSP/SPT pages |
| **Content** | Articles, tools, tributes, assessments |
| **System** | Cart, checkout, account, privacy, membership |
| **Thank You** | Confirmation/redirect pages after form submissions |

**Potential duplicates detected:** `blog` + `blog-2`, multiple SPP/SPT registration pages for same year.

---

#### 4. Draft Pages hardcoded (not accessible via public API)

- **35 draft pages** — provided from WP Admin (pages section)
- **17 draft posts** — provided from WP Admin (posts section)

---

#### 5. Key UX features

- Right-side slide panel (50% screen) on row click in Active Pages and Blog Posts
- Category drill-down modal from Executive Summary bars
- iframe loading spinner + blocked-site fallback with "Open in new tab"
- ESC key closes any open panel/modal
- Tabulator v6 with virtual scroll (no pagination needed for 110+ rows)
- Sitemap tiles expand inline with searchable URL table

---

#### 6. Deployment

- Repo: `https://github.com/devReneceo/sotsi_wordpres_audit`
- Live URL: `https://devreneceo.github.io/sotsi_wordpres_audit/`
- Hosted via GitHub Pages (repo set to public)

---

### To regenerate the report

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
python3 audit_sotsi.py
cp SOTSI_Audit_Report.html index.html
git add . && git commit -m "update: refresh audit data" && git push
```

GitHub Pages updates in ~1 minute after push.

---

### Pending / Future

- [ ] Classify blog posts by category/topic
- [ ] Add year filter to Blog Posts tab
- [ ] Schedule auto-regeneration via GitHub Actions (weekly cron)
- [ ] Get exact inactive page count from WP Admin (private + trash)

---

## Session · 2026-05-13 — Blog Migration Triage (full pipeline)

### Task from Christopher

Christopher asked over WhatsApp (2026-05-13):

1. Review every old SOTSI blog post and flag entries with dated content, references to past events, old news, or expired announcements — anything that should **not** migrate to the new site.
2. Rate the remaining (non-outdated) posts on quality.
3. Suggest SEO improvements for the keepers.
4. For new blog content, plan to repurpose Wisdom Wednesdays, Soul Seeds, Soul Snacks, top-performing FB/IG posts, and team videos.

This session delivered #1 in full. #2, #3, and #4 are deferred to follow-up sessions.

### Architecture decision — Python-first, no paid API

Joel runs the Claude monthly plan ($100/mo), not the Anthropic API. Therefore:

- Python does **all** heavy lifting: WP REST fetch, HTML parsing, deterministic heuristics, classification, PDF prep.
- Zero `ANTHROPIC_API_KEY`. Zero `anthropic` SDK dependency. Zero pip dependencies — stdlib only.
- AI (Claude) is only used during a Claude Code session to inspect ambiguous cases and to QA the output.

### Sprint 1 — Extraction + machote MD

New script: **`extract_blog_data.py`** (stdlib only). What it does:

- Fetches every published blog post from `/wp-json/wp/v2/posts` with `content.rendered`, `excerpt`, `categories`, `yoast_head_json`.
- Resolves WP category IDs to names via `/wp-json/wp/v2/categories`.
- Parses each post body with stdlib `html.parser` to extract: headings (H1–H4), image count + missing alts, internal/external link counts, word count.
- Applies deterministic heuristics (no AI per post):
  1. WP category includes `Exclude` → `auto_drop` (the SOTSI team already pre-tagged these in WordPress).
  2. Slug or title matches `soul-snack-*` / `soul-feast-*` / `soul-seed-*` / `wisdom-wednesday-*` → `auto_keep` (evergreen series).
  3. Event-keyword regex (`register`, `Zoom`, `RSVP`, `tickets`, `webinar`, `early bird`, `save the date`, etc.) + past-year regex for the remaining posts.
- Outputs:
  - `data/posts_extracted.json` — structured payload (~480 KB).
  - `BLOG_MIGRATION_TRIAGE.md` — human-readable working triage (~220 KB, 4 sections).

**Results after first pass:**

| Bucket | Posts | Notes |
|---|---:|---|
| `auto_drop` | **20** | All `Exclude`-tagged in WP — confirms decisions already made by the SOTSI editorial team |
| `auto_keep` | **167** | Soul Snacks / Feasts / Seeds / Wisdom Wednesdays — the core evergreen catalog |
| Manual review | **0** | Every post resolved by deterministic rules — no per-post AI tokens spent |

Total: 187 published posts (site grew from 166 since April 30 audit).

### Sprint 2 — Web reporter integration

Extended `audit_sotsi.py` to surface the triage inside the existing dashboard at `SOTSI_Audit_Report.html`:

- New tab **Blog Migration Triage** (next to Blog Posts) with verdict badges, chip filters (All / KEEP / DROP / REVIEW), search, and slide-panel preview reusing the existing iframe UX.
- New KPI card in the report header — clickable, jumps to the triage tab.
- Reads `data/posts_extracted.json` and embeds the rows into the self-contained HTML.
- Refreshed counts site-wide: pages 110, posts 187, sitemap URLs 858, nav 14.

### Sprint 3 — Deep content audit

After Joel asked "¿solo 20 son para eliminar? ¿los demás no son eventos?", a second pass ran a deeper scan over **the full body** of every keep-list post (not just title/excerpt). Nine independent regex patterns were checked:

| Pattern | What it would catch | Posts flagged |
|---|---|---:|
| Register by / registration opens / closes | Expired registration calls | 0 |
| Tickets / RSVP / seats remaining | Past ticketed events | 0 |
| Save the date / doors open / early bird | Promotional event language | 0 |
| Webinar on / starts on (specific date) | Specific dated webinars | 0 |
| Join us on [date] / live event / live broadcast | Past live broadcasts | 0 |
| Annual / this year's retreat or conference | Year-specific recurring events | 0 |
| Specific Month + Year in body (e.g., "March 2024") | Posts anchored to a past month | 0 |
| Specific calendar date (e.g., "October 15") | Date-specific announcements | 0 |
| Past-year-only references (body says "2023") | Time-stamped commentary | 0 |

Three phrases did appear across many keep-list posts and were inspected in context. Each was confirmed evergreen:

| Phrase | Why it appears | Verdict |
|---|---|---|
| "This week, notice…" | Recurring closing exercise (Soul Step Challenge) at the end of every Soul Snack / Feast. Reader applies the teaching during their own week — not on a specific date. | Evergreen |
| "Join Gary LIVE every month" | CTA for the ongoing Soul Themes program. Permanent and recurring monthly. | Evergreen |
| "December 14th, 2012" | One post (Soul Feast #83 with Scarlett Lewis) references the Sandy Hook anniversary as biographical context. | Evergreen |

**Confidence statement:** all 167 keep-list posts were scanned at full-body depth. Zero matched any pattern indicating a past event, expired registration, or moment-in-time announcement. The 20-post drop list is complete.

### Sprint 4 — Executive PDF for Christopher

New script: **`generate_triage_pdf.py`**. Produces a print-optimized HTML (`SOTSI_Blog_Migration_Triage_Report.html`) that Chrome headless renders to PDF (`SOTSI_Blog_Migration_Triage_Report.pdf`, ~590 KB, ~13 pages).

Style chosen: sober corporate. Helvetica, black on white, navy (#1c2333) accent only in headings. No emoji, no AI branding, no icons. Thin-border tables. Print-safe.

Final structure:

| Page | Section |
|---|---|
| 1 | Cover — "SOTSI · Blog Migration Triage Report · Prepared for Christopher Dilts" |
| 2 | Executive Summary (KPIs, method, headline finding) |
| 3 | **Section 2 — Methodology** (9 patterns checked + 3 explained-away + confidence statement) |
| 4–5 | **Section 1 — Posts to drop (20)** with title, category, year, reason |
| 6 | **Section 3 — Posts to keep (167)** summary: by series, by year, top categories |
| 7–12 | **Section 3.1 — Full keep list** with title, series, year |
| 13 | Next steps |

The methodology block also got mirrored into the web reporter as a collapsible card on the Triage tab.

### Files produced this session

| File | Type | Purpose |
|---|---|---|
| `extract_blog_data.py` | new | WP fetch + triage extractor |
| `generate_triage_pdf.py` | new | Executive PDF generator |
| `audit_sotsi.py` | modified | Added Triage tab + KPI card + methodology box |
| `data/posts_extracted.json` | new | Source of truth for triage data |
| `BLOG_MIGRATION_TRIAGE.md` | new | Working triage in markdown |
| `SOTSI_Blog_Migration_Triage_Report.html` | new | Print-ready source for the PDF |
| `SOTSI_Blog_Migration_Triage_Report.pdf` | new | Final deliverable for Christopher |
| `SOTSI_Audit_Report.html` / `index.html` | regenerated | Web report with refreshed counts and triage tab |
| `.gitignore` | new | Ignores `__pycache__`, `.env`, `.claude/` |

### Headline numbers delivered

- **20 posts** recommended **DROP** — fully listed in PDF Section 1
- **167 posts** recommended **KEEP** — evergreen Soul Snacks/Feasts/Seeds/Wisdom Wednesdays
- **89%** of the blog catalog migrates as-is
- **0** posts outside the existing `Exclude` set surfaced as event-tied after deep audit

### Still pending (for the next session)

- [ ] **Quality rating** per keep-list post (5-dimension rubric).
- [ ] **Content Pipeline tab** scaffold for Wisdom Wednesdays / Soul Seeds / top FB / IG / YouTube content. Source format and ingestion pending input from Luna.
- [ ] **GitHub Action** for weekly auto-refresh (optional).
- [ ] **Year filter** + **category filter** on Blog Posts tab.
- [ ] Confirm whether the upcoming new site is WordPress (so SEO output maps directly to Yoast) or another platform.

---

## Session · 2026-05-14 — Christopher's CSV deliverable + SEO quick wins

### Task

Joel asked for an Excel/Sheets-friendly spreadsheet for Christopher covering all 187 blog posts plus the 20 drops, with URLs as a column and basic SEO recommendations per post.

### What was built

New script: **`generate_spreadsheet.py`** (stdlib only, no pip, no API key). Reads `data/posts_extracted.json` and emits three CSVs encoded as UTF-8-BOM so Excel honours accents on open:

| File | Rows | Purpose |
|---|---:|---|
| `SOTSI_Blog_Posts_Triage.csv` | 187 | Full detail: URL, verdict, title, series, category, date, word count, image stats, link stats, Yoast title/desc, SEO score, SEO action items |
| `SOTSI_Blog_Posts_Drops.csv` | 20 | Slim view of drops only — URL, title, year, category, reason, word count, date |
| `SOTSI_Blog_SEO_QuickWins.csv` | 167 | KEEPs sorted worst-first by SEO score; top 3 action items per row |

### Deterministic SEO scoring (no AI)

Five axes, 20 points each (100 max). Score and action items computed for KEEPs only — DROPs leave those columns blank because they're going away.

| Axis | Full marks | Action emitted when failing |
|---|---|---|
| Yoast title length | 30–65 chars | "Title too long (X chars, aim 30-65)" / "Add SEO title" |
| Meta description length | 120–160 chars | "Add meta description (120-160 chars)" |
| Word count | ≥ 500 words | "Thin content" (< 300) / "Short content" (300–499) |
| Alt text coverage | All images have alt | "Add alt text to N of M images" |
| Internal links | ≥ 3 | "Add internal links (currently N, aim 3+)" |

H1 check: only flags duplicates inside the body, since the WP theme renders the post title as the page H1 outside `content.rendered` — every post would otherwise be a false positive.

### Headline findings on the 167 keepers

- **Average SEO score:** 46.9 / 100 — low, but the gap is concentrated in two fixes.
- **166 of 167** have no Yoast meta description. Fixing only that lifts average to ~67.
- **167 of 167** have fewer than 3 internal links.
- ~40 posts have titles over 65 characters (Soul Feast title pattern adds episode number + colon + topic).
- Dozens of posts have 300–500 word bodies (Soul Snack format is naturally short).

### Files produced this session

| File | Type |
|---|---|
| `generate_spreadsheet.py` | new |
| `SOTSI_Blog_Posts_Triage.csv` | new |
| `SOTSI_Blog_Posts_Drops.csv` | new |
| `SOTSI_Blog_SEO_QuickWins.csv` | new |
| `WORK_LOG.md` → `MASTERLOG.md` | renamed 2026-05-25 (este archivo) |

---

## Session · 2026-05-25 — Plan de migración a Webflow + tablero del equipo

### Tarea (Joel)

22D compró un Webflow y el diseñador (Jose) ya está diseñando sobre una plantilla comprada.
Existe un brandbook nuevo (`Sotsi and UHF Brand Guidelines.pdf`). Joel pidió un **plan de acción
para todo el equipo** (diseño, video, copy, imágenes) para migrar WordPress → Webflow, con
secciones a mantener/mejorar/quitar y **horas estimadas**, más un **tablero URL** que organice el
trabajo de todos. Decisiones: Fase 1 = sitio principal (blog después), horas **por rol**, tablero
estático **JSON-driven en GitHub Pages** (sin BD, sin backend).

### Contexto absorbido

- Leído el brandbook completo (48 págs) → destilado en `BRAND_REFERENCE.md` (dos marcas SOTSI
  navy/naturaleza + UHF purple/humanos; tokens de color; Canela/Jost; regla foto-real-no-IA).
- Inventario real extraído del reporte de auditoría → `data/site_inventory.json`:
  **110 páginas activas** (Main Site 22, Program/Event 43, Content 21, System 13, Thank You 11).

### Delegación a agentes (paralelo)

- **architect** → framework del plan: rúbrica de clasificación, veredicto para las 110 páginas,
  alcance Fase 1, benchmarks de horas por arquetipo, 5 sprints, Definition of Done, 8 riesgos.
- **code-architect** → arquitectura del tablero: esquema JSON, diseño del generador, UX, tokens CSS.

### Entregables producidos

| Archivo | Tipo | Qué es |
|---|---|---|
| `BRAND_REFERENCE.md` | new | Destilado operativo del brandbook para el equipo |
| `data/site_inventory.json` | new | Inventario real de 110 páginas por categoría |
| `seed_migration_plan.py` | new | Genera el plan desde el inventario + overrides de veredicto |
| `data/migration_plan.json` | new | **Fuente de verdad** editable: 110 págs con veredicto/sprint/horas/checklist |
| `build_migration_dashboard.py` | new | Genera el tablero de marca (KPIs, board Tabulator, slide-panel, guía) |
| `generate_migration_csv.py` | new | CSV de contenido + mapa de 301 redirects |
| `migration_dashboard.html` / `team.html` | generated | Tablero (publicar en GitHub Pages `/team`) |
| `SOTSI_Migration_Content.csv` | generated | 80 filas para el equipo de contenido |
| `SOTSI_Migration_Redirects.csv` | generated | 51 redirects 301 (drops + consolidate-losers) |
| `PLAN_MIGRACION_WEBFLOW.md` | new | **Documento guía maestro** (revisan Joel + Jose) |

### Números

- Veredictos: 13 REBUILD · 39 IMPROVE · 25 CONSOLIDATE · 3 KEEP · 30 DROP = 110.
- ~55 páginas construibles → **≈ 881.5 h** (Build 237.5 · Contenido 214 · Diseño 205 · Media 144 · Revisión 81).

### Cómo regenerar el tablero de migración

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
# (opcional) re-seed desde el inventario si cambian los veredictos base:
python3 seed_migration_plan.py
# editar data/migration_plan.json (estatus, horas, checklist) y regenerar:
python3 build_migration_dashboard.py      # -> migration_dashboard.html + team.html
python3 generate_migration_csv.py         # -> CSVs de contenido + redirects
git add -A && git commit -m "update: migration plan" && git push   # live en ~1 min
```

### Pendiente (próxima sesión)

- [ ] Revisión Joel + Jose del plan y el board; confirmar veredictos sensibles (memorial Linda, DROPs).
- [ ] Decisión de commerce + membership (bloquea Sprint 3).
- [ ] Confirmar licencia de Canela; montar biblioteca de fotos reales (no IA).
- [ ] Publicar `team.html` en GitHub Pages y compartir URL. ✅ HECHO (live en `/team`).
- [ ] Fase 2: plan de migración del blog (187 posts, ya triados 167/20).

### Actualizaciones posteriores (mismo día)

**Tablero publicado.** `team.html` live en https://devreneceo.github.io/sotsi_wordpres_audit/team (commit 7b83e3a).

**Separación por grupos de prioridad** (commit 2922955). Se agregó el campo `group` a cada
página (`seed_migration_plan.py`): `principales` (15 págs, 247.5h — core must-have: home, about,
fundadores, books, get-started, events&programs, podcast, media, faqs, connect, newsletter, blog),
`programas` (59, 420.5h), `contenido` (22, 123.5h), `sistema` (14, 90h). El tablero ahora tiene
resumen por grupo, board agrupado y filtro de Grupo; el CSV de contenido incluye la columna `group`.

**Webflow MCP conectado a esta carpeta.** Se agregó el MCP de Webflow en **scope local** con
nombre propio **`webflow-sotsi`** (NO `webflow` genérico, que reusaba el OAuth de la carpeta UHF
por estar llaveado por nombre de servidor). Así SOTSI tiene su **propia cuenta/OAuth**, separada de
UHF. Pendiente: Joel hace `/mcp` → autoriza con la cuenta SOTSI (Chrome ya logueado) y reinicia
Claude Code para cargar las tools `mcp__webflow-sotsi__*`.
  - UHF/ → servidor `webflow` (cuenta A, intacta)
  - SOTSI-WordPress-Audit/ → servidor `webflow-sotsi` (cuenta B)
  - ⚠️ `/22D Marketing` (padre) tiene un Bearer token en texto plano — considerar migrar a OAuth / rotar.

### Pendiente real (próxima sesión)

- [ ] Completar OAuth de `webflow-sotsi` (`/mcp` + reinicio) y conectar el pipeline de contenido
      `migration_plan.json` → Webflow vía MCP, empezando por las Páginas principales.
- [ ] Revisión Joel + Jose del board; confirmar veredictos sensibles (memorial Linda, DROPs).
- [ ] Decisión de commerce + membership (bloquea Sprint 3).
- [ ] Confirmar licencia de Canela; montar biblioteca de fotos reales (no IA).
- [ ] Fase 2: plan de migración del blog (187 posts, ya triados 167/20) — Joel tiene dudas aquí.

---

## Session · 2026-05-25 (tarde) — Diagnóstico de la cuenta Webflow (MCP conectado)

### Contexto

Joel completó el OAuth de `webflow-sotsi` (`/mcp` → "Authentication successful. Connected to
webflow-sotsi") y pidió un **diagnóstico de qué hay actualmente en la cuenta Webflow** vía MCP,
para registrarlo aquí. Cuenta/workspace SOTSI: `workspaceId 69fb10a1d207c46d49542bb8`.

### Hallazgo: hay 3 sitios en el workspace

| # | Nombre | Site ID | Estado | Veredicto |
|---|---|---|---|---|
| 1 | Seat of the Soul Institute | `6a0421fefc0460de5474632a` | Creado 5/13, **nunca publicado**, 5 págs, 0 colecciones CMS | **Borrador IA — eliminar** |
| 2 | The Seat of the Soul Institute | `6a04240570c532ff7c8c12f1` | Creado 5/13, **nunca publicado**, 6 págs, 0 colecciones CMS | **Borrador IA — eliminar** |
| 3 | Seat of the Soul Institute | `6a0756563c0753689004ec7f` | Creado 5/15, **publicado 5/19**, 25 págs, 9 colecciones, screenshot | **EL REAL — sitio de trabajo de Jose** |

**Sitios 1 y 2** son borradores generados con el **AI Site Builder de Webflow** (el copy SEO ya es
real de SOTSI — Gary Zukav, "authentic power" — pero las páginas son genéricas: Home, Courses,
Membership, Books, About, Style guide; sin CMS). Recomendación: **borrarlos** para que nadie del
equipo abra la URL equivocada. Ambos siguen en subdominio webflow.io, sin dominio propio.

### Sitio 3 — el sitio real (plantilla "Shimma")

- Basado en **Shimma**, plantilla de Webflow e-commerce para estudios de **yoga / Pilates /
  wellness**. Timezone `Asia/Dhaka` (autor de la plantilla / contratista).
- **Publicado 5/19** solo a subdominio `webflow.io` — **sin dominio propio** (`customDomains: []`).
- Locale primario English, **`enabled:false`** (localización apagada). Sin Google Tag, sin data
  collection.
- Screenshot del 5/19: `https://screenshots.webflow.com/sites/6a0756563c0753689004ec7f/20260519134458_e5019552e1e191841e5381d0b030ff24.png`

**25 páginas:** Home · About · Classes · Events · Blog · Contact Us · Team · Products · Checkout ·
Checkout (PayPal) · Order Confirmation · 404 · Password(401) · utility-pages (Style Guide, License,
Changelog) · plantillas CMS (Blogs, Events, Classes, Teams, Products, Categories, SKUs, **Courses**,
**Testimonials**).

**9 colecciones CMS:** Classes · Events · **Blogs** · Teams · Categories · SKUs · Products ·
**Courses** (nueva, 5/22) · **Testimonials** (nueva, 5/22).

**Trabajo reciente de Jose (5/22):** creó las colecciones + páginas plantilla **Courses** y
**Testimonials**, y editó About, Contact, Team, Blog, Events, Classes, Home. Está adaptando la
plantilla, todavía no migrando contenido.

**⚠️ Pendientes de plantilla (todo default Shimma):**
- Todos los `<title>` SEO siguen diciendo **"… - Shimma - Webflow Ecommerce Website Template"** →
  reemplazo global pendiente.
- El **Blog tiene solo 4 posts demo** con texto lorem ("Robert Fox" como autor, cuerpo de
  "task-management app", contenido falso de jardinería/yoga). Cero contenido real de SOTSI aún.

### Esquema de la colección "Blogs" (clave para migrar los 187 posts)

Collection ID `6a0756583c0753689004ee1a`. Campos actuales:

| Campo (slug) | Tipo | Mapea desde WordPress |
|---|---|---|
| `name` (Blog Title, **req**) | PlainText (max 256) | título del post |
| `slug` (**req**) | PlainText | slug del post |
| `short-description` | PlainText 1-línea | excerpt |
| `blog-image` | Image | thumbnail / featured image |
| `blog-banner-image` | Image | hero del detalle |
| `editor-name` | PlainText | autor |
| `editor-image` | Image | avatar del autor |
| `category-name` | PlainText | ⚠️ texto libre, **NO** referencia a Categories — serie (Soul Snack/Feast/Seed/Wisdom Wed) |
| `blog-single-description` | PlainText | descripción secundaria del detalle |
| `blog-rich-text` | RichText | **cuerpo del post** (`content.rendered`) |

**Faltan campos que el contenido SOTSI necesita** (decisión para Jose antes de importar):
1. **`published-on` (DateTime)** — no hay campo de fecha; el orden/archivo del blog por fecha no
   funcionará sin esto. *Crítico para 187 posts ordenados por fecha.*
2. **`seo-description` (PlainText)** — no hay meta description por item; los SEO quick-wins del CSV
   (166/167 sin meta) no tienen dónde aterrizar todavía.
3. (Opcional) **`source-url`** — para construir los 301 redirects WP→Webflow por post.
4. (Opcional) Convertir `category-name` a **referencia** a una colección de Series/Categorías si se
   quiere filtrado relacional; con texto libre basta para empezar.

### Implicaciones para el plan de migración

- El pipeline `data/posts_extracted.json` (187 posts triados: 167 keep / 20 drop) ya tiene
  título, slug, excerpt, cuerpo, categoría, autor, fecha y stats SEO → mapea casi 1:1 a esta
  colección **una vez se agreguen los 2 campos faltantes** (`published-on`, `seo-description`).
- La importación se puede automatizar vía `data_cms_tool > create_collection_items` (lotes), pero
  **primero** hay que: (a) decidir campos, (b) subir imágenes destacadas como assets Webflow,
  (c) limpiar el RichText de WP (clases/IDs de Yoast) al formato RichText de Webflow.
- Las imágenes de los posts hoy viven en `seatofthesoul.com` (WP). Webflow no las descarga solo;
  hay que subirlas con `asset_tool > upload_image_by_url` y reescribir los `src` del RichText.

### Acciones recomendadas (próxima sesión, en orden)

1. **Limpieza:** borrar sitios 1 y 2 (borradores IA) — confirmar con Joel primero.
2. **Jose:** reemplazar títulos SEO "Shimma…" y borrar los 4 posts demo del blog.
3. **Decidir el esquema final de Blogs** (agregar `published-on` + `seo-description` mínimo).
4. **Piloto de import:** migrar 3–5 posts reales vía MCP de extremo a extremo (assets + RichText +
   campos) para validar el pipeline antes de los 187.
5. Confirmar **dominio propio** (seatofthesoul.com) y plan de 301 redirects (`SOTSI_Migration_Redirects.csv`).

---

## Session · 2026-05-25 (noche) — Tablero v2: i18n, "ver vieja", Plan de Home

### Tarea (Joel)

Sobre el tablero `/team`: (1) botón por página para ver la URL vieja de WordPress; (2) toggle de
idioma ES/EN; (3) **Plan de acción por página, empezando SOLO por Home** — mini-dashboard admin que
mapea las secciones del Home original (WordPress) → Webflow con checkboxes, horas y notas; (4)
análisis del template **Shimma** (estructura/componentes globales/tokens) y mapeo del Home contra
el template; (5) bloque "Contexto de Home por IA" con recomendación estructural.

### Investigación (2 agentes en paralelo)

- **Home WordPress** (`seatofthesoul.com/`): 10 secciones reales + nav + footer. Hallazgos: `/home`
  hace **301 → `/`** (raíz canónica, WP page 41); el hero es un **carrusel Swiper de 4 slides**;
  hay **spam de casino inyectado** (señal de WP hackeado — limpiar, no migrar); el botón "ENROLL IN
  A COURSE" no tiene destino; la comunidad se empuja **2 veces** (CTAs duplicados a Mighty Networks);
  el "Final CTA" dice 'Start your journey' pero apunta al newsletter.
- **Template Shimma** (`shimma.webflow.io`): 10 secciones + librería de ~17 bloques reusables
  (video-hero, about-split, cards de oferta, team grid, testimonial slider, stats band, marquee CTA
  global, etc.). Tokens del template: Playfair Display + Montserrat sobre crema/arena/espresso/cobre,
  botones pill — **requiere re-skin** a navy/Canela. Nav con mega-menú + **carrito ecommerce** +
  CTA "Get Template" + créditos Flowzai → reescribir/apagar.

### Arquitectura del tablero (refactor)

El builder pasó de fragmentos Python a **shell + datos + assets inyectados**, con el render
dinámico e i18n movidos a JS (para que ES/EN sea uniforme). Archivos nuevos:

| Archivo | Qué es |
|---|---|
| `dashboard_src/styles.css` | Todo el CSS (base + toggle idioma, botón "ver vieja", modal de plan, tabla de secciones, tarjeta IA) |
| `dashboard_src/app.js` | Cliente: diccionario i18n ES/EN, `computeMeta`, render de KPIs/sprints/grupos/guía, board Tabulator, slide-panel, **modal de Plan de página** |
| `data/page_plans.json` | **Plan por página, indexado por slug** (reutilizable). Hoy: `home` con 13 secciones + `ai_context` + `template_analysis`. Agregar una página nueva = añadir una key |
| `build_migration_dashboard.py` | Reescrito: carga `migration_plan.json` + `page_plans.json`, inyecta CSS/JS/datos, escribe `migration_dashboard.html` + `team.html` |

### Funcionalidades entregadas

1. **Botón "Ver" por página** (columna en el board, abre la URL vieja de WP en pestaña nueva;
   `stopPropagation` para no abrir el panel) + botón "Ver página vieja ↗" en el slide-panel.
2. **Toggle ES/EN** (arriba-derecha, persiste en `localStorage`). Traduce toda la UI: header, tabs,
   KPIs, filtros, columnas del board, panel, modal y guía. El contenido-dato (notas, labels de
   sprint, veredicto del plan) queda en su idioma de autoría.
3. **Plan de Home** (modal mini-dashboard admin): tira de horas (12·6·8·12·4 = **42h**), tabla de
   13 secciones con columnas **Sección · Esqueleto viejo (WP) · Esqueleto nuevo (Webflow) · Acción
   (reconstruir/mejorar/consolidar/agregar/quitar) · Mapeado a Webflow · Notas · Horas · check**.
   Checkboxes con persistencia local (nota: para el equipo se edita el JSON y se regenera). Punto
   dorado en el board marca las páginas que ya tienen plan; se abre desde el panel o desde la tarjeta
   "Planes de página" del Resumen.
4. **Análisis del template Shimma** dentro del modal: componentes globales, bloques reusables (chips),
   qué quitar/arreglar, y nota de re-skin de tokens.
5. **Contexto de Home por IA**: tarjeta con veredicto ("RECONSTRUIR sobre Shimma, 10→8 secciones +
   limpieza de deuda") + resumen + 6 recomendaciones concretas.

### Mapeo Home WordPress → Shimma (resumen del plan)

Hero carrusel→**video-hero** (reconstruir, 1 mensaje ancla) · Value prop→about-split (mejorar) ·
Tools promo→**consolidar** en el CTA del intro · 4 pilares→cards de oferta CMS (reconstruir, arreglar
link roto) · Join Gary→evento (mejorar) · 2 bandas de comunidad→**1 sola** (consolidar) · Books→
about-split (mejorar) · Founders→team-grid (reconstruir, fotos reales) · Final CTA→marquee global
(mejorar) · +**agregar** testimonials / stats / latest-blog del template · **quitar** spam de casino.

### Verificación

`node --check` del JS OK. Render headless (Chrome) confirma: 5 KPIs, 5 sprints, grupos 14/42/18/6,
guía, board con 110 filas + botón "Ver", toggle EN traduce todo, modal con 13 secciones + IA +
Shimma, **sin `NaN`/`undefined`**. Tabla del plan con scroll horizontal en móvil.

### Cómo regenerar

```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/SOTSI-WordPress-Audit"
# editar data/migration_plan.json (páginas) y/o data/page_plans.json (planes por sección)
python3 build_migration_dashboard.py     # -> migration_dashboard.html + team.html
git add -A && git commit -m "feat: dashboard v2" && git push   # live en /team ~1 min
```

### Pendiente

- [ ] Revisión de Joel + Jose del Plan de Home (veredictos por sección, horas, mapeo a Shimma).
- [x] Publicar (push) para que `/team` muestre la v2. ✅
- [ ] Replicar el patrón de plan para la siguiente página principal (About / Fundadores).
- [ ] Confirmar decisión de commerce/membership (afecta secciones 4 pilares, books, comunidad).

---

## Session · 2026-05-25/26 — App `22d-trello` (Laravel + Cloud Run), productiza el tablero

> El tablero estático `team.html` evolucionó a una **app real** para el equipo. Proyecto hermano,
> fuera de este repo: `/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`. Su propio daylog
> (`daylog-2026-05-25.md`) y README viven ahí. Aquí queda el registro maestro.

### Tarea (Joel)
Crear un sistema tipo Trello para el equipo (asignar/seguir tareas de la migración), **Laravel +
Blade sin Vite**, **SQLite**, desplegado en **Cloud Run**. Reutiliza la data de este repo
(`migration_plan.json` + `page_plans.json` + `posts_extracted.json`). Decisiones: persistencia
SQLite efímera + **export** de BD (se re-hornea al deploy); **login con contraseña** por usuario;
alcance amplio (Dashboard + Plan de Home + Kanban + Mapeo + Blogs); sin Docker Desktop.

### Stack y deploy
- Laravel 13 + Blade puro. **Alpine.js + SortableJS por CDN**, CSS de marca propio. Sin npm/Vite.
- Cloud Run servicio **`trello-22d`** (no `22d-trello`: Cloud Run no acepta nombre con dígito inicial),
  región `us-central1`, proyecto `profound-yew-489203-b5`. Deploy con `./deploy.sh`
  (`gcloud run deploy --source`, Cloud Build remoto → **no se necesita Docker Desktop**). Dockerfile
  PHP 8.4 Apache puerto 8080, patrón copiado del `DonorBoxAC webhook`.
- **URL:** https://trello-22d-juyszotmca-uc.a.run.app · login `joel@reneceo.com` / `Reneceo2025!`
  (equipo: joel, josedaniel, luna, karol, christopher, felipe).

### Vistas entregadas
1. **Dashboard** — KPIs, grupos de prioridad, horas por rol, planes de página, actividad.
2. **Páginas principales** — 15 del grupo principales; Home abre su plan, el resto "estructura
   pendiente · abrir/generar".
3. **Plan de Home** — 13 secciones editables (viejo/nuevo, acción, bloque Shimma, notas, horas,
   media video/foto/texto, asignar, checks, comentarios) + Contexto IA + análisis Shimma.
4. **Kanban** — 110 páginas como tarjetas arrastrables por estatus (SortableJS); click → panel con
   notas del equipo.
5. **Blogposts** — revisión manual de los 187 posts (167 keep / 20 drop) en **grid compacto de chips
   (~6 cols responsivo)** con **tabs** (Por revisar / Aprobados / Drops), **radio de estado** ↻/✓/✗
   que estampa quién aprobó, **preview screenshot** (thum.io) + notas en panel, filtro por serie, y
   **evaluación automática determinística** (sin API): score 0-100 (palabras, meta, links, alt) +
   detección de duplicados → status buen post / aceptable / delgado / posible duplicado / SEO débil.
6. **Mapeo de páginas** — keep/improve/rebuild vs consolidate/drop, URL vieja → nueva.

### Datos (modelo SQLite)
`users` (role/color) · `pages` (110, +plan_meta) · `page_sections` (plan de Home) · `tasks` ·
`notes` · `activities` · `blog_posts` (187, +ai_status/score/reason/recommend). Seeders idempotentes
desde `database/data/*.json` (copiados de este repo). Comandos: `app:ensure-admin`, `app:db-export`,
`app:evaluate-blogs`. Tests: `tests/Feature/SmokeTest.php` (PHPUnit) → 13/13.

### Bugs resueltos en el camino
- Nombre Cloud Run con dígito inicial → `trello-22d`.
- 500 por `storage/framework/views` excluido de la imagen → el entrypoint crea los dirs.
- **Mixed content / login roto**: detrás del proxy Cloud Run, Laravel emitía links `http://` →
  `URL::forceScheme('https')` (prod) + `trustProxies(at:'*')`.
- Colisión columna `notes` vs relación → relación renombrada `comments()`.
- Preview iframe bloqueado → screenshot vía **thum.io** (mShots daba 403).
- Helpers `esc`/`cap` faltantes en el JS (rompían los paneles).
- Alert "No se pudo actualizar" en blogs: `applyBlogApprover` buscaba `.bchip-appr` (eliminado al
  compactar) → apuntado a `.bchip-head`.

### Persistencia (recordatorio operativo)
SQLite vive dentro del contenedor (efímero). Para conservar avance entre deploys: **"↓ Exportar BD"**
(sidebar admin) o `php artisan app:db-export` → copiar a `database/database.sqlite` → redeploy
(el entrypoint no re-siembra si ya hay datos). Pocos deploys esperados una vez estable.

### Pendiente (22d-trello)
- [ ] Generar estructura de secciones de About / Gary / Linda (mismo patrón que Home).
- [ ] (Opcional) dominio propio + actualizar `APP_URL`.
- [ ] (Opcional) evaluación editorial real por post vía LLM (gasta tokens) si se quiere ir más allá
      de la heurística determinística.

---

## Session · 2026-05-26/27 — App `22d-trello`: mapeo de secciones, rediseño de detalle, estados, mapa del plan, tareas del equipo + recursos, deploy rev 00017

> Sigue siendo la app fuera de este repo (`/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`).
> Aquí el registro maestro de la jornada.

### Detalle de sección (bottom-sheet) — rediseño completo
- Se abre como **card de abajo hacia arriba** (iframe `?embed=1`); tabs con **iconos FontAwesome**.
- Header con **pills editables: Action** (Keep/Improve/Add/Rebuild/Consolidate/**Remove=rojo**) y **Stage**
  (Backlog→Researching→Estimating→Planning→Designing→Building→In QA→Refactoring→Feedback→Done) +
  **resumen general** + **feedback interno** (editables inline con lápiz). Patrón de estados estándar
  (Jira/Linear/Asana) investigado.
- **Content blocks** rediseñados como **cards con icono por tipo** (headline/body/CTA-botón/preview de
  media), edición inline (texto → lápiz), **sugerencia** integrada, y **comentarios del equipo por bloque**.
- **Assets en 2 grupos**: **Deliverables** (con seguimiento, 4 fases 25% c/u: Started·Feedback·Approved·
  Added → build% = promedio) y **Team resources** (sin seguimiento, archivos de apoyo). Dos columnas
  6|6 con expand a 12.
- **QA por usuario** con **nota por persona** (todos ven el comentario de QA de la sección).
- **Tech/Bugs/Improvements**: cada entrada con **prioridad + fases** y **botón de borrar** (Tech gateado a Joel/Jose).
- **Persistencia de estado**: tab activo + scroll + columna expandida se conservan tras subir archivos
  (los uploads recargan) → "no se cierra todo".

### Plan de Home — mapa lateral + sliders OLD|NEW
- **Mapa de secciones a la izquierda** (tipo árbol/rama, sticky, scroll-spy) que hace scroll a cada
  sección; **línea conectora SVG** del nodo activo a su card en el **color del Action**; nodos inactivos
  atenuados. Header "Sections · 11".
- **Las 11 secciones del Home** con **slider OLD|NEW** (componente reutilizable) y **capturas de
  referencia** del template Shimma en vivo (en `public/img/refs/`): Hero, About, Courses, Membership,
  Benefits, Team/Founders (Expert Instructors → rebuild a Gary&Linda), Events, Testimonials, Articles,
  CTA marquee, Nav+Footer. Nota: la numeración de secciones que ve Joel en el template corre **+1** vs
  la numeración del plan. **Sección 12 (Template cleanup) ocultada** del plan (`hidden:true` en JSON).
- **Content blocks sembrados para las 11 secciones** según lo que aparece en cada foto.

### Equipo
- **+1 usuario: Rene Banuelos** (`rene@reneceo.com`). QA del equipo ahora cuenta **/7**.

### Dashboard — tablero de tareas general + recursos (NUEVO)
- Se reutilizó la tabla `tasks` (existía sin UI; el Kanban mueve *páginas*). **Board tipo Trello** en el
  dashboard: 5 columnas (To do/In progress/Review/Blocked/Done), **drag** para cambiar estado (SortableJS),
  **modal** de tarea con **seguimientos** (comentarios), filtro **All/Mine**, prioridad/asignado/página.
- **11 tareas sembradas** del kickoff (lista de Joel + WhatsApp de Christopher): analizar template Shimma
  (CMS/estructura), filtrar blogs, planear páginas, generar variantes, **entornos Dev y Test**,
  **investigar herramienta de landing testing**, **mockup del home (Jose, top priority)**, lista de
  change-requests (Jose/Karol), design goals (Apple UX + SEO), aplicar identidad de marca.
- **Team resources**: tabla `resources` (general o por página) + **visor PDF inline**. **Brand book**
  (`SOTSI & UHF Brand Guidelines`) subido y visible interno; + template Shimma, preview Webflow, ref SEO.

### Investigación (respuesta a Christopher: Webflow vs Unbounce/LeadPages)
- Webflow **no** tiene A/B testing nativo fuerte → opciones: **Webflow Optimize** (solo Enterprise),
  **Optibase** (App Marketplace), o externas vía **GTM/scripts/API**. **Unbounce** es CRO-first (A/B
  nativo, Smart Traffic, popups, heatmaps, reportes). **Conclusión: la idea de Christopher tiene sentido**
  para experimentación intensa de landings. Hallazgos guardados en la tarea (estado Review).

### Modelo (añadidos)
`page_sections` +`stage`,`team_feedback` (y `new_status` como resumen) · `section_assets` +`track`
(deliverable vs recurso) · `section_qa` +`note` · `section_blocks` +comentarios (`notes.section_block_id`)
· `tasks` +`priority` y follow-ups (`notes.task_id`) · nueva tabla **`resources`**.
Seeders nuevos idempotentes: `TaskSeeder`, `ResourceSeeder`. Tests: **30/30** (PHPUnit).

### Deploy
- **Cloud Run `trello-22d` revisión `00017`** vía `./deploy.sh` (Cloud Build, sin Docker local). Se
  horneó la BD local validada; `entrypoint` corre `migrate --force` (crea las columnas/tablas nuevas).
- Verificado en vivo: login, dashboard (tareas + recursos + Rene), `/plan/home` (mapa + 11 sliders, sin
  cleanup), detalle de sección (pills + blocks), brand book PDF (`200 application/pdf`), imágenes ref.
- URLs: https://trello-22d-juyszotmca-uc.a.run.app · https://trello-22d-778459417925.us-central1.run.app

### Pendiente / decisiones abiertas (registradas como tareas, no construidas)
- [ ] Elegir herramienta de A/B testing de landings: Unbounce/Instapage vs Webflow Optimize/Optibase.
- [ ] Montar entornos **Dev / Test / Prod** en Webflow (prod = build de Jose; dev = variantes con Claude + manual).
- [ ] Lista de change-requests del sitio UHF mantenida por Jose & Karol (revisar/priorizar/aprobar).
- [ ] **Mockup del home** para presentar al equipo SOTSI (prioridad de Jose).
- [ ] Aplicar identidad SOTSI/UHF (logos sol+loto, paleta navy/púrpura/amarillo) y quitar todo rastro Shimma/Flowzai.

---

## Session · 2026-05-27 — App `22d-trello`: tarjetas editables, reporte de status, **Snapshot JSON + MCP para Claude**

> Sigue siendo la app hermana fuera de este repo (`/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`).
> Aquí queda el registro maestro + el **runbook para desplegar y conectar el MCP** (pendiente de probar).

### Dashboard / tarjetas de tarea (UI)
- **Login**: toggle ojo 👁 para ver/ocultar contraseña. **Favicon** "22" de marca (`public/favicon.svg`) en layout + login (antes salía la X roja por no tener favicon).
- **Tarjetas de tarea** ahora con: **pill de prioridad** clickeable (cicla High→Med→Low), **estimación de horas** opcional (chip `~4h`), **renombrar inline**, **borrar**, y **modo vista/edición** (los controles arrancan ocultos; el lápiz ✏ los muestra, ✓ cierra). Todo guardado optimista, editable por cualquiera (sin restricción por usuario).
- **Múltiples asignados** por tarea (columna JSON `tasks.assignee_ids`, migración con backfill del `assignee_id` viejo). Avatares apilados en la tarjeta; se eligen con checkboxes en el panel de la tarea.
- **Dashboard reestructurado**: header "SOTSI New Website / Tasks & Resources", KPIs compactos en el **topbar** (Progress·Hours left·In progress·Blocked·**My hours**), **tabs** Team tasks | Resources, secciones de abajo (page plans, grupos, horas por rol, actividad) **comentadas** para no saturar. Inputs con look **Material** (CSS propio, sin importar el framework).
- **Sidebar**: se quitó "Home Plan"; se agregó **"My hour report"** (`/my-hours`) — estimado de horas asignadas a la persona (mock data-driven).
- **El modal de detalle de tarea no tenía CSS** (la X/💬 "no hacía nada"): se agregaron estilos de `.modal/.modal-ov/.open` (overlay centrado). También arregla el visor de PDF.

### Reporte de status "Resume project" (determinístico, sin IA)
- Botón **Resume project** en el dashboard → modal con **reporte ejecutivo listo para cliente** (Christopher/jefe): **Print/Save PDF** + **Email** (mailto con cuerpo en texto).
- **100% de la BD, sin IA ni API**: KPIs reales + tabla por grupo + **highlights/risks/next-steps generados de datos** (tareas done/creadas últimos 7 días, bloqueadas, alta prioridad abiertas, sin estimación) + **comparación semana vs. semana** (▲▼). Lógica en `App\Support\ProjectReport`.

### Snapshot JSON + MCP (para que Claude analice el proyecto desde fuera) — **construido, SIN desplegar**
- **`GET /snapshot.json?token=…`** — volcado read-only de todo (KPIs, tareas, páginas, horas, reporte). Protegido por token. Lógica en `App\Support\ProjectSnapshot`.
- **Servidor MCP** en **`/mcp/{token}`** (JSON-RPC sobre HTTP, `App\Http\Controllers\McpController`), 4 tools que leen la BD en vivo: `get_status_report`, `get_kpis`, `list_tasks`, `get_full_snapshot`. CSRF exento para `mcp/*` (`bootstrap/app.php`).
- **Token**: env **`SNAPSHOT_TOKEN`** (config `app.snapshot_token`). En local ya está en `.env`. Verificado local: handshake `initialize`→`tools/list`→`tools/call`, token malo→401, notificación→202, GET→405. **37/37 tests** (PHPUnit).

### RUNBOOK — desplegar y conectar el MCP en Claude (pendiente de probar)
```bash
cd "/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello"

# 1) Deploy con el token como env var de Cloud Run (agregar la flag al deploy):
gcloud run deploy trello-22d --source . --project profound-yew-489203-b5 \
  --region us-central1 --platform managed --allow-unauthenticated --port 8080 \
  --set-env-vars SNAPSHOT_TOKEN=<tu-token-secreto>
#   (o sin re-deploy:)
gcloud run services update trello-22d --region us-central1 \
  --update-env-vars SNAPSHOT_TOKEN=<tu-token-secreto>

# 2) URLs resultantes (base https://trello-22d-…run.app):
#    Snapshot:  https://trello-22d-…run.app/snapshot.json?token=<token>
#    MCP:       https://trello-22d-…run.app/mcp/<token>
```
**Conectar en Claude (Chrome → claude.ai):** Settings → **Connectors** → **Add custom connector** → pegar la **URL del MCP** (`…/mcp/<token>`). Luego en el prompt: *"Connect to the 22D Trello project and give me the status report"*.
- ⚠️ **Requisitos reales**: la URL debe ser **pública HTTPS** (por eso hay que desplegar; localhost no sirve para claude.ai web). Y **claude.ai puede exigir OAuth** al agregar el conector — si lo pide, falta montar la capa OAuth 2.1 (Camino B, no construido aún). Si acepta server sin auth, conecta con el token en la URL.
- Atajo para probar sin claude.ai web: **Claude Desktop** vía `mcp-remote` con la URL del token (sin OAuth).
- **Demo rápido hoy sin MCP**: abrir el `/snapshot.json`, copiar el JSON y pegarlo en Claude con el prompt "dame un status ejecutivo + 3 riesgos + qué esperar la próxima semana".

### Pendiente (próxima sesión)
- [ ] Probar el `/snapshot.json` y el conector MCP en Claude (desplegar + setear `SNAPSHOT_TOKEN`).
- [ ] Si claude.ai exige OAuth → montar OAuth 2.1 (Camino B) para el MCP.
- [ ] (Opcional) Executive Summary con tendencias más finas / horas por persona en el reporte.

---

## Session · 2026-05-28 — App `22d-trello`: MCP **Fase 2 + 3** (write tools) · Blog posts (SOTSI approval / rating / comments / content extractor) · Blog MCP

> Sigue siendo la app hermana (`/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`).
> Todo verificado en local; **sin deploy todavía** (decisión: seguir construyendo, desplegar después).

### MCP — Fase 2 (crear tareas desde una minuta)
- Tools nuevas en `App\Http\Controllers\McpController` (siguen leyendo/escribiendo en la BD local del CRM):
  - **`list_team`** → ids/nombres del equipo. Claude la llama primero para mapear "Karol" → user_id.
  - **`create_task`** → una tarea. Acepta `assignee_names`, `page_title`, `created_by_name` (nombres → ids resueltos en server).
  - **`bulk_create_tasks`** → lote para una minuta de reunión. Crea N tareas en una sola call.
- Soporte de `dry_run` en todas (preview sin persistir) y atribución correcta en el `activities` log (`created_by` sale del nombre que Claude pase).
- Validado round-trip: Claude lee una minuta → llama `bulk_create_tasks` con `assignee_names:["Karol"]` + `page_title:"Home"` → server resuelve nombres + página por substring → tareas en el board.

### MCP — Fase 3 (actualizar avances desde una minuta de seguimiento)
- Tools nuevas:
  - **`find_tasks`** → fuzzy search por título (con `status` opcional). Para resolver "the hero banner task" desde un texto.
  - **`update_task`** → cambia status/priority/hours/title/description/page/asignados. Acepta `task_id` o `task_title` fuzzy.
    - Asignados incrementales: `add_assignees:["Jose"]` / `remove_assignees:["Karol"]` además de replace.
    - Campo `follow_up` opcional: agrega un comentario en el mismo call (el flujo natural "Karol terminó X" → status:done + nota).
    - Devuelve **before/after** y soporta `dry_run`.
  - **`add_follow_up`** → comentario suelto a una tarea.
  - **`bulk_update_tasks`** → N updates desde una minuta de seguimiento, cada uno con su `follow_up` opcional.
- **Ambigüedad protegida**: si el `task_title` matchea >1 tarea, devuelve `ok:false` + lista de candidatos con sus ids — Claude no actualiza algo equivocado, te pregunta o usa `task_id`.

### Blog posts — UI nueva en `/blogs`
- **Migraciones**: `blog_posts` ganó `sotsi_approved` / `sotsi_approved_by_id` / `sotsi_approved_at` / `rating` (good/regular/bad) / `content_sections` (JSON) / `content_fetched_at`. Tabla nueva `blog_post_comments` (id, blog_post_id, user_id, body, timestamps).
- **Chip de cada post** ahora tiene:
  - **Rating pill** (click cicla `Rate → ★ Good → ● Regular → ✗ Weak → Rate`). 3 niveles confirmados con Joel.
  - **Botón SOTSI** que activa/desactiva el visto bueno final del cliente (independiente del review interno). Badge **SOTSI ✓** navy en la cabecera cuando está aprobado.
- **Tabs**: Pending · Internal approved · Drops · **SOTSI approved** (nuevo). 5 KPIs arriba (agregados "SOTSI approved" y "Rated Good").
- **Panel del post** (al click): **lazy fetch** del body de WordPress vía REST API, cacheado en BD. Body cortado por **secciones tipadas** (h2/h3/h4 / ¶ párrafo / LIST ul·ol / "quote") con **botón "Copy" por sección** + **"Copy all"** arriba (usa `navigator.clipboard`). Hilo de **comentarios por usuario** (distinto del campo `notes` compartido que sigue ahí).

### Backend del extractor de contenido
- **`App\Support\WpContentFetcher::sectionsFromHtml($html)`** — parser con `DOMDocument` que devuelve `[{type, text|items}, …]`. Maneja UTF-8, ignora wrappers, recursión un nivel para divs anidados.
- **Comando** `php artisan app:fetch-blog-content [--limit=N] [--force] [--sleep=200]` — bulk fetch + cache. Probado en vivo: post #84 de Soul Feast → 10 secciones limpias.
- **Endpoints**: `/blogs/{id}/sotsi`, `/blogs/{id}/rate`, `/blogs/{id}/comment`, `/blogs/{id}/content` (lazy fetch + cache).
- **Para precargar los 187 posts antes del demo**: `php artisan app:fetch-blog-content` (~40 s con sleep:200ms).

### MCP — Blog posts (8 tools, divididas por intención)
Confirmamos con Joel la división "kpi para reporte / fill / update":

**Reporte (read):**
- `get_blog_kpis` → totales por review_status, sotsi_approved, rating (good/regular/bad/unrated), por serie. Para juntarlo en el status report.
- `list_blog_posts` → filtros `review_status` / `sotsi_approved` / `rating` / `series` / `limit`.
- `find_blog_posts` → fuzzy por título.
- `get_blog_post` → post completo con `sections` (body cacheado) + comments. Claude lee antes de comentar.

**Fill (write):**
- `comment_blog_post` → comentario por usuario con `user_name`.

**Update (write):**
- `rate_blog_post` → good/regular/bad/null.
- `sotsi_approve_blog_post` → toggle con atribución (`by_name`).

**Combo:**
- `bulk_review_blog_posts` → desde una minuta editorial, por post aplica **rating + sotsi + review_status + comment** en una sola call. `dry_run` para preview.

### Estado del MCP completo
- **19 tools** total: 4 reportes proyecto + 3 crear tareas + 4 actualizar tareas + 8 blog.
- Endpoint: `/mcp/{token}` (token = `SNAPSHOT_TOKEN`, mismo del `/snapshot.json`).
- **48/48 PHPUnit tests verdes** (+ las pruebas en vivo del extractor y los bulk).

### Demo flow para Christopher (ya posible local con el snapshot — el conector queda para post-deploy)
- Tipo minuta de reunión: *"Karol terminó el hero, Jose sube About a review, Books queda bloqueado"* → Claude hace `bulk_update_tasks` con 3 entradas → cambios + follow-ups en el board.
- Tipo minuta editorial: *"Soul Feast #84 lo aprobamos SOTSI con rating Good. El #62 lo bajamos a Weak"* → Claude hace `bulk_review_blog_posts` → ratings + SOTSI + comments en los chips.
- *"Connect to 22D Trello and give me the status report including blogs"* → Claude combina `get_status_report` + `get_blog_kpis`.

### Pendiente (decidido: seguir construyendo en local antes del deploy)
- [ ] Deploy con `SNAPSHOT_TOKEN` env var en Cloud Run.
- [ ] Probar el conector en claude.ai con minuta real (otter / junta).
- [ ] OAuth si claude.ai exige (Camino B) — sin construir.
- [ ] (Opcional, pre-deploy) Más tools del MCP / capas en blog / lo que vaya saliendo en sesión.

---

## Session · 2026-06-01 — Cutover a Supabase PROD · Passwords equipo · MCP conectado a Claude · Endpoint `/read` · Tareas privadas · Repo en GitHub · Config global de Claude

> Sesión larga. App `22d-trello` (sibling: `/Users/joeldoradoaguilus/Documents/22D Marketing/22d-trello`). Servicio Cloud Run `trello-22d`, proyecto `profound-yew-489203-b5`, región `us-central1`. URL `https://trello-22d-juyszotmca-uc.a.run.app`. Deploy con `./deploy.sh` (Cloud Build `--source`, sin Docker local). Terminó en **rev 00026**.

### Config global de Claude (`~/.claude/settings.json`)
- `env: { CLAUDE_EFFORT: "high" }` (antes solo en el shell). Niveles low<medium<high<xhigh; xhigh = más tokens, reservar para tareas duras.
- `statusLine` → barra: modelo · carpeta · branch · **costo de sesión** · ⚠ contexto >200k. Script `~/.claude/scripts/statusline.js`.
- `includeCoAuthoredBy: false` (commits sin Co-Authored-By). `permissions.deny` con 12 comandos peligrosos.
- Log global general en `~/.claude/claudeMasterLog.md`.

### Supabase PROD — cutover COMPLETO (antes prod estaba en SQLite)
- **Dockerfile:** agregado `pdo_pgsql pgsql` + `libpq-dev` (la imagen era solo-SQLite → "could not find driver").
- **Conexión:** la directa `db.<ref>.supabase.co` es **IPv6-only** → Cloud Run (IPv4) NO la alcanza. Hay que usar el **Pooler**.
- **Pooler correcto:** `aws-1-us-west-2.pooler.supabase.com` (¡prefijo **`aws-1-`**, no `aws-0-`!), **modo SESIÓN puerto 5432** (más seguro para el `migrate` del entrypoint), usuario `postgres.<project-ref>` (ref empieza con `syepy...`). El `.env` local se cambió de la directa al pooler (host/port/username; password intacto).
- **6 env vars en Cloud Run** (`DB_CONNECTION=pgsql_supabase` + 5 `SUPABASE_DB_*`) subidas con **`python3 push_supabase_env.py`** (lee `.env`, NUNCA imprime valores, usa `--update-env-vars` con delimitador `\x1f` → no pisa otras vars). El `SNAPSHOT_TOKEN` también se subió igual.
- **FIX CRÍTICO de secuencias Postgres:** el `db:port-from-sqlite` dejó las secuencias desfasadas → la PRIMERA inserción en cualquier tabla fallaba (`duplicate key … _pkey`). Se reseteó `setval` en 16 tablas. **Si se re-portan datos, repetir esto** (idealmente meterlo en `db:port-from-sqlite`).
- Datos ya estaban portados (7 users / 110 pages / 187 blogs / 21 tasks). Login en prod verificado (302 → dashboard 200).

### Passwords del equipo
- Nuevo comando **`php artisan app:set-team-passwords`** → password = `<parte-antes-del-@>` + `reneceo`. Aplicado en Supabase prod a los 7 users: joel→`joelreneceo`, josedaniel→`josedanielreneceo`, luna→`lunareneceo`, karol→`karolreneceo`, christopher→`christopherreneceo`, felipe→`felipereneceo`, rene→`renereneceo`. (El entrypoint `app:ensure-admin` nunca resetea passwords existentes → sobreviven redeploys.)

### MCP conectado a Claude — FUNCIONA
- Conector custom en **claude.ai** (web): Settings → Connectors → URL `/mcp/<SNAPSHOT_TOKEN>`. Cargó los **19 tools** sin OAuth. (El token vive en el `.env` de 22d-trello; NO se escribe aquí.)
- También: `claude mcp add --transport http -s user trello-sotsi <url>` para Claude Code.
- 19 tools: lectura (get_status_report, get_kpis, list_tasks, list_team, get_blog_kpis, list_blog_posts…) + escritura (create_task, bulk_create_tasks, update_task, add_follow_up, rate/sotsi_approve/comment blog…). Casi todas con `dry_run`.

### Endpoints de datos para IA externa (3)
- `/snapshot.json?token=` → JSON completo (ahora incluye **blogs**).
- **`/read/<token>`** (NUEVO) → Markdown legible `text/plain`, token en el path (para que ChatGPT/IA lo lea como página). Secciones: **Summary Metrics, Hours by role, Momentum, Team Workload (por persona, tareas+horas abiertas), Priority Tasks, Blogs (counts+series+muestra), Highlights/Risks/Next steps**. `SnapshotController::readable()` + `toMarkdown()`.
- `/mcp/<token>` → MCP en vivo (lee y escribe). ProjectSnapshot ahora trae `blogs` y `visibility` por tarea.

### Tareas privadas (visibility)
- Columna `tasks.visibility` ('team' default = compartida, todas las viejas quedan team; 'private'). `Task::visibleTo(User)` → privada visible solo a **creador + asignados + admin**. `DashboardController` filtra el tablero/`$taskJson` por `visibleTo($me)`, pero **el reporte y el MCP/snapshot/read siguen viendo TODAS** (requisito de Joel). UI: selector Team/Private en composer y modal; badge 🔒 (`.tk-private`) en cards privadas.

### Fix UX al agregar tarea + estilo del edit inline (Opción B)
- **Bug:** local ahora pega a Supabase (más lento que SQLite) → el botón Add no daba feedback → doble-click → tareas duplicadas. **Fix:** `t-add-btn` con spinner (`loading`) + guard `_addingTask`/`_quickAdding` anti-doble-submit en `addTask()` y `commitQuickAdd()`.
- **Opción B (estilo):** el edit inline de la card (`<select>`/título/horas) se veía nativo/gris. Se estilizó con CSS para el look Shoelace: `.tk-sel` con flecha custom (appearance:none) + hover/focus, y `.tk-title-edit`/`.tk-hrs-in` con anillo de foco suave. (No se incrustó `<sl-select>` en las cards por ser frágil al re-render; queda como opción futura el dropdown flotante exacto.)

### Local → Supabase
- `.env` local: `DB_CONNECTION=pgsql_supabase`. **OJO: local ahora escribe en la BD de PROD** (misma Supabase). Pendiente decidir si se separa una BD de pruebas.

### GitHub
- Repo creado: **`github.com/devReneceo/22d-trello`** (privado). Se hizo `git init` + remote + **4 commits** + push de `main`. `.env` real queda fuera (gitignored); solo se subió `.env.example`. Se agregó al `.gitignore`: `/database/*.sqlite`, `/storage/framework/*`.
- ⚠️ Caveat del historial: por ser repo nuevo, los archivos de cada feature entraron completos en su commit temático → los commits intermedios no son ejecutables solos, pero **HEAD sí está completo** = igual a prod.

### PENDIENTE (próxima sesión)
- [ ] **Commit + push de los ÚLTIMOS cambios** (NO están en git aún; los 4 commits fueron antes): `resources/views/dashboard.blade.php` (fix add-task) + `public/css/app.css` (estilo edit inline). Sugerido: `feat: add-task loading feedback + inline card edit styling`.
- [ ] **Limpiar tareas duplicadas** creadas por el doble-click (buscar mismo título seguidos, mostrar antes de borrar).
- [ ] **Decidir BD de pruebas** vs local=prod (hoy local escribe en Supabase prod).
- [ ] **Cloud Scheduler keep-alive** (Supabase free se PAUSA tras 7 días sin actividad).
- [ ] **Backup semanal** `pg_dump` → GCS.
- [ ] (Opcional) Dropdown `<sl-select>` flotante real en el edit de card (hoy es CSS que imita).
- Costo de esta sesión: ~$34.26, contexto >200k → se cierra para abrir sesión nueva y barata.
