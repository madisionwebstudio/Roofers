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
UNSET = lambda v: (not str(v).strip()) or str(v).strip().startswith("[")
missing = [k for k, v in cfg.items() if UNSET(v) and k not in ("CHAT_AI", "FOUNDER_VIDEO")]
digits = re.sub(r"\D", "", cfg["US_PHONE"])
cfg["US_PHONE_E164"] = "+1" + digits[-10:] if len(digits) >= 10 else ""
cfg["YEAR"] = str(date.today().year)
_wa = re.sub(r"\D", "", cfg.get("WHATSAPP", ""))
cfg["WHATSAPP_URL"] = ("https://wa.me/" + _wa + "?text=" + "Hi%20" + cfg["FOUNDER_NAME"].split()[0] + "%2C%20I%27m%20a%20roofer%20and%20I%27d%20like%20a%20free%20website%20preview.") if _wa else "https://wa.me/[WHATSAPP]"
BASE = "https://" + cfg["DOMAIN"].strip().rstrip("/")
LAUNCH_ON = cfg.get("LAUNCH_PRICING", "on").lower() == "on"
FONT = cfg.get("DISPLAY_FONT", "jakarta").lower() if cfg.get("DISPLAY_FONT", "jakarta").lower() in ("anton", "archivo", "jakarta") else "jakarta"
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
    jw = info.get("jpg")
    if jw:  # <picture>: WebP for modern browsers, one JPG for older Safari (iOS 13 and below)
        return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
                f'<img src="/assets/img/{name}-{jw}.jpg" width="{w}" height="{h}" alt="{alt}"{cls}{load}></picture>')
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


def launch_tag(m):
    """{{launch after="$699"}} -> launch-price line, or nothing when LAUNCH_PRICING is off."""
    if not LAUNCH_ON:
        return ""
    a = dict(ATTR.findall(m.group(1)))
    txt = cfg.get("LAUNCH_LINE", "Launch price — goes to {after} after our first 10 roofing clients.").replace("{after}", a.get("after", ""))
    return f'<span class="launch">{html.escape(txt)}</span>'


WORK = json.load(open(os.path.join(SRC, "static", "assets", "data", "work.json")))


def work_tag(m):
    """{{work}} or {{work limit="1"}} -> before/after redesign cards from assets/data/work.json."""
    a = dict(ATTR.findall(m.group(1) or ""))
    items = WORK["roofing"]
    real = [w for w in items if w.get("name")]
    slots = [w for w in items if not w.get("name")]
    if a.get("limit"):
        real = real[: int(a["limit"])]
        slots = []
    out = []
    for i, w in enumerate(real):
        loc = f'{w["city"]}, {w["state"]}'
        badge = ("Client" + (" · " + w["status_note"] if w.get("status_note") else "")) if w.get("status") == "client" else "Redesign concept — not a client"
        bcls = "badge badge--client" if w.get("status") == "client" else "badge badge--concept"
        before = img_tag(re.match(r"(.*)", f'name="{w["before_img"]}" alt="Before: {w["name"]} current website homepage" sizes="(min-width:1000px) 760px, 92vw"'))
        after = img_tag(re.match(r"(.*)", f'name="{w["after_img"]}" alt="After: our redesign of the {w["name"]} homepage" sizes="(min-width:1000px) 760px, 92vw"'))
        mob = img_tag(re.match(r"(.*)", f'name="{w["mobile_img"]}" alt="Our {w["name"]} redesign on a phone" sizes="200px"'))
        imps = "".join(f"<li><svg aria-hidden=\"true\"><use href=\"/assets/img/icons.svg#i-check\"/></svg><span>{html.escape(x)}</span></li>" for x in w["improvements"])
        out.append(f'''<article class="wcard" aria-labelledby="w-{i}">
  <div class="wcard__media">
    <div class="ba" data-ba style="--pos:50%">
      <div class="ba__img ba__img--after">{after}</div>
      <div class="ba__img ba__img--before">{before}</div>
      <span class="ba__tag ba__tag--before" aria-hidden="true">Before</span><span class="ba__tag ba__tag--after" aria-hidden="true">After</span>
      <span class="ba__handle" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M9 6l-6 6 6 6M15 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4"/></svg></span>
      <input class="ba__range" type="range" min="0" max="100" value="50" aria-label="Drag to compare the old and new {html.escape(w["name"])} website">
    </div>
    <div class="wcard__phone" aria-hidden="false">{mob}</div>
  </div>
  <div class="wcard__body">
    <p class="wcard__badges"><span class="{bcls}">{badge}</span><span class="badge">{html.escape(loc)}</span></p>
    <h3 id="w-{i}" class="h3">{html.escape(w["name"])}</h3>
    <p class="muted">{html.escape(w.get("description", ""))}</p>
    <ul class="wcard__imps" role="list">{imps}</ul>
    <p class="small muted">{html.escape(w.get("note", ""))}</p>
    <p class="btn-row">{('<a class="btn btn--dark" href="' + w["case_study"] + '" data-cta="work-case-' + str(i) + '">Read the case study <svg aria-hidden="true"><use href="/assets/img/icons.svg#i-arrow"/></svg></a>') if w.get("case_study") else ""}
    <a class="arrow-link" href="{w["live_url"]}" target="_blank" rel="noopener" data-cta="work-live-{i}">See the new site <svg aria-hidden="true"><use href="/assets/img/icons.svg#i-arrow"/></svg></a></p>
  </div>
</article>''')
    slot_html = []
    for i, w in enumerate(slots):
        slot_html.append('''<article class="wcard wcard--slot"><div class="wcard__body"><p class="wcard__badges"><span class="badge">Open slot</span></p>
  <h3 class="h3">Your roofing company here</h3><p class="muted">We'll redesign your homepage free and show it here next to your current site — only with your OK.</p>
  <a class="btn" href="/free-preview/" data-cta="work-slot">Get my free website preview <svg aria-hidden="true"><use href="/assets/img/icons.svg#i-arrow"/></svg></a></div></article>''')
    if slot_html:
        out.append('<div class="work-slots">' + "\n".join(slot_html) + "</div>")
    return "\n".join(out)


