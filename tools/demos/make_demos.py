#!/usr/bin/env python3
"""Render the three DEMO roofing homepages and screenshot them for /our-work/.

These are fictional companies built to show our design work. They are always
labeled "Demo build" on the site. Replace them with real client screenshots
as soon as you have permission (see README > "Add your work").

    python3 tools/demos/make_demos.py   (needs Playwright + Chromium, Pillow)
"""
import json, os, re, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(ROOT, "src", "static", "assets", "img")
FONTS = os.path.join(ROOT, "src", "static", "assets", "fonts")

DEMOS = {
 "demo-ironpitch": dict(
   name="Ironpitch Roofing Co.", city="San Antonio, TX", phone="(210) 555-0187", url="ironpitchroofing.example",
   bg="#101820", fg="#fff", accent="#D7322B", accent_fg="#fff", paper="#F4F1EC", ink="#101820",
   head="Anton", body="Inter", photo="crew-ridge-1200", layout="left",
   h1="San Antonio's<br>storm-damage<br>roofers.", sub="Hail, wind and leak repairs. Full roof replacements. We meet your adjuster on the roof.",
   cta="Get a free inspection", badges=["Licensed &amp; insured", "Insurance claim help", "Financing available"],
   services=[("Roof replacement", "tear-off"), ("Storm &amp; hail damage", "hail-shingles"), ("Roof repair", "roofer-sealant")]),
 "demo-cedarslate": dict(
   name="Cedar &amp; Slate Roofing", city="Omaha, NE", phone="(402) 555-0119", url="cedarandslate.example",
   bg="#F7F5F0", fg="#1E2A22", accent="#2F5D45", accent_fg="#fff", paper="#ffffff", ink="#1E2A22",
   head="Barlow Condensed", body="Inter", photo="home-farmhouse-1440", layout="split",
   h1="Roofs built for Nebraska winters.", sub="Family-owned roofing for Omaha homes. Asphalt, metal and cedar. Clear written quotes within 48 hours.",
   cta="Request a quote", badges=["Free written estimates", "Manufacturer-certified", "Since 2009"],
   services=[("Asphalt shingles", "home-new-roof"), ("Metal roofing", "metal-roof"), ("Gutters &amp; siding", "home-blue")]),
 "demo-bluebonnet": dict(
   name="Bluebonnet Roof Works", city="Austin, TX", phone="(512) 555-0164", url="bluebonnetroofworks.example",
   bg="#0B0D10", fg="#fff", accent="#F5C518", accent_fg="#0B0D10", paper="#EEF0F2", ink="#0B0D10",
   head="Barlow Condensed", body="Inter", photo="storm-house-1440", layout="center",
   h1="Hail hit last night?<br>We're on it today.", sub="24/7 emergency tarping, insurance claim help and full replacements across Central Texas.",
   cta="Book an inspection", badges=["24/7 emergency tarping", "Claims help", "0% financing options"],
   services=[("Emergency tarping", "crew-pair"), ("Hail damage", "hail-shingles"), ("Metal roofs", "metal-fasten")]),
}


