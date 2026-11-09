# Working notes for this project

## Deliverables — every time the site changes
The owner uses an **older iPhone (older iOS) that cannot open claude.ai artifacts**. So after every change:
1. Rebuild (`python3 tools/build.py`), commit and push.
2. Republish the clickable artifact (preview copy with relative links — see the preview script used before).
3. **Always also send files that open on any iPhone, via SendUserFile:**
   - a PDF of phone-size screenshots (390 px wide @2x) of Home, the 3 service pages, Pricing, Our Work and Free Preview, one phone screen per PDF page;
   - 1–2 JPG screenshots of what changed (phone + desktop).
4. Send the zips (`public_html` upload zip + full project) when asked.

## Older iPhone / Safari support (keep it)
- Every photo is a `<picture>` with WebP + one JPG fallback (`tools/jpg_fallbacks.py` after adding images).
- No `inset:` shorthand (use top/right/bottom/left), `-webkit-clip-path` alongside `clip-path`,
  `.btn--arrow` class instead of `:has()`, `aspect-ratio` fallbacks in main.css.

## Rules from the owner's briefs
- Services: Web Design, SEO, Google Ads only. Main CTA "Get my free website preview".
- Prices: Starter $499 · Pro $199/mo (12-mo min, buyout to $1,499) or $1,499 · SEO from config · Ads $399 setup + 10% of spend, $2,000/mo min.
- Never invent reviews, results, clients or stats. Placeholders stay visible in [BRACKETS].
