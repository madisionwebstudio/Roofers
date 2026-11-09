# Roofrs — marketing website

Static marketing site for **Roofrs**, a marketing agency for US roofing contractors. Every page drives toward one action: **book a free Lead-Leak Audit**.

- Plain HTML5 + one CSS file + vanilla JS. No framework, no build step.
- One PHP file (`send.php`) handles both forms.
- Built for shared hosting (Hostinger). Upload the contents of `public_html/` to your `public_html`.

---

## Folder structure

```
public_html/
├── index.html                      Home
├── .htaccess                       gzip, caching, security headers, 404, HTTPS (commented)
├── robots.txt / sitemap.xml
├── send.php                        Form handler (audit + contact) → email
├── 404.html
├── styleguide.html                 Design system: every component (noindex)
├── assets/
│   ├── css/main.css                Tokens, type, components — the whole design system
│   ├── js/config.js                Runtime placeholders: Calendly, GA4, Ads, contact info
│   ├── js/main.js                  Nav, accordions, reveal, count-up, calculator, forms, analytics
│   └── img/
│       ├── icons.svg               Custom 1.5px-stroke icon sprite (<use href="…#i-name">)
│       ├── SHOTLIST.md             Photos to source, with sizes and art direction
│       └── *.jpg / *.webp          Placeholder photos (replace)
├── services/
│   ├── index.html                  Services hub
│   ├── roofing-seo/                + san-antonio-tx/
│   ├── roofing-web-design/         + san-antonio-tx/
│   ├── roofing-marketing/          + san-antonio-tx/   (Google Ads, LSA, Meta)
│   ├── lead-response-automation/
│   ├── reviews-reputation/
│   └── website-care-plans/
├── locations/                      Locations hub
│   └── san-antonio-tx/             City hub (template)
├── pricing/  free-audit/  thank-you/  our-work/  about/  contact/
├── resources/
│   ├── missed-call-calculator/
│   └── lsa-google-ads-migration-2026/
└── privacy/  terms/
```

Each page is `folder/index.html`, so URLs are clean (`/pricing/`). The header and footer are duplicated in every file and identical — if you change one, change them all (search-and-replace works well; see below).

---

## Replace placeholders

All placeholders are in square brackets. Find them all:

```bash
grep -rn "\[[A-Z_ ]*\]" public_html --include=*.html --include=*.php --include=*.js --include=*.xml --include=*.txt | less
```

