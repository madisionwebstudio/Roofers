#!/usr/bin/env python3
"""Generate the city landing pages (src/pages/locations/<slug>/) and the /locations/ hub
from tools/cities_data.py. Run: python3 tools/cities.py && python3 tools/build.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from cities_data import CITIES

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'pages', 'locations')
CHECK = '<svg aria-hidden="true"><use href="/assets/img/icons.svg#i-check"/></svg>'
ARROW = '<svg aria-hidden="true"><use href="/assets/img/icons.svg#i-arrow"/></svg>'


def li(b, s):
    return f'<li>{CHECK}<div><b>{b}</b><span>{s}</span></div></li>'


def faq(q, a):
    return f'<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>'


def page(c):
    C, ST, S = c['city'], c['st'], c['state']
    cs = f'{C}, {ST}'
    slug = c['slug']
    title = f'Roofing Marketing Agency {cs} | Web Design & SEO'
    assert len(title) <= 60, title
    desc = f'Roofing marketing agency for {cs} roofers: website design, roofing SEO, Google Ads and lead generation. Free website preview in 5 days, $0 upfront.'
    meta = {
        "title": title, "description": desc, "path": f"/locations/{slug}/",
        "crumbs": [["Home", "/"], ["Locations", "/locations/"], [cs, f"/locations/{slug}/"]],
        "preload": c['img'],
        "service": {"name": f"Roofing marketing agency in {cs}", "type": "Marketing for roofing contractors: web design, SEO, Google Ads",
                    "area": {"@type": "City", "name": C, "containedInPlace": {"@type": "State", "name": S}},
                    "offers": [["Starter website", "499"], ["Pro website, monthly", "199", "MONTH"], ["Local SEO", "[PRICE_SEO_LOCAL]", "MONTH"]]},
    }
    market = ''.join(f'<p>{p}</p>' for p in c['market'])
    chall = ''.join(li(b, s) for b, s in c['challenges'])
    subs = ''.join(f'<li>{s}</li>' for s in c['suburbs'])
    others = ' · '.join(f'<a class="tlink" href="/locations/{o["slug"]}/">{o["city"]}</a>' for o in CITIES if o['slug'] != slug)
    tzline = ('the same time zone as you' if c['tz'] == 'Central' else f'and we\'ll schedule calls around {c["tz"]} time')
    faqs = ''.join(faq(q, a) for q, a in c['faqs']) + ''.join([
        faq(f'Do you have an office in {C}?', f'No. We\'re a small remote team working US hours, Monday to Friday 8am–6pm Central, and we won\'t pretend otherwise. We work with {C} roofers by phone, video, WhatsApp and email, and you send photos of your jobs from your phone.'),
        faq(f'How much does roofing marketing cost in {C}?', f'Our prices are the same everywhere: websites from $499 (Pro $199/month or $1,499), Local SEO [PRICE_SEO_LOCAL]/month, and Google Ads management at $399 setup + 10% of ad spend. What changes in {C} is the ad budget — local cost per click decides how far a budget goes, and we check it for you before you spend anything.'),
        faq(f'Do you work with other roofers in {C}?', 'We may. If we do, we\'ll tell you on the first call, and we never share one client\'s data, keywords or plans with another. If exclusivity in your area matters to you, ask — we\'ll discuss it openly.'),
    ])
    return f'''<!--meta {json.dumps(meta, ensure_ascii=False, indent=2)} -->

<section class="hero hero--page hero--form" aria-labelledby="h1">
  <div class="hero__media">{{{{img name="{c['img']}" alt="{c['img_alt']}" sizes="100vw" eager}}}}</div>
  <div class="wrap hero__in">
    <div class="stack" style="--s:1.3rem">
      {{{{crumbs}}}}
      <h1 id="h1" class="d-hero"><span class="h1-kw">Roofing marketing agency in {cs}</span> More roofing jobs <span class="hl">in {C}.</span></h1>
      <p class="lede">[BRAND] is a roofing marketing agency for {C} roofing contractors: roofing website design, roofing SEO, Google Ads and lead generation — planned around how homeowners in {C} and its suburbs search for a roofer.</p>
      <p class="hero__micro"><span>Roofers only</span><span>Remote team, US hours</span><span>Prices on the site</span></p>
    </div>
    {{{{qform service="web-design" cta="Get my free website preview" title="Free website preview for {C} roofers" sub="See your new homepage in 5 days. $0 upfront — pay only if you love it."}}}}
  </div>
</section>

<section class="sec sec--paper" aria-labelledby="mkt-h">
  <div class="wrap grid g-4-8">
    <div class="stack"><p class="eyebrow">The {C} roofing market</p><h2 id="mkt-h" class="d-l reveal">{c['head']}</h2></div>
    <div class="prose">{market}</div>
  </div>
</section>

<section class="sec sec--white" aria-labelledby="ch-h">
  <div class="wrap grid g-2">
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">Roofing contractor marketing in {C}</p>
      <h2 id="ch-h" class="d-l reveal">What makes it hard <span class="hl">in {C}.</span></h2>
      <p class="measure muted">Every market has its own problems. These are the ones we'd plan around for a {C} roofing company.</p>
    </div>
    <ul class="checks" role="list">{chall}</ul>
  </div>
</section>

<section class="sec sec--navy" aria-labelledby="svc-h">
  <div class="wrap">
    <div class="head head--split">
      <div class="stack"><p class="eyebrow">Roofing marketing services in {C}</p><h2 id="svc-h" class="d-xl reveal">Four ways we bring <span class="hl">{C} homeowners to you.</span></h2></div>
      <p class="lede muted">Use one, or all four. Every account, domain and lead stays in your name.</p>
    </div>
    <div class="grid g-2" style="row-gap:40px">
      <div class="feature"><svg class="ico" aria-hidden="true"><use href="/assets/img/icons.svg#i-browser"/></svg><h3 class="h3">Roofing web design in {C}</h3><p>A fast, mobile-first website that shows {C} homeowners you're local and established: your projects, reviews, license and insurance, and one clear next step. <a class="tlink" href="/roofing-website-design/">Roofing website design</a></p></div>
      <div class="feature"><svg class="ico" aria-hidden="true"><use href="/assets/img/icons.svg#i-search"/></svg><h3 class="h3">Roofing SEO in {C}</h3><p>Service pages, real suburb pages, citations and technical fixes, so you show up when homeowners search for a roofer in your towns. <a class="tlink" href="/roofing-seo/">Roofing SEO services</a></p></div>
      <div class="feature"><svg class="ico" aria-hidden="true"><use href="/assets/img/icons.svg#i-target"/></svg><h3 class="h3">Google Ads for {C} roofers</h3><p>Replacement, repair and storm campaigns limited to the parts of the {C} area you serve, with weekly reports. <a class="tlink" href="/roofing-google-ads/">Roofing PPC management</a></p></div>
      <div class="feature"><svg class="ico" aria-hidden="true"><use href="/assets/img/icons.svg#i-inbox"/></svg><h3 class="h3">Roofing lead generation in {C}</h3><p>Leads that come to you, not shared with other roofers — every call, message and form tracked to its source. <a class="tlink" href="/roofing-lead-generation/">Roofing lead generation</a></p></div>
    </div>
  </div>
</section>

<section class="sec sec--paper" aria-labelledby="seo-h">
  <div class="wrap grid g-2">
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">Local SEO strategy</p>
      <h2 id="seo-h" class="d-l reveal">Getting found in <span class="hl">{C} Google Maps.</span></h2>
      <p class="measure">{c['seo']}</p>
      <p class="measure muted">Google ranks local results mainly on relevance, distance and prominence, so we never fake addresses or build copy-paste suburb pages. More on <a class="tlink" href="/local-seo-for-roofing-companies/">local SEO for roofing companies</a>.</p>
      <p class="small muted"><b>Towns around {C} we'd consider</b> — only where you really work:</p>
      <ul class="tags" role="list">{subs}</ul>
    </div>
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">Google Ads strategy</p>
      <h2 class="d-l reveal">Ads for <span class="hl">{C} roofers.</span></h2>
      <p class="measure">{c['ppc']}</p>
      <p class="measure muted">Management is $399 setup + 10% of ad spend, with a $2,000/month minimum budget paid directly to Google. See <a class="tlink" href="/blog/google-ads-for-roofers/">Google Ads for roofing companies</a>.</p>
    </div>
  </div>
</section>

<section class="sec sec--white" aria-labelledby="chk-h">
  <div class="wrap grid g-2 ai-c">
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">Free, on the first call</p>
      <h2 id="chk-h" class="d-l reveal">What we check for your <span class="hl">{C} company.</span></h2>
      <p class="measure muted">Real numbers for your area, checked live — not guesses from a template.</p>
      <ul class="checks" role="list">
        {li(f'Who holds the {C} Maps top 3', f'For “roofer {C}” and your main suburb, and how their reviews compare with yours.')}
        {li('Your local cost per click', f'Google Keyword Planner ranges for roof replacement and repair searches in {C}.')}
        {li('Where you show up today', 'Your Maps position across your service area, and which searches already find your website.')}
        {li('Your website on a phone', 'Speed, first screen, contact form and proof — the things that turn visits into calls.')}
      </ul>
    </div>
    <div class="stack" style="--s:1rem">
      <div class="founder__photo" style="aspect-ratio:4/3">{{{{img name="tear-off" alt="Roofer removing old shingles during a tear-off" sizes="(min-width:900px) 45vw, 100vw"}}}}</div>
      <p class="small muted">Want an example of our work? See the <a class="tlink" href="/our-work/hardtland-home-improvement/">Hardtland Home Improvement case study</a> — a roofing website we rebuilt for a client in Madison, WI.</p>
    </div>
  </div>
</section>

<section class="sec sec--paper" aria-labelledby="how-h">
  <div class="wrap grid g-2 ai-c">
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">How we work with {C} roofers</p>
      <h2 id="how-h" class="d-l reveal">Remote team. <span class="hl">Local-looking results.</span></h2>
      <p class="measure">We don't have a {C} office, and we won't pretend to. We work Monday to Friday, 8am–6pm Central, {tzline}. You send photos of your jobs from your phone; we turn them into a site and Google profile that look unmistakably local.</p>
    </div>
    <ul class="checks" role="list">
      {li('Free homepage preview in 5 days', '$0 upfront. Don\'t love it? Pay nothing.')}
      {li('Websites from $499', 'Pro Site $199/month or $1,499 one-time — only after you approve the finished site.')}
      {li('SEO and Google Ads, month to month', 'Local SEO [PRICE_SEO_LOCAL]/month · Ads $399 setup + 10% of ad spend.')}
      {li('You own everything', 'Domain, Google Business Profile and ad accounts stay in your name.')}
    </ul>
  </div>
</section>

<section class="sec sec--white" aria-labelledby="faq-h">
  <div class="wrap grid g-4-8">
    <div class="stack"><p class="eyebrow">{C} FAQ</p><h2 id="faq-h" class="d-l reveal">Questions from {C} roofers.</h2><p class="muted small">Other cities: {others} · <a class="tlink" href="/locations/">all locations</a></p></div>
    <div class="faq">{faqs}</div>
  </div>
</section>

<!--@include cta-final-->
'''


def hub():
    by_state = {}
    for c in CITIES:
        by_state.setdefault(c['state'], []).append(c)
    cards = ''.join(
        f'<a class="loc-card" href="/locations/{c["slug"]}/" data-cta="loc-{c["slug"]}"><b>{c["city"]}, {c["st"]}</b><span>Roofing marketing agency in {c["city"]}</span></a>'
        for c in CITIES)
    meta = {"title": "Roofing Marketing Agency Locations | 16 US Cities",
            "description": "Roofing marketing for roofing contractors in 16 US cities — Dallas, Houston, Phoenix, Austin, Atlanta, Chicago and more. Web design, SEO and Google Ads.",
            "path": "/locations/", "crumbs": [["Home", "/"], ["Locations", "/locations/"]], "preload": "aerial-culdesac"}
    states = ', '.join(sorted(by_state))
    return f'''<!--meta {json.dumps(meta, ensure_ascii=False, indent=2)} -->

<section class="hero hero--page" aria-labelledby="h1">
  <div class="hero__media">{{{{img name="aerial-culdesac" alt="Aerial view of a suburban cul-de-sac" sizes="100vw" eager}}}}</div>
  <div class="wrap hero__in stack" style="--s:1.4rem">
    {{{{crumbs}}}}
    <h1 id="h1" class="d-hero"><span class="h1-kw">Roofing marketing agency locations</span> Roofing marketing, <span class="hl">city by city.</span></h1>
    <p class="lede">We work with roofing contractors anywhere in the US. These 16 city pages explain how we'd market a roofing company in each market — the weather, the competition, the suburbs and the searches that matter.</p>
    <div class="btn-row"><a class="btn btn--lg" href="/free-preview/" data-cta="loc-hero-preview">Get my free website preview {ARROW}</a></div>
  </div>
</section>

<section class="sec sec--paper" aria-labelledby="cities-h">
  <div class="wrap">
    <div class="head head--split">
      <div class="stack"><p class="eyebrow">16 cities</p><h2 id="cities-h" class="d-xl reveal">Pick your <span class="hl">market.</span></h2></div>
      <p class="lede muted">Cities in {states}. Not on the list? We work with roofers everywhere — the plan just starts with your own market.</p>
    </div>
    <div class="loc-grid">{cards}</div>
  </div>
</section>

<section class="sec sec--white" aria-labelledby="why-h">
  <div class="wrap grid g-2">
    <div class="stack" style="--s:1.2rem">
      <p class="eyebrow">Why these cities</p>
      <h2 id="why-h" class="d-l reveal">Big roofing markets, <span class="hl">very different needs.</span></h2>
      <p class="measure">We picked these markets for their roofing demand, growth and competition, using public market research such as <a class="tlink" href="https://www.groundworkdemographics.com/markets/roofing" target="_blank" rel="noopener">Groundwork Demographics</a> and <a class="tlink" href="https://nextterritory.com/markets" target="_blank" rel="noopener">NextTerritory</a>. A hail-driven market like Dallas needs a different plan from a rain-driven one like Seattle.</p>
      <p class="measure muted">We don't have offices in these cities and don't claim clients there unless it's true. We're a remote team on US hours.</p>
    </div>
    <ul class="checks" role="list">
      {li('Hail markets', 'Dallas, Austin, San Antonio, Kansas City, Minneapolis, Indianapolis — storm campaigns ready to launch.')}
      {li('Hurricane markets', 'Houston, Orlando, Tampa — insurance and inspection pages up front.')}
      {li('Desert markets', 'Phoenix, Las Vegas — tile, underlayment and flat-roof pages.')}
      {li('Four-season and rain markets', 'Chicago, Seattle, Atlanta, Charlotte, Nashville — leak, ice and storm work all year.')}
    </ul>
  </div>
</section>

<!--@include cta-final-->
'''


if __name__ == '__main__':
    for c in CITIES:
        d = os.path.join(ROOT, c['slug'])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w').write(page(c))
    open(os.path.join(ROOT, 'index.html'), 'w').write(hub())
    print(f'wrote {len(CITIES)} city pages + hub')
