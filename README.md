# [BRAND] — roofing agency website (v2: “$0 upfront, pay only if you love it”)

Marketing site for an agency that builds websites, SEO and Google Ads **only for US roofing contractors**.
Every page pushes one action: **Get my free website preview** (`/free-preview/`).

- **Output:** plain HTML + one CSS file + vanilla JS + one PHP form handler, in `public_html/`. No framework, nothing to install on the server.
- **Hosting:** upload the *contents* of `public_html/` to Hostinger's `public_html`.
- **Source:** `src/` + `config.json`. A small Python script (`tools/build.py`, standard library only) fills in your details,
  stitches the shared header/footer into each page and writes `public_html/`.

> The default brand in `config.json` is “Roofrs” (from v1), with a fictional 555 phone number and `example.com`.
> Change them before launch — see below.

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

Everything lives in **`config.json`**. Each `[KEY]` in the source is replaced site-wide (HTML, PHP, JS, robots.txt, sitemap).

| Key | What | Default |
|---|---|---|
| `BRAND` | Business name (logo wordmark, titles, schema, emails) | `Roofrs` |
| `DOMAIN` | Domain without `https://`, e.g. `roofrs.com` (canonicals, sitemap, OG, schema, form origin check) | `example.com` |
| `FOUNDER_NAME` | Founder name | `Rakesh Dadhich` |
| `FOUNDER_PHOTO` | Path to founder photo (4:5) | `/assets/img/founder-placeholder.webp` (designed placeholder) |
| `US_PHONE` | Display phone; the `tel:` link (`[US_PHONE_E164]`) is generated from it | `(210) 555-0142` (fictional) |
| `EMAIL` | Public email | `hello@example.com` |
| `CALENDLY_URL` | Calendly event URL (embedded on `/thank-you/`). Empty = “we'll call you” fallback | empty |
| `GA4_ID` | GA4 measurement ID. Empty = no analytics script at all | empty |
| `GADS_CONVERSION_ID` | Google Ads ID (`AW-…`) | empty |
| `GADS_FORM_LABEL` / `GADS_CALL_LABEL` | Ads conversion labels for form submits and phone clicks | empty |
| `TO_EMAIL` | Inbox that receives leads (`send.php`) | empty |
| `FROM_EMAIL` | Sender — must be a mailbox on your own domain (create it in Hostinger → Emails) | empty |

**If you change the brand name**, also re-render the bitmaps that contain it:
`node tools/brand/render.js "NewBrand" "Founder Name"` then convert the founder placeholder (or just add a real founder photo).

### Placeholders that stay visible on purpose
These are content gaps for *you* to fill. The build highlights them in orange on the page so they can't slip through:

- `[SOURCE NEEDED: …]` — blog articles and city page. Add a link to the real source, or delete the claim.
- `[DATA: …]` — San Antonio local facts. Fill with dated, checked numbers (see `docs/ADD-A-CITY.md`).
- `[ADD: …]` — founder background (About), non-roofing past work (Our Work), legal details (Privacy/Terms).

Find them all: `grep -rn "\[SOURCE NEEDED\|\[DATA:\|\[ADD:" src/pages`

---

## Folder structure

```
config.json                 ← your details (the one place)
src/
  pages/                    ← one file per page; folder = URL (pages/pricing/index.html → /pricing/)
  partials/                 ← header, footer, final CTA, price cards, fine print, admin mock, founder…
  static/                   ← copied as-is: CSS, JS, fonts, images, send.php, .htaccess, robots.txt, /demos/
tools/
  build.py                  ← builds public_html/
  images.py                 ← downloads Unsplash photos, exports responsive WebP + manifest.json
  demos/make_demos.py       ← renders + screenshots the 3 demo roofing sites (also publishes them at /demos/…)
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
with width/height/lazy loading), `{{device key="demo-ironpitch" url="…"}}` (browser + phone frame), `{{crumbs}}`.
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

## Add your work
- **Real client site:** screenshot desktop (1440 wide) and phone (390 wide @2x), add like `tools/demos/make_demos.py` does, then
  use `{{device key="client-name" label="Client site" url="…"}}` on `/our-work/` and Home. Only with written permission.
- **Demo builds** stay labeled “Demo build” and their live versions (`/demos/…`) carry a banner saying the company is fictional.
- **Non-roofing work:** fill the `[ADD: …]` block on `/our-work/`, or delete it.

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
5. **Demo builds, honestly labeled.** No real client sites existed, so we built three fictional roofing homepages (Ironpitch, Cedar & Slate, Bluebonnet), screenshotted them into the device frames, label them “Demo build” everywhere, and publish them at `/demos/…` with a “fictional company” banner. Their Lighthouse mobile scores (96/97/98) were measured, not made up.
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
10. **Only one city page**, built as a template with a `[DATA: …]` block. More cities should be added only with real local data (the footer says so).

## Quality checks run
- Playwright screenshots of all 20 pages at 390 and 1440 (plus 375 / 768 / 1024 on key pages): no horizontal scroll; offer + CTA visible in the first screen on mobile and desktop.
- Lighthouse mobile (local PHP server, no gzip — production will be faster): Home 96/100/100/100, Free Preview 96/100/100/100, Pricing 100/100/100/100 (Performance/Accessibility/Best practices/SEO).
- End-to-end form test: validation, submit, CSV write, redirect; `send.php` honeypot, origin check, GET rejection and plain-POST fallback tested with curl.