def qform_tag(m):
    """{{qform service="seo" cta="Get my free website preview" title="..."}} -> short lead form for service-page heroes."""
    a = dict(ATTR.findall(m.group(1)))
    svc = a.get("service", "web-design")
    cta = a.get("cta", "Get my free website preview")
    title = a.get("title", "Get your free website preview")
    sub = a.get("sub", "Free homepage preview in 5 days. No card. No obligation.")
    p = "q-" + svc
    def field(name, label, typ, auto, req=True, opt=False, extra=""):
        r = f' required aria-describedby="{p}-{name}-e"' if req else ""
        o = ' <span class="opt">(optional)</span>' if opt else ""
        e = f'<p class="err" id="{p}-{name}-e"></p>' if req else ""
        return (f'<div class="field"><label for="{p}-{name}">{label}{o}</label><input id="{p}-{name}" type="{typ}" name="{name}" autocomplete="{auto}"{r}{extra}>{e}</div>')
    return (f'''<div class="qform" id="get-started"><h2>{html.escape(title)}</h2><p class="sub">{html.escape(sub)}</p>
<form class="form" action="/send.php" method="post" data-form="{svc}" novalidate>
<input type="hidden" name="form" value="free-preview"><input type="hidden" name="service" value="{svc}"><input type="hidden" name="_ts" value="">
<div class="hp" aria-hidden="true"><label for="{p}-fax">Leave this empty</label><input id="{p}-fax" type="text" name="fax_number" tabindex="-1" autocomplete="off"></div>
<div class="row row-2">{field("name", "Your name", "text", "name", extra=' data-msg="Please tell us your name."')}{field("company", "Company", "text", "organization", extra=' data-msg="What is your company called?"')}</div>
<div class="row row-2">{field("phone", "Phone", "tel", "tel", extra=' inputmode="tel"')}{field("email", "Email", "email", "email")}</div>
<div class="row row-2">{field("city", "City, state", "text", "address-level2", extra=' placeholder="Madison, WI" data-msg="Which city and state?"')}{field("website", "Current website", "url", "url", req=False, opt=True, extra=' inputmode="url" placeholder="yourroofing.com"')}</div>
<label class="consent field"><input type="checkbox" name="consent" value="yes" required data-msg="Please tick the box so we can contact you."><span>I agree to be contacted by phone, text and email about my request. Reply STOP to opt out. <span class="err"></span></span></label>
<p class="form-status" role="alert" tabindex="-1"></p>
<button class="btn btn--lg btn--block" type="submit" data-cta="form-{svc}">{html.escape(cta)} <svg aria-hidden="true"><use href="/assets/img/icons.svg#i-arrow"/></svg></button>
<p class="form-note">$0 upfront. We reply within 1 business day.</p>
</form></div>''')


