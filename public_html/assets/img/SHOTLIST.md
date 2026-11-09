# Roofrs — photo shot list

Every photo on the site is currently a blueprint-style placeholder with the same filename the real photo should use.
Replace each pair (`.jpg` + `.webp`) at the size listed. Keep filenames, or update the `<picture>` tags.

**Art direction for all shots:** real roofs, real crews, overcast or golden-hour light. Slightly desaturated (−15 to −25% saturation), cool shadows. No staged handshakes, no people pointing at laptops, no hard-hat-and-clipboard stock. Leave calm space where text may sit — the site adds a navy overlay.

**Export:** JPG at quality ~78 and WebP at ~72. Keep the hero under 250 KB (WebP), others under 150 KB.
`cwebp -q 72 in.jpg -o out.webp` or Squoosh.app.

| File | Size (px) | Orientation | Subject | Mood | Used on |
|---|---|---|---|---|---|
| `hero-storm-sky-suburb` | 1920×1080 | Landscape | Dark storm clouds over a row of suburban homes, rooflines visible along the bottom third | Heavy, tense, just before the storm | Home hero (at ~18% opacity behind navy) |
| `svc-roofing-seo` | 1200×900 | Landscape 4:3 | Drone shot looking straight down or at 45° on a neighborhood of shingle roofs | Orderly, mapped, wide | Roofing SEO, Services hub |
| `svc-web-design` | 1200×900 | Landscape 4:3 | Roofer at the tailgate of a work truck, looking at a quote on a phone | Real, mid-workday | Web Design, Services hub |
| `svc-roofing-marketing` | 1200×900 | Landscape 4:3 | Shelf cloud or storm rolling over a cul-de-sac, late afternoon | Dramatic but not apocalyptic | Google Ads / LSA, Services hub |
| `svc-lead-response` | 1200×900 | Landscape 4:3 | Two roofers in harnesses on a steep pitch, mid tear-off (hands busy — the point is nobody can answer the phone) | Busy, physical | Lead Response, Services hub |
| `svc-reviews` | 1200×900 | Landscape 4:3 | Freshly re-roofed house, crew packing up the truck, homeowner on the driveway | Finished, proud, calm | Reviews, Services hub |
| `svc-care-plans` | 1200×900 | Landscape 4:3 | Macro of new architectural shingles and ridge cap, raking light | Precise, crafted | Website Care, Services hub |
| `city-san-antonio` | 1200×900 | Landscape 4:3 | San Antonio-area home with visible hail marks on shingles, South Texas sky | Local, specific, post-storm | Locations hub |
| `founder.jpg` (new) | 800×1000 | Portrait 4:5 | One real founder photo — on a job site or at a desk, natural light, no suit | Honest, approachable | About (replace the dashed placeholder block) |
| `og-default.jpg` | 1200×630 | Landscape | Already designed (brand card). Optionally replace with a photo + wordmark | — | Social shares |

## Demo site screenshots (optional)
The three demo builds on Home and Our Work are drawn in CSS. If you build the real demo sites, replace the `.mock` blocks
with screenshots at 1440×900 (laptop) and 390×820 (phone), keeping the "Demo build — not a client" label.
