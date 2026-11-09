# [BRAND] — roofing marketing website (v3)

Marketing site for an agency that sells **three services to US roofing contractors only: Web Design, SEO and Google Ads (PPC)** — with one goal: more leads for the roofer.

Main promise: **“A perfect website captures more leads — and we know exactly what homeowners look for when they choose a roofing company.”**
Main CTA everywhere: **Get my free website preview** → `/free-preview/` (on the Google Ads page: **Get a free Google Ads plan** → same form, service preselected).

- **Output:** plain HTML + one CSS file + vanilla JS + two PHP files (`send.php`, optional `chat.php`), in `public_html/`. Nothing to install on the server.
- **Hosting:** upload the *contents* of `public_html/` to Hostinger's `public_html`.
- **Source:** `src/` + `config.json`. `python3 tools/build.py` (standard library only) fills in your details, stitches shared parts into pages and writes `public_html/`.

---

## Quick start

```bash
# 1. Put your details in config.json (brand, domain, phone, email, IDs)
# 2. Build
python3 tools/build.py
# 3. Preview locally (PHP so the form works too)
php -S 127.0.0.1:8080 -t public_html
# 4. Upload the contents of public_html/ to Hostinger
```

`tools/build.py` prints warnings for: broken internal links, titles over 62 characters, descriptions outside 70–165
characters, pages without exactly one `<h1>`, and any config value you haven't set yet.

---

## Placeholders — one config file

Everything lives in **`config.json`**. Values still in `[BRACKETS]` are not set yet — the build lists them every time.

| Key | What | Status |
|---|---|---|
| `BRAND` | Business name | `Roofrs` |
| `DOMAIN` | Domain without `https://` (canonicals, sitemap, OG, schema, robots, form origin check) | **`[DOMAIN]` — set it** |
| `US_PHONE` | Display phone, e.g. `(608) 555-1234` — use a **local US number**; `tel:` links are generated from it | **`[US_PHONE]` — set it** |
| `EMAIL` | Public email | **`[EMAIL]` — set it** |
| `FOUNDER_NAME`, `FOUNDER_PHOTO`, `FOUNDER_VIDEO` | Founder block (photo 4:5; video = YouTube/Vimeo embed URL or `/assets/video/intro.mp4`) | photo + video **needed** |
| `LINKEDIN_URL`, `FIVERR_URL` | Founder profiles (also in Person schema `sameAs`) | set |
| `PRICE_SEO_LOCAL`, `PRICE_SEO_PRO` | SEO prices used everywhere (pages, schema, chat, llms.txt) | **`[CONFIRM]` $597 / $997** |
| `LAUNCH_PRICING` | `"on"`/`"off"` — shows or hides every launch-price line | `on` |
| `LAUNCH_LINE` | Wording; `{after}` becomes the later price | “Launch price — goes to {after} after our first 10 roofing clients.” |
| `DISPLAY_FONT` | `"anton"` (Anton + Barlow Condensed) or `"archivo"` | `anton` |
| `TO_EMAIL`, `FROM_EMAIL` | Lead inbox / sender on your domain (`send.php`) | needed |
| `CALENDLY_URL`, `GA4_ID`, `GADS_CONVERSION_ID`, `GADS_FORM_LABEL`, `GADS_CALL_LABEL` | Booking + tracking | needed |
| `SAME_AS` | Business profile URLs (Google Business Profile, Facebook…) → Organization `sameAs` | optional |
| `CHAT_AI` | `"on"` = chat sends unanswered questions to Claude (see below) | `off` |

### Placeholders that stay visible on purpose
These are content gaps for *you* to fill. The build highlights them in orange on the page so they can't slip through:

- `[SOURCE NEEDED: …]` — blog articles and city page. Add a link to the real source, or delete the claim.
- `[DATA: …]` — San Antonio local facts. Fill with dated, checked numbers (see `docs/ADD-A-CITY.md`).
- `[ADD: …]` — founder story (About), legal details (Privacy/Terms).
- `[IMAGE: …]`, `[REVIEW TEXT …]`, `[Reviewer name]`, `[VIDEO_1]`, `[VIDEO_2]` — Vidales Law screenshot, 3 Fiverr reviews (copy word for word), 2 video testimonials (in `src/partials/proof-other.html`).