def founder_video_tag(_m):
    v = cfg.get("FOUNDER_VIDEO", "").strip()
    if not v or UNSET(v):
        return ('<div class="video-ph" role="img" aria-label="Founder intro video coming soon"><svg viewBox="0 0 24 24" aria-hidden="true">'
                '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 8.5l6 3.5-6 3.5z" fill="currentColor"/></svg>'
                '60-second intro video from [FOUNDER_NAME] — coming soon</div>')
    if v.endswith(".mp4"):
        return f'<video controls preload="none" src="{html.escape(v)}"></video>'
    return f'<iframe src="{html.escape(v)}" title="60-second intro from [FOUNDER_NAME]" loading="lazy" allow="fullscreen; picture-in-picture"></iframe>'


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
       "logo": BASE + "/assets/img/logo.png", "email": cfg["EMAIL"],
       "founder": {"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"]},
       "areaServed": {"@type": "Country", "name": "United States"},
       "slogan": "A perfect website gets you more roofing leads.",
       "description": f"{cfg['BRAND']} is a roofing marketing agency for US roofing contractors: roofing website design, roofing SEO, Google Ads / PPC and roofing lead generation.",
       "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": cfg["EMAIL"], "url": cfg["WHATSAPP_URL"],
                        "areaServed": "US", "availableLanguage": "English",
                        "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "18:00"}},
       "knowsAbout": ["Roofing marketing", "Roofing web design", "Roofing SEO", "Local SEO for roofing companies", "Roofing PPC management", "Roofing lead generation"]}
SAME_AS = [u.strip() for u in cfg.get("SAME_AS", "").split(",") if u.strip()]
if SAME_AS:
    ORG["sameAs"] = SAME_AS

