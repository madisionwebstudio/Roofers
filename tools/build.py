#!/usr/bin/env python3
"""Build public_html/ from src/ + config.json.

    python3 tools/build.py

Python 3.8+, standard library only. The output is plain static HTML/CSS/JS
(no framework, nothing to install on the server). This script only does the
boring, error-prone parts so you don't have to do them by hand:

  * replaces [BRAND], [DOMAIN], [US_PHONE] ... with the values in config.json
  * stitches the shared header/footer into every page (<!--@include name-->)
  * writes responsive <img> tags from {{img name="..." alt="..."}}
  * inlines main.css as critical CSS, adds canonical/OG/Twitter tags
  * adds JSON-LD: Organization, WebSite, BreadcrumbList, FAQPage (read from
    the page's FAQ markup), Service, Article + Person
  * writes sitemap.xml and checks for broken internal links

Each page in src/pages/ starts with a JSON front-matter comment:
<!--meta {"title": "...", "description": "...", ...} -->
"""
import html, json, os, re, shutil, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "public_html")
TODAY = date.today().isoformat()

cfg = json.load(open(os.path.join(ROOT, "config.json")))
cfg = {k: v for k, v in cfg.items() if not k.startswith("_")}
missing = [k for k, v in cfg.items() if not str(v).strip()]
digits = re.sub(r"\D", "", cfg["US_PHONE"])
cfg["US_PHONE_E164"] = "+1" + digits[-10:] if len(digits) >= 10 else ""
cfg["YEAR"] = str(date.today().year)
BASE = "https://" + cfg["DOMAIN"].strip().rstrip("/")
FOUNDER_FIRST = cfg["FOUNDER_NAME"].split()[0] if cfg["FOUNDER_NAME"] else "the founder"
cfg["FOUNDER_FIRST"] = FOUNDER_FIRST

manifest = json.load(open(os.path.join(SRC, "static", "assets", "img", "manifest.json")))


def tokens(text):
    for k, v in cfg.items():
        text = text.replace("[" + k + "]", str(v))
    return text


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def include(text, depth=0):
    def rep(m):
        p = os.path.join(SRC, "partials", m.group(1).strip() + ".html")
        return include(read(p), depth + 1)
    return re.sub(r"<!--@include\s+([\w\-/]+)\s*-->", rep, text) if depth < 6 else text


ATTR = re.compile(r'(\w[\w\-]*)(?:="([^"]*)")?')


def img_tag(m):
    a = {k: (v if v is not None else True) for k, v in ATTR.findall(m.group(1))}
    a = {k: (True if v == "" and k in ("eager", "high") else v) for k, v in a.items()}
    name = a["name"]
    alt = html.escape(a.get("alt", ""), quote=True) if a.get("alt") is not True else ""
    cls = f' class="{a["class"]}"' if isinstance(a.get("class"), str) else ""
    sizes = a.get("sizes", "100vw")
    eager = a.get("eager") is True or a.get("eager") == "true"
    info = manifest.get(name)
    if not info:  # graceful SVG placeholder so a missing photo never shows as broken
        print("  ! missing image", name)
        return (f'<svg{cls} role="img" aria-label="{alt}" viewBox="0 0 800 600" width="800" height="600" '
                f'style="background:#1F2A37"><path d="M0 420 L400 220 L800 420" fill="none" stroke="#F26B1D" stroke-width="6"/></svg>')
    ws = info["widths"]
    w = ws[-1] if eager or len(ws) < 3 else ws[-2]
    h = round(w * info["ratio"])
    srcset = ", ".join(f"/assets/img/{name}-{x}.webp {x}w" for x in ws)
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    return (f'<img src="/assets/img/{name}-{w}.webp" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{alt}"{cls}{load}>')


def device_tag(m):
    """{{device key="demo-ironpitch" url="ironpitch.example" label="Demo build" alt="..."}} -> browser + phone frame."""
    a = dict(ATTR.findall(m.group(1)))
    k = a["key"]
    alt = a.get("alt", "")
    label = a.get("label", "Demo build")
    desk = img_tag(re.match(r"(.*)", f'name="{k}-desktop" alt="{alt}" sizes="(min-width:1000px) 760px, 92vw"'))
    mob = img_tag(re.match(r"(.*)", f'name="{k}-mobile" alt="" sizes="210px"'))
    return (f'<figure class="device-stage"><div class="browser"><div class="browser__bar" aria-hidden="true"><i></i><i></i><i></i>'
            f'<span class="browser__url">{a.get("url", "")}</span></div><div class="screen screen--scroll" style="--scroll:-68%">{desk}</div></div>'
            f'<div class="phone" aria-hidden="true"><div class="screen screen--scroll" style="--scroll:-70%">{mob}</div></div>'
            f'<span class="label-demo label-chip">{label}</span></figure>')