Find them all: `grep -rn "\[SOURCE NEEDED\|\[DATA:\|\[ADD:\|\[IMAGE\|\[REVIEW\|\[VIDEO" src`

---

## Folder structure

```
config.json                 ← your details (the one place)
src/
  pages/                    ← one file per page; folder = URL (pages/pricing/index.html → /pricing/)
  partials/                 ← header, footer, final CTA, price cards, fine print, admin mock, founder…
  static/                   ← copied as-is: CSS, JS, fonts, images, send.php, .htaccess, robots.txt, assets/data/work.json
tools/
  build.py                  ← builds public_html/
  images.py                 ← downloads Unsplash photos, exports responsive WebP + manifest.json
  brand/render.js           ← OG image, logo PNGs, founder placeholder
  shoot.js                  ← QA screenshots (Playwright)
docs/ADD-A-CITY.md
public_html/                ← BUILD OUTPUT — upload this. Don't edit by hand; edit src/ and rebuild.
design/mockups/             ← v1 exploration mockups (not part of the site)
```

### Page front matter
Each page starts with a JSON comment the build reads:
```html
<!--meta {"title": "...", "description": "...", "path": "/pricing/",
  "crumbs": [["Home","/"],["Pricing","/pricing/"]],   → breadcrumbs + BreadcrumbList schema
  "preload": "hero-crew",                              → preloads the hero image
  "service": {...}, "article": {...}, "noindex": true } -->
```
Helpers inside pages: `<!--@include name-->` (a partial), `{{img name="crew-ridge" alt="…" sizes="…"}}` (responsive WebP
with width/height/lazy loading), `{{work}}` / `{{work limit="1"}}` (before/after cards from work.json), `{{qform service="seo"}}` (hero lead form), `{{launch after="$699"}}` (launch-price line), `{{crumbs}}`.
FAQ schema is generated automatically from `<details class="faq-item">` blocks.

---

## Forms → `send.php`

`/free-preview/` and `/contact/` post to `/send.php`. With JS: inline validation, `fetch`, redirect to `/thank-you/`.
Without JS: normal POST and 303 redirect.

- POST only, same-origin check, honeypot (`fax_number`) + 3-second minimum fill time (bots get a fake success)
- Rate limit: 5 submissions / 15 min per IP
- Validates and sanitizes every field; strips control characters (no header injection); whitelists services/logo values
- Requires the SMS/phone/email consent box and records consent text, time, IP, browser and page
- Emails the lead to `TO_EMAIL` **and** appends it to **`../form-leads/leads.csv` — one level above `public_html`, not web-reachable**
  (spreadsheet formulas are neutralized). If email fails, the lead is still saved.
- **Test it after upload:** submit both forms, check the inbox *and spam*, and check `form-leads/leads.csv` in Hostinger's File Manager.

## Analytics
Nothing loads until `GA4_ID` is set. Then:
- `generate_lead` (GA4) + Ads conversion (`GADS_FORM_LABEL`) on every successful form submit
- `phone_click` + Ads conversion (`GADS_CALL_LABEL`) on every `tel:` link
- `cta_click` on every element with `data-cta="…"` (all CTAs have one), with the CTA name and page

If you add a cookie banner, only set `GA4_ID` behind consent.

---

## SEO setup (follows the Territory local SEO manual)

- **Titles** are keyword-first and ≤ 60 characters (`build.py` warns above 60), e.g. “Roofing Website Design for Contractors | Brand”. **Descriptions** are 140–160 characters with the service, the benefit and the offer.
- **Every H1 contains the target term** as a small keyword line (`<span class="h1-kw">Roofing website design</span>`) above the big sales headline, so the page keeps its punchy headline and still ranks for the term.
- **Cities always include the state** (“San Antonio, Texas” / “TX”) in titles, H1s and schema (`addressRegion` via `containedInPlace`).
- **Schema:** Organization (+ `contactPoint` with hours, `slogan`, `knowsAbout`, and `sameAs` from config), WebSite, Service (with `audience: Roofing contractors` and offers), BreadcrumbList, FAQPage, Article + Person. No LocalBusiness address and no Google Business Profile storefront: we're a remote operator and the manual is clear that faking a local address risks suspension.
- **`/llms.txt`** gives AI assistants a plain, consistent summary of the business, prices and key pages (the “AI answers” surface).
- `index, follow, max-image-preview:large` on indexable pages, Twitter title/description, OG image alt.
- Every page links to `/free-preview/` and `/pricing/`; no orphan pages; tested at 360 px.

