# Add a city page

City pages only help if they're genuinely local. Google treats near-identical “city swap” pages as doorway pages, and
homeowners can tell. The rule: **at least 60% of the page must be unique to that city, and every local fact must be real.**

## 1. Copy the template
```bash
mkdir -p src/pages/locations/omaha-ne
cp src/pages/locations/san-antonio-tx/index.html src/pages/locations/omaha-ne/index.html
```

## 2. Update the front matter (top of the file)
- `title` (≤ 60 characters), `description` (70–160), `path` (`/locations/omaha-ne/`)
- `crumbs` → `[["Home", "/"], ["Omaha, NE", "/locations/omaha-ne/"]]`
- `service.area` → `{"@type": "City", "name": "Omaha", "containedInPlace": {"@type": "State", "name": "Nebraska"}}`
- `preload` → the hero image name

## 3. Rewrite, don't find-and-replace
- **Hero and market section:** what weather actually hits this city (hail? wind? snow load? hurricanes?), how competitive it is,
  what homeowners there worry about. Remove Texas-specific lines (Texas Insurance Code, Spanish-language note) unless they apply.
- **“What we'd build” features:** pick the 3 that matter most in this market.
- **FAQ:** 3 questions a roofer in this city would actually ask.
- Keep the honest line: “We work with roofers in [City] — remotely.”

## 4. Fill the `[DATA: …]` block — with real, dated numbers
| Field | Where to get it |
|---|---|
| Recent storms | NOAA Storm Events Database / National Weather Service local office. Date + link. |
| Top 3 Maps competitors + review counts | Search “roofer [city]” in an incognito window, note the map pack and the date you checked. |
| Local CPC | Google Ads Keyword Planner for “roof replacement [city]”, “roof repair [city]”. Date it. |
| Suburbs served | Only towns your clients actually serve. |
| Local notes | Permits, HOAs, common roof types — only what you've verified. |

Never estimate. If you don't have a number, leave the placeholder and don't publish the page yet.
Remove the dashed `datablock` styling once it's filled (or keep the facts in a normal section).

## 5. Link it in and build
- Add the city to the “Where we work” list in `src/partials/footer.html`.
- Optionally link it from `/roofing-seo/` or `/roofing-websites/`.
- Replace every `[SOURCE NEEDED: …]` with a real source link, or delete the claim.
- Run `python3 tools/build.py` — the sitemap updates automatically and the build warns about broken links, title length and H1 count.
