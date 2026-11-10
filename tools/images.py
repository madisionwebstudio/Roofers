#!/usr/bin/env python3
"""Download the site photos from Unsplash and export responsive WebP sizes.

Usage:  python3 tools/images.py            (skips files that already exist)
        python3 tools/images.py --force    (re-export everything)

Needs Pillow (pip install pillow). Originals are cached in tools/.img-cache/
(git-ignored). Output: src/static/assets/img/<name>-<width>.webp plus
src/static/assets/img/manifest.json, which tools/build.py reads to write
srcset, width and height on every <img>.

To swap in a real client photo: drop a JPG at tools/.img-cache/<name>.jpg,
delete the matching <name>-*.webp files, and run this script again.
"""
import io, json, os, sys, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", ".img-cache")
OUT = os.path.join(ROOT, "src", "static", "assets", "img")
FORCE = "--force" in sys.argv

# name: (unsplash photo id, photographer, crop aspect w/h or None, focal x 0-1, focal y 0-1, widths, treatment)
PHOTOS = {
    "hero-crew":        ("1635424709870-cdc6e64f0e20", "Raze Solar", 16/9, .62, .55, [640, 960, 1440, 1920, 2400], None),
    "crew-ridge":       ("1635424824849-1b09bdcc55b1", "Raze Solar", 4/3, .45, .5, [480, 800, 1200, 1600], None),
    "roofer-sealant":   ("1635424824800-692767998d07", "Raze Solar", 4/5, .55, .5, [480, 800, 1200], None),
    "roofer-rope":      ("1635424710928-0544e8512eae", "Raze Solar", 4/5, .5, .5, [480, 800, 1200], None),
    "crew-pair":        ("1635424709961-f3a150459ad4", "Raze Solar", 4/3, .5, .5, [480, 800, 1200], None),
    "tear-off":         ("1633759593085-1eaeb724fc88", "Zohair Mirza", 4/3, .5, .5, [480, 800, 1200, 1600], None),
    "shingle-bundles":  ("1643225523483-e2c434191bba", "Zohair Mirza", 4/5, .5, .5, [480, 800, 1200], None),
    "roofer-brick":     ("1632759145351-1d592919f522", "Zohair Mirza", 4/3, .5, .4, [480, 800, 1200], None),
    "storm-house":      ("1748701821466-0b9f8bf839ac", "Steve Gribble", 21/9, .6, .55, [640, 960, 1440, 1920, 2400], None),
    "storm-night":      ("1488226941561-6d7a806ae42a", "Dorin Vancea", 16/9, .5, .55, [640, 960, 1440, 1920, 2400], None),
    "aerial-suburb":    ("1516156008625-3a9d6067fab5", "Breno Assis", 4/3, .5, .5, [480, 800, 1200, 1600], None),
    "aerial-culdesac":  ("1555192881-d1bee8bdfedf", "Michael Tuszynski", 4/3, .5, .5, [480, 800, 1200, 1600], "duotone"),
    "hail-shingles":    ("1782274951165-b88199bde548", "blue soda", 4/3, .5, .5, [480, 800, 1200, 1600], None),
    "metal-roof":       ("1779941373840-a93f6e0d5db0", "Meg", 4/3, .5, .5, [480, 800, 1200, 1600], None),
    "metal-fasten":     ("1780445392484-5fb7d5610708", "Sergio Martins", 4/3, .5, .5, [480, 800, 1200], None),
    "shingle-texture":  ("1518736346281-76873166a64a", "Michael Jasmund", 4/3, .5, .5, [480, 800, 1200, 1600], "duotone"),
    "home-new-roof":    ("1778164909438-c27c813cb480", "Roger Starnes Sr", 4/3, .5, .5, [480, 800, 1200, 1600], None),
    "home-farmhouse":   ("1761013320045-d29e4f10bcbc", "Roger Starnes Sr", 16/9, .5, .55, [640, 960, 1440, 1920], None),
    "home-blue":        ("1780080019323-20a5fb128906", "Roger Starnes Sr", 4/3, .5, .5, [480, 800, 1200], None),
    "home-white-metal": ("1787094497609-5efe6029b950", "Roger Starnes Sr", 4/3, .5, .5, [480, 800, 1200], None),
    "golden-street":    ("1627759337152-1cf00b1bb33e", "Conrad de Wet", 16/9, .5, .5, [640, 960, 1440, 1920], None),
}

NAVY = (15, 30, 46)
ORANGE = (242, 107, 29)
PAPER = (245, 243, 239)


def fetch(name, pid):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".jpg")
    if not os.path.exists(path):
        url = f"https://images.unsplash.com/photo-{pid}?w=2600&q=85&fm=jpg"
        print("download", name)
        with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def crop(img, aspect, fx, fy):
    w, h = img.size
    if aspect is None:
        return img
    if w / h > aspect:
        nw = int(h * aspect); x = int(min(max(fx * w - nw / 2, 0), w - nw))
        return img.crop((x, 0, x + nw, h))
    nh = int(w / aspect); y = int(min(max(fy * h - nh / 2, 0), h - nh))
    return img.crop((0, y, w, y + nh))


def duotone(img):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1)
    return ImageOps.colorize(g, black=NAVY, white=PAPER, mid=(120, 128, 136)).convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    credits = []
    for name, (pid, who, aspect, fx, fy, widths, treat) in PHOTOS.items():
        try:
            src = Image.open(fetch(name, pid)).convert("RGB")
        except Exception as e:  # network failure: keep going, build.py falls back to an SVG placeholder
            print("FAILED", name, e); continue
        img = crop(src, aspect, fx, fy)
        if treat == "duotone":
            img = duotone(img)
        w0, h0 = img.size
        done = []
        for w in widths:
            if w > w0:
                continue
            out = os.path.join(OUT, f"{name}-{w}.webp")
            if FORCE or not os.path.exists(out):
                img.resize((w, round(w * h0 / w0)), Image.LANCZOS).save(out, "WEBP", quality=72 if w > 1000 else 76, method=6)
            done.append(w)
        manifest[name] = {"widths": done, "ratio": round(h0 / w0, 5)}
        credits.append((name, pid, who))
        print("ok", name, done)
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)


if __name__ == "__main__":
    main()