Still on you (from the manual's 26-week tracker): local phone number in `config.json`, `SAME_AS` profiles, Bing Places / Apple Business Connect, 15–20 real citations, real case studies (replace demo builds), and a review system.

---

## Chat assistant (bottom-right on every page)

- A button opens a chat panel. It answers common questions **instantly from a built-in list** (`src/static/assets/js/chat.js` → `KB`): $0 upfront, pricing, ownership, 12-month minimum, timeline, SEO, guarantees, ads, admin panel, pages, redesigns, team, examples.
- **“Leave my details”** walks the visitor through name → company → city → phone → email → consent, then posts the lead **with the full chat transcript** to `send.php` (`form=chat`). It arrives in `TO_EMAIL` and `form-leads/leads.csv` like the other forms, and fires `generate_lead` + the Ads conversion.
- `chat.js` only loads when someone hovers or taps the button, so it costs nothing on page speed.
- Edit the answers in the `KB` list in `chat.js` (keywords → answer) and rebuild.

### Optional: real AI answers (Claude)
1. Create an API key at console.anthropic.com.
2. On Hostinger, create `private/anthropic-key.txt` **one level above** `public_html` (next to `form-leads/`) containing only the key. Never put it in `public_html`, `config.json` or git.
3. Set `"CHAT_AI": "on"` in `config.json`, rebuild, upload.

`chat.php` then sends questions to Claude (`claude-opus-5-5`, low effort, short answers) with a system prompt containing only your real offer and prices, and rules against inventing facts or promising rankings. It's rate-limited (30 replies per IP per hour), same-origin only, and falls back to the built-in answers if the key is missing or the API is down. Cost: each reply is one API call billed to your Anthropic account. Edit the facts in `chat.php` if your prices change.

---

## Pricing (single source of truth — keep these consistent)
- **Starter Site** (1–3 pages): **$499** one-time (launch price → $699). 12 months hosting & care, then $29/month.
- **Pro Site** (4–10 pages incl. up to 3 city pages): **$199/month**, 12-month minimum (→ $299/month) — own it early by paying the difference to $1,499 — or **$1,499** one-time (→ $1,999). Admin panel + 1 month of SEO free.
- **SEO:** Local SEO `[PRICE_SEO_LOCAL]`/mo · SEO Pro `[PRICE_SEO_PRO]`/mo · 6 months → 3 landing pages free.
- **Google Ads:** **$399** setup + **10%** of ad spend · **$2,000/month** minimum budget paid directly to Google · weekly reports.
Prices appear in: `src/partials/price-cards.html`, `pricing`, the three service pages, `faq-core.html`, `terms`, `chat.js` (KB), `chat.php`, `llms.txt`, and the blog cost article. Search for the number before changing it.

## Our Work — before/after redesigns (`src/static/assets/data/work.json`)
Home shows the first entry; `/our-work/` shows all. Each entry: `name, city, state, status ("concept"|"client"), before_img, after_img, mobile_img, live_url, description, improvements[], note`. Entries with an empty `name` render as “Your roofing company here” slots.
- **Honesty rules:** `concept` shows the badge “Redesign concept — not a client”; switch to `client` only after they sign. Improvements must be measurable and true (Hardtland's scores were measured with Lighthouse on both sites).
- **Add a redesign:** screenshot the current site and your redesign at 1440×900 and the redesign on a phone at 390×844 @2x, convert to WebP (see SHOTLIST.md), add the names to `src/static/assets/img/manifest.json` like the `work/hardtland-*` entries, fill a slot in `work.json`, rebuild.
- “Other proof” (Roll n' Brush, Vidales Law, Fiverr reviews, video testimonials) lives in `src/partials/proof-other.html`.

## Service pages = Google Ads landing pages
`/roofing-web-design-agency/`, `/roofing-seo-agency/`, `/roofing-marketing-agency/` each have a short lead form in the hero (`{{qform service="…"}}`), the keyword in the H1, a CTA every couple of sections, Service + FAQPage + BreadcrumbList schema, and a sticky mobile CTA bar.
**Attribution:** `main.js` reads `utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid` from the landing URL, keeps them for the visit, and adds them (plus the landing page) as hidden fields to every form and chat lead. They appear in the lead email (“Source:” line) and in `form-leads/leads.csv`. `?service=web-design|seo|google-ads` preselects the service on `/free-preview/`.

## Add a blog post
1. Copy `src/pages/blog/do-roofers-need-seo/` to a new folder (the slug is the URL).
2. Update the front matter (`title`, `description`, `path`, `crumbs`, `article.date`, `article.image`).
3. Write it. No invented stats — mark anything unsourced `[SOURCE NEEDED: …]` until you add a link.
4. Add a card to `src/pages/blog/index.html` and a link in `src/partials/article-aside.html`. Build.

(Client blogs are published from their own admin panel — that's a separate project. This is the agency's own blog.)

## Add a city page
See **`docs/ADD-A-CITY.md`**. Short version: copy the San Antonio template, rewrite ≥60% for the city, fill the
`[DATA: …]` block with real dated numbers, never invent local facts.

## Photos
See `src/static/assets/img/CREDITS.md` (every photo, photographer, source) and `SHOTLIST.md` (what to replace with real photos first).

---

## Pre-launch checklist

- [ ] `config.json`: BRAND, DOMAIN, real phone, real email, founder photo → `python3 tools/build.py`
- [ ] Brand changed? Re-run `tools/brand/render.js` (OG image, logo, icons)
- [ ] `TO_EMAIL` + `FROM_EMAIL` set; `FROM_EMAIL` mailbox exists on your domain; **test both forms**, check spam and `form-leads/leads.csv`
- [ ] `CALENDLY_URL` set; booking tested on `/thank-you/`
- [ ] GA4 + Ads IDs/labels set; test events in GA4 DebugView and Google Tag Assistant
- [ ] Real founder photo + founder background (`/about/` `[ADD: …]`)
- [ ] All `[SOURCE NEEDED: …]` replaced with links (or claims removed) — 3 blog posts + San Antonio
- [ ] San Antonio `[DATA: …]` filled with dated facts — or don't link the page until it is
- [ ] Privacy policy + terms completed and **reviewed by a lawyer** (TCPA/SMS consent, the 12-month minimum, early-exit terms)
- [ ] Confirm the admin-panel features shown on the site match what the admin-panel project actually ships
- [ ] Swap the top 3–5 photos from `SHOTLIST.md` for real ones
- [ ] SSL active → uncomment the HTTPS (and www/non-www) redirect in `.htaccess`
- [ ] Submit `https://DOMAIN/sitemap.xml` in Google Search Console
- [ ] Lighthouse (mobile) on Home, Free Preview, Pricing against the live domain
- [ ] `styleguide.html` is `noindex` and disallowed in robots.txt — keep or delete

---

## Key decisions (made without asking, as briefed)

1. **Rebuilt from scratch.** v1 sold a “Lead-Leak Audit”; v2 is a different offer, sitemap and design. Old v1 URLs 301-redirect to their closest v2 page (`.htaccess`).
2. **Tiny build script, static output.** Hand-duplicating a header/footer across 20 pages is how sites drift and break. `tools/build.py` (stdlib Python) does includes, placeholders, responsive images, schema, sitemap and link checks. The server only ever sees static files + `send.php`.
3. **Whole CSS inlined as critical CSS.** It's ~11 KB gzipped, so inlining it removes the only render-blocking request. Fonts self-hosted (Fontsource, OFL); only Anton is preloaded.
4. **Derived colors for accessibility:** `--orange-ink #B3480B` for orange *text* on light backgrounds (brand orange is 2.7:1 on paper — fails AA) and `--fog #A9B3BB` for muted text on navy. Brand orange text appears only on dark backgrounds; buttons use ink text on orange (white on orange fails).
5. ~~Demo builds~~ — replaced in v3 by real before/after redesigns (see v3 decisions).
6. **No fake data anywhere.** Admin panel and report mocks are tagged “Example screen” / “Example layout — not client data” and use “Homeowner A/B/C”. The PageSpeed block is labeled “Sample report — illustration”. No testimonials, star ratings or results — the reviews feature is described, not faked.
7. **Founder bio left for you.** We only wrote what the brief states (founder runs projects, remote team, US Central hours). Background is an `[ADD: …]` block, and the founder photo is a designed placeholder, not a stock face.
8. **Interpretations of the offer you should confirm:**
   - “Preview in 5 days” is counted from the call, once we have the logo and details (stated on the Free Preview page and Terms).
   - $199/month early exit: the remaining months of the 12-month minimum are due, and the site is then yours. After 12 months: stay month to month or take the files.
   - SEO and Google Ads plans are described as **month to month** (the only reason to sign 6 months of SEO is the 3-landing-page bonus).
   - The free SEO month = one month of the Local SEO plan ($597 value), and it doesn't auto-renew.
   - Admin panel claims were kept to the brief (leads, business info, services, photos, text, blog, mobile login) plus regular backups. Lead status tags appear only in the example mock.
   - Logo design is listed as an optional add-on (price not stated); domain registration as a small yearly fee paid to the registrar.
9. **Form leads are saved to CSV outside `public_html` even when `TO_EMAIL` is empty**, so the site works on day one and no lead is lost if email delivery fails.
10. **Growth-first messaging (v2.1).** Headlines lead with the outcome roofers buy — more calls and booked jobs (“Turn Google searches into booked roof jobs”) — not with the website or with paying later. The risk reversal stays in the sub-copy, steps, pricing and FAQ. No result is promised: copy says what the system is *built to* do.
11. ~~Free growth plan~~ — removed in v3; the offer is the free website preview (plus a free Google Ads plan on the Ads page).
12. Font: Archivo was tried in v2; v3 is back on Anton + Barlow Condensed (switchable with `DISPLAY_FONT`).
13. **Chat assistant** works without AI by default (no running cost, no wrong answers); AI answers are opt-in with your own key.
14. **Only one city page**, built as a template with a `[DATA: …]` block. More cities should be added only with real local data (the footer says so).

## v3 decisions
1. **Fonts back to Anton + Barlow Condensed** as the brief says; Archivo stays available (`DISPLAY_FONT`).
2. **Demo builds removed.** Our Work is now real redesigns from `work.json` (Hardtland first) with an honest concept/client badge.
3. **Chat assistant kept** (it's a website feature, not a service we sell) and updated to the v3 offer and prices; still no AI by default.
4. **Placeholders are visible on purpose** (`[DOMAIN]`, `[US_PHONE]`, `[EMAIL]`, `[IMAGE]`, `[REVIEW TEXT]`, `[VIDEO_*]`), so nothing fake ships. Canonicals become correct as soon as `DOMAIN` is set.
5. **The H1 on every page carries the target keyword** as a small line above the headline (e.g. “Roofing web design agency”), so the big sales headline stays readable.
6. **Old URLs 301 → new** in `.htaccess`; `/admin-panel/` → `/roofing-web-design-agency/#admin-panel` (RewriteRule with `NE` so the `#` isn't encoded).
7. Removed the unsourced “$3,000–$10,000” claim and all speed claims except measured, labeled Lighthouse scores.

## Quality checks run (v3)
- Playwright screenshots of every page at 360, 390 and 1440 px: no horizontal scroll; hero H1 fits; form or CTA in the first mobile screen on every service page; Our Work directly under the hero on Home.
- Lighthouse mobile (local PHP server, no gzip; test domain set so canonicals are valid): Home 97/100/100/100 · Web design 96/100/100/100 · SEO 95–96/100/100/100 · Google Ads 97/100/100/100 · Pricing 100/100/100/100 · Free preview 97/100/100/100 (Performance/Accessibility/Best practices/SEO). CLS 0 on all. With `[DOMAIN]` still unset, SEO shows 85 because the canonical and robots sitemap URL are invalid — set `DOMAIN`.
- End-to-end form test from `/roofing-marketing-agency/?utm_source=google&…&gclid=…`: validation → send.php → CSV row with service + UTM + gclid → `/thank-you/`. `?service=google-ads` preselects on `/free-preview/`; attribution persists across pages; chat leads carry it too.
- Before/after slider works with mouse, touch and keyboard (arrow keys).
- JSON-LD valid on all pages: Organization, WebSite, Person (sameAs LinkedIn/Fiverr), Service + offers, FAQPage, BreadcrumbList, Article.
- `.htaccess` redirects reviewed by hand (no Apache available locally) — **test them on Hostinger after upload**: `/roofing-websites/`, `/roofing-seo/`, `/roofing-google-ads/`, `/admin-panel/`, `/blog/do-roofers-need-seo/`.
- Site-wide search: no `example.com`, `555`, `lorem`, `growth plan`, `CRM`, `automation`, `text-back` in visible text.