def page(key, d):
    f = f"file://{FONTS}"
    svc = "".join(f'<div class="svc"><img src="file://{IMG}/{img}-480.webp" width="480" height="360" loading="lazy" alt=""><h3>{n}</h3><p>Clear scope, photos of every step, and a written warranty.</p><a>Learn more →</a></div>' for n, img in d["services"])
    badges = "".join(f"<li>✓ {b}</li>" for b in d["badges"])
    hero_img = f"file://{IMG}/{d['photo']}.webp"
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><style>
@font-face{{font-family:Anton;src:url({f}/anton-latin-400-normal.woff2)}}
@font-face{{font-family:"Barlow Condensed";font-weight:800;src:url({f}/barlow-condensed-latin-800-normal.woff2)}}
@font-face{{font-family:"Barlow Condensed";font-weight:700;src:url({f}/barlow-condensed-latin-700-normal.woff2)}}
@font-face{{font-family:Inter;font-weight:400;src:url({f}/inter-latin-400-normal.woff2)}}
@font-face{{font-family:Inter;font-weight:600;src:url({f}/inter-latin-600-normal.woff2)}}
*{{box-sizing:border-box;margin:0}}body{{font:400 17px/1.55 Inter,sans-serif;color:{d['ink']};background:{d['paper']}}}
h1,h2,h3,.logo{{font-family:"{d['head']}";font-weight:{400 if d['head']=='Anton' else 800};text-transform:uppercase;line-height:.95}}
.top{{background:{d['bg']};color:{d['fg']};display:flex;align-items:center;gap:28px;padding:18px 5vw;font-weight:600;font-size:15px}}
.logo{{font-size:26px;margin-right:auto;letter-spacing:.02em}}.logo i{{color:{d['accent']};font-style:normal}}
.top nav{{display:flex;gap:24px}}.ph{{font-weight:700}}
.b{{background:{d['accent']};color:{d['accent_fg']};padding:14px 22px;font:800 17px "Barlow Condensed";text-transform:uppercase;letter-spacing:.05em;display:inline-block;border-radius:3px}}
.hero{{position:relative;color:#fff;min-height:620px;display:flex;align-items:center;padding:80px 5vw;background:url({hero_img}) center/cover}}
.hero:before{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.82),rgba(0,0,0,.35))}}
.hero>div{{position:relative;max-width:760px}}.hero h1{{font-size:clamp(46px,7vw,96px);margin:14px 0 18px}}.hero p{{font-size:20px;max-width:560px;margin-bottom:28px;opacity:.92}}
.kick{{font:700 15px "Barlow Condensed";text-transform:uppercase;letter-spacing:.14em;color:{d['accent'] if d['accent']!='#2F5D45' else '#fff'}}}
.badges{{display:flex;flex-wrap:wrap;gap:10px 26px;list-style:none;padding:0;margin-top:30px;font-weight:600;font-size:15px}}
.split .hero{{background:{d['bg']};color:{d['ink']};padding:0;min-height:600px}}.split .hero:before{{display:none}}
.split .hero>div{{max-width:none;display:grid;grid-template-columns:1fr 1fr;width:100%;min-height:600px}}.split .copy{{padding:80px 5vw;align-self:center}}.split .pic{{background:url({hero_img}) center/cover}}
.center .hero{{text-align:center;justify-content:center}}.center .hero>div{{max-width:900px}}.center .hero p{{margin-inline:auto}}.center .badges{{justify-content:center}}
.trust{{display:grid;grid-template-columns:repeat(4,1fr);background:{d['bg']};color:{d['fg']};text-align:center}}.trust div{{padding:26px 10px;border-right:1px solid rgba(127,127,127,.25);font:700 16px "Barlow Condensed";text-transform:uppercase;letter-spacing:.08em}}.trust b{{display:block;font-size:34px;color:{d['accent']}}}
.sec{{padding:80px 5vw}}.sec h2{{font-size:52px;margin-bottom:34px;max-width:800px}}
.svcs{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}}.svc{{background:#fff;border:1px solid rgba(0,0,0,.08)}}.svc img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}}.svc h3{{font-size:28px;padding:18px 20px 6px}}.svc p{{padding:0 20px;font-size:15px;opacity:.8}}.svc a{{display:block;padding:12px 20px 20px;font-weight:700;color:{d['accent'] if d['accent']!='#F5C518' else '#8a6d00'}}}
.storm{{background:{d['bg']};color:{d['fg']};display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:center}}.storm img{{width:100%;aspect-ratio:4/3;object-fit:cover}}.storm ol{{padding-left:22px;margin:18px 0 26px}}.storm li{{margin:8px 0}}
.fin{{display:grid;grid-template-columns:1.2fr 1fr;gap:40px;align-items:center}}.form{{background:#fff;padding:30px;border-top:6px solid {d['accent']};box-shadow:0 20px 40px -20px rgba(0,0,0,.3)}}.form div{{border:1px solid #ccc;height:46px;margin:10px 0;border-radius:3px}}.form .b{{width:100%;text-align:center;margin-top:10px}}
.rev{{text-align:center;border:2px dashed rgba(0,0,0,.2);padding:40px;font-weight:600;opacity:.7}}
footer{{background:{d['bg']};color:{d['fg']};padding:50px 5vw;display:flex;justify-content:space-between;font-size:14px;opacity:.95}}
@media(max-width:600px){{.top nav,.top .ph{{display:none}}.top{{padding:14px 18px}}.logo{{font-size:21px}}.top .b{{padding:10px 12px;font-size:14px}}.hero{{min-height:560px;padding:56px 20px}}.split .hero>div{{grid-template-columns:1fr}}.split .pic{{min-height:260px;order:-1}}.split .copy{{padding:40px 20px}}.trust{{grid-template-columns:1fr 1fr}}.sec{{padding:56px 20px}}.sec h2{{font-size:38px}}.svcs,.storm,.fin{{grid-template-columns:1fr}}footer{{flex-direction:column;gap:10px}}}}
</style></head><body class="{d['layout']}">
<div class="top"><div class="logo">{d['name']}</div><nav><a>Roof Replacement</a><a>Repairs</a><a>Storm Damage</a><a>Financing</a><a>Projects</a></nav><span class="ph">{d['phone']}</span><span class="b">{d['cta']}</span></div>
<section class="hero"><div>{'<div class=copy>' if d['layout']=='split' else ''}<div class="kick">Roofing contractor · {d['city']}</div><h1>{d['h1']}</h1><p>{d['sub']}</p><span class="b">{d['cta']}</span> &nbsp; <span class="b" style="background:transparent;border:2px solid currentColor;color:inherit">Call {d['phone']}</span><ul class="badges">{badges}</ul>{'</div><div class=pic></div>' if d['layout']=='split' else ''}</div></section>
<div class="trust"><div><b>24h</b>Quote turnaround</div><div><b>Free</b>Inspections</div><div><b>Written</b>Workmanship warranty</div><div><b>0%</b>Financing options</div></div>
<section class="sec"><div class="kick" style="color:inherit;opacity:.7">What we do</div><h2>Roofing services in {d['city'].split(',')[0]}</h2><div class="svcs">{svc}</div></section>
<section class="sec storm"><img src="file://{IMG}/hail-shingles-800.webp" width="800" height="600" loading="lazy" alt=""><div><div class="kick">Storm damage?</div><h2 style="margin:10px 0">We help with the insurance claim.</h2><ol><li>Free inspection with photos</li><li>We meet your adjuster on site</li><li>You pay your deductible — we handle the rest</li></ol><span class="b">{d['cta']}</span></div></section>
<section class="sec fin"><div><h2>Need a new roof but not the bill all at once?</h2><p>Monthly payment options through our financing partner. Check your rate in minutes with no impact to your credit score.</p></div><div class="form"><h3 style="font-size:28px">Get your free quote</h3><div></div><div></div><div></div><span class="b">{d['cta']}</span></div></section>
<section class="sec"><h2>What homeowners say</h2><div class="rev">Live Google reviews appear here once connected</div></section>
<footer><div><b>{d['name']}</b><br>{d['city']} · {d['phone']}</div><div>Demo build — fictional company</div></footer>
</body></html>"""


def main():
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    manifest_p = os.path.join(IMG, "manifest.json")
    manifest = json.load(open(manifest_p))
    paths = {}
    for key, d in DEMOS.items():
        p = os.path.join(HERE, "out", key + ".html")
        open(p, "w").write(page(key, d))
        paths[key] = p
    # Web copies for /demos/<name>/ (noindex) so visitors can click through to a live demo
    for key, d in DEMOS.items():
        web = page(key, d).replace(f"file://{FONTS}", "/assets/fonts").replace(f"file://{IMG}", "/assets/img")
        web = web.replace("<meta charset=utf-8>", "<meta charset=utf-8><meta name=robots content=noindex><title>" + d["name"] + " — demo build</title>"
                          "<meta name=description content='Demo roofing website for a fictional company, built by our team.'>")
        web = web.replace("<html>", "<html lang=en>")
        web = re.sub(r"(<body[^>]*>)", r'\1<div style="background:#F26B1D;color:#14181D;font:700 14px Inter,sans-serif;padding:10px 5vw;text-align:center">Demo build by [BRAND] — this is a fictional company. <a href="/our-work/" style="color:#14181D">Back to our work</a></div>', web, count=1)
        out = os.path.join(ROOT, "src", "static", "demos", key.replace("demo-", ""))
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w").write(web)
    js = os.path.join(HERE, "shoot.js")
    subprocess.run(["node", js, json.dumps(paths), os.path.join(HERE, "out")], check=True)
    for key in DEMOS:
        for kind, widths in (("desktop", [640, 1000, 1440]), ("mobile", [240, 390])):
            src = os.path.join(HERE, "out", f"{key}-{kind}.png")
            im = Image.open(src).convert("RGB")
            w0, h0 = im.size
            for w in widths:
                im.resize((w, round(w * h0 / w0)), Image.LANCZOS).save(os.path.join(IMG, f"{key}-{kind}-{w}.webp"), "WEBP", quality=74, method=6)
            manifest[f"{key}-{kind}"] = {"widths": widths, "ratio": round(h0 / w0, 5)}
    json.dump(manifest, open(manifest_p, "w"), indent=1)
    print("demo screenshots done")


if __name__ == "__main__":
    main()
