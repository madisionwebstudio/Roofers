# Shot list — photos to replace with real client photos

The site launches with high-quality Unsplash roofing photos (see CREDITS.md). Real photos of real crews always win.
Replace them as soon as you can, starting at the top of this list.

**How to replace one:** save your photo as `tools/.img-cache/<name>.jpg` (at least 2400px wide for heroes, 1600px for the rest),
delete `src/static/assets/img/<name>-*.webp`, then run `python3 tools/images.py && python3 tools/build.py`.
The script crops to the right shape (aspect ratios below) around the center — adjust the focal point in `tools/images.py` if needed.

**Art direction:** real roofs, real crews, overcast or golden-hour light. Leave calm space on the LEFT of hero photos
(the headline sits there behind a navy gradient). No posed handshakes, no laptops, no hard-hat-and-clipboard stock.

| Priority | Name | Shape | What to shoot | Used on |
|---|---|---|---|---|
| 1 | `founder` (set `FOUNDER_PHOTO` in config.json) | 4:5 portrait, 800×1000+ | The founder, natural light, on a call or at a desk. No suit needed. | Home, About, blog bylines |
| 2 | `hero-crew` | 16:9 | Crew on a steep shingle roof mid-install, harnesses on, subject on the right third | Home hero, OG image |
| 3 | `storm-night` | 16:9 | Dark storm sky over suburban homes, rooflines along the bottom | Final CTA on every page |
| 4 | `storm-house` | 21:9 | Shelf cloud or storm rolling over houses, late afternoon | Home band, Google Ads |
| 5 | `home-new-roof` | 4:3 | A freshly finished re-roof, whole house in frame | Roofing websites hero |
| 6 | `hail-shingles` | 4:3 | Close-up of real hail damage on asphalt shingles (with the homeowner's permission) | Google Ads, San Antonio |
| 7 | `crew-truck` (new) | 4:3 | Crew unloading ladders and shingles from the work truck | Suggested for About |
| 8 | `aerial-suburb` | 4:3 | Drone shot over a neighborhood you actually work in | Roofing SEO |
| 9 | `golden-street` | 16:9 | A finished home at golden hour | About hero |
| 10 | `metal-roof` | 4:3 | A standing-seam metal roof you installed | Contact |

## Our Work screenshots (`assets/img/work/`)
For each roofing redesign: desktop screenshots of the **current site** and **our redesign** at 1440×900 (same size, top of page) and a phone screenshot of the redesign at 390×844 @2x. Save as WebP at 640/1000/1440 (desktop) and 240/390 (phone), add them to `manifest.json` (see README → “Add a redesign”) and to `assets/data/work.json`.

Still needed: `[IMAGE]` Vidales Law website + Google Search Console results screenshot · founder photo · founder 60-second video · 2 client video testimonials.
