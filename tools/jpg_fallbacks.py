#!/usr/bin/env python3
"""Make one JPG fallback per image for older iPhones/Safari (iOS 13 and below can't show WebP).

    python3 tools/jpg_fallbacks.py     (needs Pillow; run after adding images)

For every entry in src/static/assets/img/manifest.json it writes <name>-<w>.jpg at one
middle width and records it as "jpg" in the manifest. build.py then emits
<picture><source type="image/webp" srcset=...><img src="...jpg"></picture>.
"""
import json, os
from PIL import Image
IMG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "static", "assets", "img")
man = json.load(open(os.path.join(IMG, "manifest.json")))
for name, info in man.items():
    ws = info["widths"]
    w = max([x for x in ws if x <= 1200] or [ws[0]])
    if any(x > 1200 for x in ws) and w < 1000:  # wide heroes: use the ~1440 size
        w = min(x for x in ws if x > 1200)
    src = os.path.join(IMG, f"{name}-{w}.webp")
    out = os.path.join(IMG, f"{name}-{w}.jpg")
    if not os.path.exists(out):
        Image.open(src).convert("RGB").save(out, "JPEG", quality=72, optimize=True, progressive=True)
    info["jpg"] = w
json.dump(man, open(os.path.join(IMG, "manifest.json"), "w"), indent=1)
print("jpg fallbacks:", len(man))
