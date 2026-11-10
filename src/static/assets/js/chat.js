/* [BRAND] — website chat assistant.
   Loaded on demand by main.js (first hover/focus/tap on the chat button).
   - Answers common questions instantly from the built-in list below (no AI cost).
   - If AI is switched on (config.json CHAT_AI = "on" + an API key on the server),
     questions the list can't answer go to /chat.php (Claude).
   - "Leave my details" collects name / company / phone / email / city and sends
     the lead (with the transcript) to /send.php. */
(function () {
  "use strict";
  var d = document, cfg = window.SITE || {};
  var root = d.getElementById("chatbot");
  if (!root || root.getAttribute("data-ready")) return;
  root.setAttribute("data-ready", "1");
  window.__chatReady = true;

  var panel = d.getElementById("chat-panel"), log = d.getElementById("chat-log"),
      form = d.getElementById("chat-form"), input = d.getElementById("chat-input"),
      chips = d.getElementById("chat-chips"), launcher = d.getElementById("chat-launcher");
  var transcript = [], lead = null, busy = false, started = Date.now();

  /* ---------- Built-in answers ---------- */
  var KB = [
    { k: ["catch", "free", "upfront", "risk", "love", "pay after", "pay only", "nothing", "zero", "$0", "preview"],
      a: "No catch. After a 15-minute call we design your homepage — free, within 5 days. If you love it, we build the rest and you pay when you're happy. If not, you owe nothing. <a href=\"/free-preview/\">Get your free website preview</a>." },
    { k: ["price", "cost", "how much", "pricing", "199", "499", "1499", "1,499", "fee", "expensive", "cheap"],
      a: "Websites: Starter (1–3 pages) $499 one-time; Pro (4–10 pages) $199/month with a 12-month minimum or $1,499 one-time. SEO from [PRICE_SEO_LOCAL]/month. Google Ads: $399 setup + 10% of ad spend. <a href=\"/pricing/\">See all pricing</a>." },
    { k: ["starter", "pro site", "which plan", "difference", "pages"],
      a: "Starter ($499) is 1–3 pages — great if you're new or mostly work referrals. Pro (4–10 pages, incl. up to 3 city pages) adds replacement, repair, storm and insurance pages, a projects gallery, the admin panel and a free month of SEO." },
    { k: ["own", "ownership", "domain", "who owns", "my site", "leave", "cancel"],
      a: "You do. Your domain, Google profile and ad accounts are always in your name. The site is yours on day one with a one-time plan, or after 12 months on the $199/month plan." },
    { k: ["12 month", "12-month", "minimum", "contract", "lock", "commitment", "buy out", "buyout"],
      a: "The $199/month plan has a 12-month minimum because building your site is real work up front. You can own it early anytime by paying the difference to $1,499. SEO and Google Ads have no long contract." },
    { k: ["how long", "time", "days", "fast", "quick", "when", "timeline", "launch"],
      a: "Your homepage preview arrives within 5 days of our call. Then we build the rest with 2 rounds of changes and launch on your domain once you approve and pay." },
    { k: ["seo", "rank", "google maps", "maps", "found", "search", "organic", "first page"],
      a: "SEO is the backbone of your leads: it gets you found on Google and Maps in your area. Local SEO is [PRICE_SEO_LOCAL]/month for 1 city, SEO Pro [PRICE_SEO_PRO]/month for 2–3 cities. Expect early movement in 1–3 months, strong results in 3–6. <a href=\"/roofing-seo/\">Roofing SEO</a>." },
    { w: 2, k: ["lead gen", "lead generation", "buy leads", "shared leads", "angi", "homeadvisor", "leads"],
      a: "We don't sell or share leads. We build your own lead system — a website that converts, SEO and Google Ads — with every lead tracked to its source. You pay only for the services you use. <a href=\"/roofing-lead-generation/\">Roofing lead generation</a>." },
    { w: 2, k: ["google business", "gbp", "map pack", "local seo", "reviews", "citations"],
      a: "Local SEO gets you into the Google Maps results in your towns: Google Business Profile management, a review routine, citations and real city pages. [PRICE_SEO_LOCAL]/month for 1 city, month to month. <a href=\"/local-seo-for-roofing-companies/\">Local SEO for roofers</a>." },
    { w: 3, k: ["guarantee", "promise", "results", "how many leads", "how many calls"],
      a: "No — nobody honest can guarantee #1 on Google. We guarantee the work and show you every result in plain reports." },
    { k: ["ads", "google ads", "ppc", "lsa", "local services", "advertis", "budget"],
      a: "Google Ads get you leads fast — usually in the first 1–2 weeks. $399 setup + 10% of ad spend, minimum ad budget $2,000/month paid directly to Google. Weekly reports and full access to your account. <a href=\"/roofing-google-ads/\">Google Ads for roofers</a>." },
    { k: ["admin", "edit", "change", "update", "login", "panel", "blog", "photos", "wordpress", "plugin"],
      a: "Pro Sites include an admin panel: edit your info, see every lead in one inbox and publish blog posts — from your phone. No WordPress, no plugins to update." },
    { k: ["include", "included", "what do i get", "features", "storm", "insurance", "financing", "city pages"],
      a: "Every site is custom, mobile-first and fast, with click-to-call, a quote form, on-page SEO, Search Console and Analytics. Pro adds replacement, repair, storm & hail, insurance, projects, reviews, about, service areas, up to 3 city pages, the admin panel and 1 month of SEO free." },
    { k: ["existing", "redo", "redesign", "current site", "already have", "rebuild"],
      a: "Yes. We build brand-new websites and redesign existing ones. For a redesign we keep your domain and redirect your old pages so you keep the rankings you've earned. See a before/after on <a href=\"/our-work/\">Our Work</a>." },
    { k: ["where", "located", "office", "team", "who are you", "remote", "hours", "founder"],
      a: "We're a small remote team on US hours, Mon–Fri 8am–6pm Central. You talk to the founder, [FOUNDER_NAME], from the first call to launch. We reply within 1 business day." },
    { k: ["example", "portfolio", "work", "samples", "show me", "before", "after"],
      a: "See our roofing websites — new builds and redesigns — on <a href=\"/our-work/\">Our Work</a>, including the Hardtland Home Improvement case study." },
    { k: ["not included", "logo", "photo shoot", "photographer", "extra"],
      a: "Not included: ad spend (paid to Google), professional photo shoots, and logo design (an optional add-on)." },
    { k: ["phone", "call", "talk", "human", "person", "contact", "email", "whatsapp", "number"],
      a: "Message us on <a href=\"[WHATSAPP_URL]\" target=\"_blank\" rel=\"noopener\">WhatsApp</a> or email <a href=\"mailto:[EMAIL]\">[EMAIL]</a> (Mon–Fri 8am–6pm Central). Or tap “Leave my details” and we'll reach out within 1 business day." }
  ];
  var CHIPS = ["How does $0 upfront work?", "What does it cost?", "Starter or Pro?", "Do you do Google Ads?", "Do I own the website?", "Leave my details"];

  function norm(s) { return (" " + s.toLowerCase().replace(/[^a-z0-9$,\- ]+/g, " ") + " "); }
  function match(q) {
    var t = norm(q), best = null, score = 0;
    KB.forEach(function (item) {
      var s = 0;
      item.k.forEach(function (k) { if (t.indexOf(k) !== -1) s += (k.length > 4 ? 2 : 1) * (item.w || 1); });
      if (s > score) { score = s; best = item; }
    });
    return score >= 1 ? best.a : null;
  }

  /* ---------- Rendering ---------- */
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function linkify(s) { return esc(s).replace(/(^|\s)(\/[a-z0-9\-\/]+\/)(?=[\s.,]|$)/g, '$1<a href="$2">$2</a>'); }
  function add(role, html, plain) {
    var el = d.createElement("div");
    el.className = "chat__msg chat__msg--" + role;
    el.innerHTML = html;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    transcript.push({ role: role === "bot" ? "assistant" : "user", text: plain || el.textContent });
    return el;
  }
  function typing(on) {
    var t = d.getElementById("chat-typing");
    if (on && !t) { t = d.createElement("div"); t.id = "chat-typing"; t.className = "chat__msg chat__msg--bot chat__typing"; t.innerHTML = "<i></i><i></i><i></i><span class=\"sr\">Typing…</span>"; log.appendChild(t); log.scrollTop = log.scrollHeight; }
    if (!on && t) t.remove();
  }
  function setChips(list) {
    chips.innerHTML = "";
    list.forEach(function (c) {
      var b = d.createElement("button"); b.type = "button"; b.className = "chat__chip" + (c === "Leave my details" ? " chat__chip--cta" : ""); b.textContent = c;
      b.addEventListener("click", function () { if (c === "Leave my details") startLead(); else ask(c); });
      chips.appendChild(b);
    });
  }
  function track(name, p) {
    p = p || {}; p.page_path = location.pathname;
    if (typeof window.gtag === "function") window.gtag("event", name, p);
    (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name }, p));
  }

  /* ---------- Q&A ---------- */
  function ask(q) {
    q = q.trim(); if (!q || busy) return;
    add("user", esc(q), q);
    if (lead) return leadStep(q);
    if (/leave (my )?details|call me|contact me|get started|sign me up|free preview/i.test(q)) return startLead();
    var local = match(q);
    if (cfg.chatAI === "on") {
      busy = true; typing(true);
      fetch("/chat.php", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: transcript.slice(-12) }) })
        .then(function (r) { return r.json(); })
        .then(function (res) { typing(false); busy = false; if (res.ok && res.reply) botSay(linkify(res.reply), res.reply); else fallback(local); })
        .catch(function () { typing(false); busy = false; fallback(local); });
    } else {
      typing(true);
      setTimeout(function () { typing(false); fallback(local); }, 450);
    }
  }
  function botSay(html, plain) { add("bot", html, plain); }
  function fallback(local) {
    if (local) botSay(local);
    else botSay("Good question — I don't want to guess. Leave your details and [FOUNDER_FIRST] will answer it personally within one business day, or message us on <a href=\"[WHATSAPP_URL]\" target=\"_blank\" rel=\"noopener\">WhatsApp</a>.");
    setChips(CHIPS);
  }

  /* ---------- Lead capture ---------- */
  var STEPS = [
    { key: "name", q: "Great — what's your name?", check: function (v) { return v.length >= 2 || "Just your first name is fine."; } },
    { key: "company", q: "And your roofing company's name?", check: function (v) { return v.length >= 2 || "What's the company called?"; } },
    { key: "city", q: "Which city and state do you mainly work in?", check: function (v) { return v.length >= 2 || "For example: San Antonio, TX"; } },
    { key: "phone", q: "Best phone number to reach you? (Type “skip” to use email only.)", check: function (v) { return /^skip$/i.test(v) || v.replace(/\D/g, "").length >= 10 || "Please enter a 10-digit US number, or type skip."; } },
    { key: "email", q: "And your email?", check: function (v, l) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) || (/^skip$/i.test(v) && l.phone) || "That email doesn't look right."; } }
  ];
  function startLead() {
    if (lead) return;
    lead = { step: 0, data: {} };
    track("chat_lead_start");
    botSay("I'll pass this straight to [FOUNDER_NAME]. A few quick questions — about 30 seconds.");
    setChips([]);
    setTimeout(function () { botSay(STEPS[0].q); input.focus(); }, 300);
  }
  function leadStep(v) {
    var st = STEPS[lead.step], ok = st.check(v, lead.data);
    if (ok !== true) { botSay(esc(ok)); return; }
    lead.data[st.key] = /^skip$/i.test(v) ? "" : v;
    lead.step++;
    if (lead.step < STEPS.length) { botSay(STEPS[lead.step].q); return; }
    // consent
    var el = botSay("Last thing: is it OK if we contact you by phone, text and email about your request? You can reply STOP to opt out anytime.");
    setChips([]);
    var yes = d.createElement("button"); yes.type = "button"; yes.className = "chat__chip chat__chip--cta"; yes.textContent = "Yes, contact me";
    var no = d.createElement("button"); no.type = "button"; no.className = "chat__chip"; no.textContent = "No thanks";
    yes.addEventListener("click", function () { add("user", "Yes, contact me"); chips.innerHTML = ""; submitLead(); });
    no.addEventListener("click", function () { add("user", "No thanks"); chips.innerHTML = ""; lead = null; botSay("No problem — nothing was sent. Ask me anything else."); setChips(CHIPS); });
    chips.appendChild(yes); chips.appendChild(no);
    input.disabled = true;
  }
  function submitLead() {
    var data = lead.data, fd = new FormData();
    fd.append("form", "chat"); fd.append("_ts", String(started));
    fd.append("name", data.name); fd.append("company", data.company); fd.append("city", data.city);
    fd.append("phone", data.phone || ""); fd.append("email", data.email || "");
    fd.append("consent", "yes"); fd.append("page", location.pathname);
    var at = window.__attrib || {}; Object.keys(at).forEach(function (k) { fd.append(k, at[k]); });
    fd.append("message", transcript.map(function (m) { return (m.role === "user" ? "Visitor: " : "Assistant: ") + m.text; }).join("\n"));
    typing(true);
    fetch("/send.php", { method: "POST", body: fd, headers: { "Accept": "application/json" } })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        typing(false); input.disabled = false; lead = null;
        if (!res.ok) throw new Error(res.error);
        track("generate_lead", { form: "chat" });
        if (typeof window.gtag === "function" && cfg.adsId && cfg.adsFormLabel) window.gtag("event", "conversion", { send_to: cfg.adsId + "/" + cfg.adsFormLabel });
        botSay("Done — thanks, " + esc(data.name.split(" ")[0]) + "! We'll be in touch within one business day (Mon–Fri, Central time). Want to start now? <a href=\"/free-preview/\">Get your free website preview</a> or message us on <a href=\"[WHATSAPP_URL]\" target=\"_blank\" rel=\"noopener\">WhatsApp</a>.");
        setChips(["What does it cost?", "Do I own the website?"]);
      })
      .catch(function (e) {
        typing(false); input.disabled = false; lead = null;
        botSay("Sorry, that didn't send (" + esc(String(e.message || "error")) + "). Please <a href=\"[WHATSAPP_URL]\" target=\"_blank\" rel=\"noopener\">WhatsApp us</a> or use the <a href=\"/free-preview/\">free preview form</a>.");
        setChips(CHIPS);
      });
  }

  /* ---------- Open / close ---------- */
  function open() {
    panel.hidden = false; launcher.setAttribute("aria-expanded", "true"); root.classList.add("is-open");
    if (!log.children.length) {
      botSay("Hi! I'm the [BRAND] assistant. Ask me about websites, SEO, Google Ads or pricing — or how the free website preview works.");
      setChips(CHIPS);
      track("chat_open");
    }
    setTimeout(function () { input.focus(); }, 50);
  }
  function close() { panel.hidden = true; launcher.setAttribute("aria-expanded", "false"); root.classList.remove("is-open"); launcher.focus(); }
  launcher.addEventListener("click", function () { panel.hidden ? open() : close(); });
  d.getElementById("chat-close").addEventListener("click", close);
  d.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) close(); });
  form.addEventListener("submit", function (e) { e.preventDefault(); var v = input.value; input.value = ""; ask(v); });

  if (root.getAttribute("data-open-on-load") === "true") open();
})();