def preload_tag(name, sizes):
    info = manifest.get(name)
    if not info:
        return ""
    srcset = ", ".join(f"/assets/img/{name}-{x}.webp {x}w" for x in info["widths"])
    return f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset}" imagesizes="{sizes}" fetchpriority="high">\n'


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def faq_schema(body):
    items = re.findall(r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div class="faq-a">(.*?)</div>\s*</details>', body, re.S)
    if not items:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in items]}


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": cfg["BRAND"], "url": BASE + "/",
       "logo": BASE + "/assets/img/logo.png", "email": cfg["EMAIL"], "telephone": cfg["US_PHONE_E164"],
       "founder": {"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"]},
       "areaServed": {"@type": "Country", "name": "United States"},
       "knowsAbout": ["Roofing website design", "Roofing SEO", "Google Ads for roofers", "Local Services Ads"]}

NAV = [("Websites", "/roofing-websites/"), ("SEO", "/roofing-seo/"), ("Google Ads", "/roofing-google-ads/"),
       ("Pricing", "/pricing/"), ("Our Work", "/our-work/"), ("Blog", "/blog/")]


def render(path_rel, raw, css_inline):
    m = re.match(r"\s*<!--meta\s+(\{.*?\})\s*-->", raw, re.S)
    if not m:
        sys.exit(f"{path_rel}: missing <!--meta {{...}} --> front matter")
    meta = json.loads(tokens(m.group(1)))
    body = raw[m.end():]
    url_path = meta["path"]
    canonical = BASE + url_path
    title = meta["title"]
    desc = meta["description"]
    if len(title) > 62:
        print(f"  ! title {len(title)} chars: {url_path}")
    if not (70 <= len(desc) <= 165):
        print(f"  ! description {len(desc)} chars: {url_path}")

    body = include(body)
    # breadcrumbs
    crumbs = meta.get("crumbs")
    if crumbs:
        lis = "".join(
            (f'<li><a href="{u}">{html.escape(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{html.escape(n)}</li>')
            for i, (n, u) in enumerate(crumbs))
        body = body.replace("{{crumbs}}", f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>')
    # make owner-to-do placeholders visible on the page
    body = re.sub(r"\[(SOURCE NEEDED[^\]]*|DATA:[^\]]*|ADD:[^\]]*)\]", lambda m: f'<span class="src-needed">[{m.group(1)}]</span>', body)
    body = re.sub(r"\{\{device\s+(.*?)\}\}", device_tag, body, flags=re.S)
    body = re.sub(r"\{\{img\s+(.*?)\}\}", img_tag, body, flags=re.S)

    page = read(os.path.join(SRC, "partials", "_layout.html"))
    page = include(page)
    nav_html = "".join(
        f'<a href="{u}" data-cta="nav-{n.lower().replace(" ", "-")}"' + (' aria-current="page"' if url_path.startswith(u) else "") + f">{n}</a>"
        for n, u in NAV)
    page = page.replace("{{nav}}", nav_html)

    # JSON-LD graph
    graph = [ORG]
    if url_path == "/":
        graph.append({"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": cfg["BRAND"], "publisher": {"@id": BASE + "/#org"}})
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]})
    if meta.get("service"):
        s = meta["service"]
        node = {"@type": "Service", "name": s["name"], "serviceType": s.get("type", s["name"]), "provider": {"@id": BASE + "/#org"},
                "areaServed": s.get("area", {"@type": "Country", "name": "United States"}), "url": canonical, "description": desc}
        if s.get("offers"):
            node["offers"] = [{"@type": "Offer", "name": o[0], "price": o[1], "priceCurrency": "USD",
                               **({"priceSpecification": {"@type": "UnitPriceSpecification", "price": o[1], "priceCurrency": "USD", "unitText": o[2]}} if len(o) > 2 else {})}
                              for o in s["offers"]]
        graph.append(node)
    if meta.get("article"):
        a = meta["article"]
        graph.append({"@type": "Article", "headline": title.split(" | ")[0], "description": desc, "url": canonical,
                      "image": BASE + f"/assets/img/{a['image']}-1200.webp", "datePublished": a["date"], "dateModified": a.get("modified", a["date"]),
                      "author": {"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"], "url": BASE + "/about/"},
                      "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": canonical})
    if url_path == "/about/":
        graph.append({"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"], "jobTitle": "Founder",
                      "worksFor": {"@id": BASE + "/#org"}, "url": BASE + "/about/"})
    fq = faq_schema(body)
    if fq:
        graph.append(fq)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

    og_img = BASE + "/assets/img/" + (meta.get("og") or "og-default.jpg")
    robots = '<meta name="robots" content="noindex, follow">\n' if meta.get("noindex") else ""
    preload = preload_tag(meta["preload"], meta.get("preloadSizes", "100vw")) if meta.get("preload") else ""
    site_js = {"calendly": cfg["CALENDLY_URL"], "adsId": cfg["GADS_CONVERSION_ID"],
               "adsFormLabel": cfg["GADS_FORM_LABEL"], "adsCallLabel": cfg["GADS_CALL_LABEL"]}
    analytics = ""
    if cfg["GA4_ID"]:
        ids = [cfg["GA4_ID"]] + ([cfg["GADS_CONVERSION_ID"]] if cfg["GADS_CONVERSION_ID"] else [])
        cfgs = "".join(f"gtag('config','{i}');" for i in ids)
        analytics = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={cfg["GA4_ID"]}"></script>\n'
                     f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());{cfgs}</script>\n")
    head = (
        f'<title>{html.escape(title)}</title>\n'
        f'<meta name="description" content="{html.escape(desc, quote=True)}">\n'
        f'{robots}<link rel="canonical" href="{canonical}">\n'
        f'<meta property="og:type" content="{"article" if meta.get("article") else "website"}">\n'
        f'<meta property="og:site_name" content="{html.escape(cfg["BRAND"])}">\n'
        f'<meta property="og:title" content="{html.escape(meta.get("ogTitle", title), quote=True)}">\n'
        f'<meta property="og:description" content="{html.escape(desc, quote=True)}">\n'
        f'<meta property="og:url" content="{canonical}">\n'
        f'<meta property="og:image" content="{og_img}">\n'
        f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<link rel="preload" href="/assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
        f'{preload}'
        f'<style>{css_inline}</style>\n'
        f'<script>document.documentElement.classList.add("js");window.SITE={json.dumps(site_js)}</script>\n'
        f'{analytics}'
        f'<script type="application/ld+json">{ld}</script>'
    )
    page = page.replace("{{head}}", head).replace("{{content}}", body)
    page = page.replace("{{bodyclass}}", meta.get("bodyClass", ""))
    page = tokens(page)
    return page, meta


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    # static assets
    shutil.copytree(os.path.join(SRC, "static"), OUT)
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith((".php", ".js", ".txt", ".css", ".htaccess", ".svg", ".xml", ".html")) or f == ".htaccess":
                p = os.path.join(root, f)
                if f.endswith(".svg") and "icons" in f:
                    continue
                s = read(p); t = tokens(s)
                if t != s:
                    open(p, "w", encoding="utf-8").write(t)
    css_inline = tokens(minify_css(read(os.path.join(SRC, "static", "assets", "css", "main.css"))))
    pages = []
    pdir = os.path.join(SRC, "pages")
    for root, _, files in os.walk(pdir):
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(root, f), pdir)
            html_out, meta = render(rel, read(os.path.join(root, f)), css_inline)
            dest = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "w", encoding="utf-8").write(html_out)
            pages.append((rel, meta, html_out))
    # sitemap
    urls = sorted([m for _, m, _ in pages if not m.get("noindex")], key=lambda m: (m["path"].count("/"), m["path"]))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for m in urls:
        sm.append(f"  <url><loc>{BASE}{m['path']}</loc><lastmod>{m.get('updated', TODAY)}</lastmod></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    # checks: internal links, leftover placeholders, h1 count
    known = {"/" + os.path.dirname(r).replace(os.sep, "/") + "/" if r.endswith("index.html") else "/" + r for r, _, _ in pages}
    known = {k.replace("//", "/") for k in known}
    bad = 0
    seen = set()
    for rel, meta, h in pages:
        for href in re.findall(r'href="(/[^"#?]*)', h):
            if href.startswith("/assets/") or href in ("/send.php", "/sitemap.xml") or href.startswith("/demos/"):
                if href.startswith("/assets/") and not os.path.exists(os.path.join(OUT, href.lstrip("/"))):
                    print(f"  ! missing asset {href} in {rel}"); bad += 1
                continue
            if href not in known and (href, rel) not in seen:
                seen.add((href, rel)); print(f"  ! broken link {href} in {rel}"); bad += 1
        for src in re.findall(r'src="(/assets/[^"]+)"', h):
            if not os.path.exists(os.path.join(OUT, src.lstrip("/"))):
                print(f"  ! missing file {src} in {rel}"); bad += 1
        n_h1 = len(re.findall(r"<h1[\s>]", h))
        if n_h1 != 1:
            print(f"  ! {n_h1} <h1> in {rel}")
        left = set(re.findall(r"\[(?:%s)\]" % "|".join(cfg.keys()), h))
        if left:
            print(f"  ! unreplaced {left} in {rel}")
    print(f"built {len(pages)} pages -> public_html/  ({bad} link problems)")
    if missing:
        print("  not set yet in config.json:", ", ".join(missing))


if __name__ == "__main__":
    main()