NAV = [("Web Design", "/roofing-website-design/"), ("SEO", "/roofing-seo/"), ("Google Ads", "/roofing-google-ads/"),
       ("Lead Gen", "/roofing-lead-generation/"), ("Pricing", "/pricing/"), ("Our Work", "/our-work/"), ("Blog", "/blog/"), ("About", "/about/")]


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
    if len(title) > 60:
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
    body = re.sub(r"\[(SOURCE NEEDED[^\]]*|DATA:[^\]]*|ADD:[^\]]*|IMAGE[^\]]*|REVIEW TEXT[^\]]*|Reviewer name[^\]]*|VIDEO_\d[^\]]*|CONFIRM[^\]]*)\]", lambda m: f'<span class="src-needed">[{m.group(1)}]</span>', body)
    body = re.sub(r"\{\{device\s+(.*?)\}\}", device_tag, body, flags=re.S)
    body = re.sub(r"\{\{launch\s+(.*?)\}\}", launch_tag, body, flags=re.S)
    body = re.sub(r"\{\{qform\s+(.*?)\}\}", qform_tag, body, flags=re.S)
    body = body.replace("{{founder_video}}", founder_video_tag(None))
    body = re.sub(r"\{\{work(\s+.*?)?\}\}", work_tag, body, flags=re.S)
    body = re.sub(r"\{\{img\s+(.*?)\}\}", img_tag, body, flags=re.S)

    page = read(os.path.join(SRC, "partials", "_layout.html"))
    page = include(page)
    nav_html = "".join(
        f'<a href="{u}" data-cta="nav-{n.lower().replace(" ", "-")}"' + (' aria-current="page"' if url_path.startswith(u) else "") + f">{n}</a>"
        for n, u in NAV)
    page = page.replace("{{nav}}", nav_html)
    page = page.replace("{{mnav}}", "".join(f'<a class="mnav__l" href="{u}"' + (' aria-current="page"' if url_path.startswith(u) else "") + f">{n}</a>" for n, u in NAV))
    page = page.replace('class="no-js"', f'class="no-js f-{FONT}"', 1)

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
                "areaServed": s.get("area", {"@type": "Country", "name": "United States"}), "url": canonical, "description": desc,
                "audience": {"@type": "BusinessAudience", "audienceType": "Roofing contractors"}}
        if s.get("offers"):
            num = lambda v: re.sub(r"[^\d.]", "", str(v)) or "0"
            node["offers"] = [{"@type": "Offer", "name": o[0], "price": num(o[1]), "priceCurrency": "USD",
                               **({"priceSpecification": {"@type": "UnitPriceSpecification", "price": num(o[1]), "priceCurrency": "USD", "unitText": o[2]}} if len(o) > 2 else {})}
                              for o in s["offers"]]
        graph.append(node)
    if meta.get("article"):
        a = meta["article"]
        graph.append({"@type": "Article", "headline": title.split(" | ")[0], "description": desc, "url": canonical,
                      "image": BASE + f"/assets/img/{a['image']}-1200.webp", "datePublished": a["date"], "dateModified": a.get("modified", a["date"]),
                      "author": {"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"], "url": BASE + "/about/"},
                      "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": canonical})
    if url_path in ("/about/", "/"):
        person = {"@type": "Person", "@id": BASE + "/about/#founder", "name": cfg["FOUNDER_NAME"], "jobTitle": "Founder",
                  "worksFor": {"@id": BASE + "/#org"}, "url": BASE + "/about/"}
        person["sameAs"] = [u for u in (cfg.get("LINKEDIN_URL"), cfg.get("FIVERR_URL")) if u and not UNSET(u)]
        graph.append(person)
    fq = faq_schema(body)
    if fq:
        graph.append(fq)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

    og_img = BASE + "/assets/img/" + (meta.get("og") or "og-default.jpg")
    robots = '<meta name="robots" content="noindex, follow">\n' if meta.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large">\n'
    preload = preload_tag(meta["preload"], meta.get("preloadSizes", "100vw")) if meta.get("preload") else ""
    site_js = {"calendly": cfg["CALENDLY_URL"], "adsId": cfg["GADS_CONVERSION_ID"],
               "adsFormLabel": cfg["GADS_FORM_LABEL"], "adsCallLabel": cfg["GADS_CALL_LABEL"],
               "chatAI": "on" if cfg.get("CHAT_AI", "").lower() == "on" else "off"}
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
        f'<meta name="twitter:title" content="{html.escape(meta.get("ogTitle", title), quote=True)}">\n'
        f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">\n'
        f'<meta property="og:image:alt" content="{html.escape(cfg["BRAND"])} — roofing websites, SEO and Google Ads">\n'
        + {"anton": '<link rel="preload" href="/assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n<link rel="preload" href="/assets/fonts/barlow-condensed-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>\n',
           "archivo": '<link rel="preload" href="/assets/fonts/archivo-cond-600-900.woff2" as="font" type="font/woff2" crossorigin>\n',
           "jakarta": '<link rel="preload" href="/assets/fonts/plus-jakarta-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'}[FONT] +
        f'{preload}'
        f'<style>{css_inline}</style>\n'
        f'<script>document.documentElement.classList.add("js");window.SITE={json.dumps(site_js)}</script>\n'
        f'{analytics}'
        f'<script type="application/ld+json">{ld}</script>'
    )
    page = page.replace("{{head}}", head).replace("{{content}}", body)
    page = page.replace("{{bodyclass}}", meta.get("bodyClass", ""))
    page = tokens(page)
    # older Safari has no :has() — mark buttons that carry an arrow icon with a class instead
    page = re.sub(r'(<(?:a|button) class="btn)([^"]*)("[^>]*>)(?=(?:(?!</(?:a|button)>).)*?<svg)', r'\1\2 btn--arrow\3', page, flags=re.S)
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
            if href.startswith("/assets/") or href in ("/send.php", "/sitemap.xml") or href.startswith("/assets/data/"):
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
        left = set(re.findall(r"\[(?:%s)\]" % "|".join(k for k, v in cfg.items() if not UNSET(v)), h))
        if left:
            print(f"  ! unreplaced {left} in {rel}")
    print(f"built {len(pages)} pages -> public_html/  ({bad} link problems)")
    if missing:
        print("  not set yet in config.json:", ", ".join(missing))


if __name__ == "__main__":
    main()