| Placeholder | Where | Replace with |
|---|---|---|
| `[DOMAIN]` | All HTML (canonical, OG, schema, email), sitemap.xml, robots.txt, send.php, config.js | `roofrs.com` (no https://, no slash) |
| `[US PHONE]` | All HTML (display) | `(210) 555-0142` |
| `[US_PHONE_E164]` | All HTML (`tel:` links) | `+12105550142` |
| `[TO_EMAIL]` | `send.php` | Inbox that receives form leads |
| `[CALENDLY_URL]` | `assets/js/config.js` | Your Calendly event URL |
| `[GA4_ID]`, `[ADS_CONVERSION_ID]`, `[ADS_CONVERSION_LABEL]` | `assets/js/config.js` | Your IDs, then set `analytics.enabled: true` |
| `[DATA: …]` | City pages | Real, dated local numbers (see "Add a city") |
| `[SOURCE: …]` | LSA guide | Links to Google's official pages |
| `[DATE]`, `[STATE]`, `[HOST]`, … | privacy / terms | Your details — then have a lawyer review |
| `[FOUNDER: …]`, `[ADD REAL PHOTO]` | About | Your story and photo |
| `[CASE: …]` | Our Work (hidden until published) | Approved client numbers |

Bulk replace (Mac: use `sed -i ''`; Linux: `sed -i`):

```bash
cd public_html
grep -rl "\[DOMAIN\]" . | xargs sed -i 's/\[DOMAIN\]/roofrs.com/g'
grep -rl "\[US PHONE\]" . | xargs sed -i 's/\[US PHONE\]/(210) 555-0142/g'
grep -rl "\[US_PHONE_E164\]" . | xargs sed -i 's/\[US_PHONE_E164\]/+12105550142/g'
```

### Change the brand name
The name lives in page text, titles, schema and `send.php`. Replace both spellings:

```bash
grep -rl "Roofrs\|ROOFRS" . | xargs sed -i 's/ROOFRS/NEWNAME/g; s/Roofrs/Newname/g'
```
Then update `brandName` in `config.js`, regenerate `og-default.jpg`, `logo.png` and `apple-touch-icon.png`, and check that titles are still ≤ 60 characters.

### Remove the founding-client offer
In `pricing/index.html`, delete everything between `<!-- FOUNDING OFFER: start -->` and `<!-- FOUNDING OFFER: end -->`.

### Publish a case study
In `our-work/index.html`, find `<article class="case" data-state="empty">`, change it to `data-state="filled"` and fill every `[CASE: …]`. Only use numbers the client has approved in writing.

---

## Forms

Both forms post to `/send.php`. With JavaScript the form submits with `fetch`, shows errors inline and then redirects to `/thank-you/`. Without JavaScript it falls back to a normal POST and a 303 redirect.

`send.php`:
- POST only, same-origin check
- Honeypot field (`fax_number`) and minimum fill time — bots get a fake "success"
- Rate limit: 5 submissions per 15 min per IP (file-based) and per session
- Validates every field, strips control characters (no header injection), whitelists select values
- Requires the TCPA/SMS consent box, and records consent text, time, IP, user agent and page in the email
- Sends plain-text email with `mail()`

**Setup:** set `TO_EMAIL` and `FROM_EMAIL` at the top of `send.php`. `FROM_EMAIL` must be a mailbox on your own domain (create it in Hostinger → Emails), or inboxes will treat the message as spoofed. Until `TO_EMAIL` is set, the form deliberately returns "not connected to an inbox yet".

---

## Add a new city page

1. **Copy the templates.** For `omaha-ne`:
   ```bash
   cp -r public_html/locations/san-antonio-tx public_html/locations/omaha-ne
   for s in roofing-seo roofing-web-design roofing-marketing; do
     cp -r public_html/services/$s/san-antonio-tx public_html/services/$s/omaha-ne
   done
   ```
2. **Rewrite the copy, don't just swap the name.** Change the title, meta description, canonical, OG URL, breadcrumbs and the JSON-LD (`areaServed`, BreadcrumbList). Rewrite the market section for that city's storms, insurance mix and suburbs. Aim for at least 60% different from the main service page and from other cities. Remove Texas-specific lines (Insurance Code ch. 707, Spanish-language angle) unless they apply.
3. **Fill the `[DATA: …]` block** with numbers you checked yourself, with dates:
   - Storm season and one recent major storm (with a source link)
   - Top 3 roofers in the Maps pack for "roofer [city]" and their review counts
   - Google Ads CPC range for "roof replacement [city]" (Keyword Planner)
   - Lowest LSA weekly budget you've seen in that market
   - Local notes: insurance share, HOAs, permit rules
   Never estimate local numbers. Leave a placeholder rather than guess.
4. **Link it in.** In `locations/index.html`, change the city from "Coming soon" to a link. Update the "Locations" column in the footer of every page and the city links on the three service pages (`services/*/index.html`, "We work with roofers in").
5. **Add the 4 new URLs to `sitemap.xml`.**

---

## Analytics

Nothing loads until you turn it on. In `assets/js/config.js`, add your GA4 ID (and optionally a Google Ads conversion ID and label), then set `analytics.enabled: true`.

- `generate_lead` (GA4) + the Ads `conversion` fire on every successful form submit.
- `cta_click` fires on every element with `data-track="…"` (all audit buttons, call buttons, plan buttons), with the label and page path.

If you add a cookie banner, gate `analytics.enabled` behind consent.

---

## Pre-launch checklist

- [ ] Brand name final — swapped everywhere (HTML, `send.php`, `config.js`, OG image, logo PNGs)
- [ ] `[DOMAIN]` replaced in HTML, `sitemap.xml`, `robots.txt`, `send.php`, `config.js`
- [ ] Phone (`[US PHONE]`, `[US_PHONE_E164]`) and email (`hello@…`) set and working
- [ ] Real photos added per `assets/img/SHOTLIST.md` (+ founder photo on About)
- [ ] `TO_EMAIL` / `FROM_EMAIL` set in `send.php`; **send a test from both forms** and check spam
- [ ] Calendly URL set in `config.js`; booking tested from `/free-audit/` and `/thank-you/`
- [ ] GA4 + Google Ads conversion IDs added and `analytics.enabled: true`; test in GA4 DebugView
- [ ] Privacy policy and terms filled in and **reviewed by a lawyer** (SMS/TCPA consent especially)
- [ ] LSA guide `[SOURCE: …]` links filled; "Last updated" date checked
- [ ] San Antonio `[DATA: …]` blocks filled with dated numbers (or hide the city pages until they are)
- [ ] Founding-client offer kept or removed
- [ ] SSL active → uncomment the HTTPS redirect in `.htaccess`; choose www or non-www
- [ ] Submit `sitemap.xml` in Google Search Console
- [ ] Run Lighthouse on Home and Free Audit against the live domain
- [ ] Delete or keep `styleguide.html` (it's `noindex` and blocked in robots.txt)

---

## Design system notes

- **Colors:** exact brand tokens in `:root` in `main.css`. One derived token, `--fog` (#A9B3BB), is used for muted text on navy because `--steel` fails contrast there.
- **Orange:** buttons, key numbers, the hi-vis tape and step numbers only. Text on orange is always ink, never white (white on orange fails AA). Big orange numbers only sit on navy for the same reason.
- **Signature elements:** `.pitch-l / .pitch-r / .pitch-gable` (roof-pitch section edges), `.dim` (blueprint dimension lines), `.tape` (hi-vis stripes), `.grid-paper` (engineering-paper texture), `.bignum` (editorial numbers), `icons.svg` sprite.
- **Motion:** `.reveal` fade-up on headings, `data-count` count-up, 2px button lift. All disabled under `prefers-reduced-motion`.
- See `/styleguide.html` for every component.
