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
    { k: ["catch", "free", "upfront", "risk", "love", "pay after", "pay only", "nothing", "zero", "$0"],
      a: "No catch — the risk is on us. After a 15-minute call we send you a free growth plan and a designed homepage within 5 days. If you love it, we build the full site and you pay only when you're happy. If not, you owe nothing. <a href=\"/free-preview/\">Get your free growth plan</a>." },
    { k: ["price", "cost", "how much", "pricing", "199", "1499", "1,499", "fee", "expensive", "cheap"],
      a: "Websites are $199/month (12-month minimum, you own it after) or $1,499 one-time. Local SEO is $597/month, SEO Pro $997/month. Google Ads management is $597/month ($797 with Local Services Ads) plus a $300 setup. <a href=\"/pricing/\">See all pricing</a>." },
    { k: ["own", "ownership", "domain", "who owns", "my site", "leave", "cancel"],
      a: "You do. Your domain, Google Business Profile and ad accounts are always in your name. The website is yours from day one on the $1,499 plan, or after 12 months on the $199/month plan." },
    { k: ["12 month", "12-month", "minimum", "contract", "lock", "commitment"],
      a: "The $199/month plan has a 12-month minimum because it replaces a big upfront build fee — hosting, security, backups and monthly edits are included, and the site is yours after 12 months. Prefer no commitment? Take the $1,499 one-time option. SEO and Ads plans are month to month." },
    { k: ["how long", "time", "days", "fast", "quick", "when", "timeline", "launch"],
      a: "Your growth plan and homepage preview arrive within 5 days of our call. The full site follows with up to 2 rounds of changes, then we launch on your domain once you approve it." },
    { k: ["seo", "rank", "google maps", "map", "found", "search", "organic", "first page"],
      a: "Our roofing SEO puts you in Google Maps and search for the towns you want more jobs in: Business Profile management, new pages every month, citations and a monthly calls report. Most roofers see momentum in 3–6 months. We never guarantee rankings — Google decides. <a href=\"/roofing-seo/\">Roofing SEO</a>." },
    { w: 3, k: ["guarantee", "promise", "results", "how many leads", "how many calls"],
      a: "We don't guarantee rankings or a number of leads — nobody honest can, because Google and your market decide those. We guarantee the work, listed upfront, and clear monthly reporting on calls and leads by source." },
    { k: ["ads", "google ads", "lsa", "local services", "ppc", "advertis", "guaranteed", "screened"],
      a: "Google Ads and Local Services Ads get you calls within weeks. Management is $597/month, or $797 with LSA, plus a $300 setup. We recommend $1,500+/month in ad spend, paid straight to Google from your own account — no markup. <a href=\"/roofing-google-ads/\">Google Ads for roofers</a>." },
    { k: ["admin", "edit", "change", "update", "login", "panel", "blog", "photos", "wordpress", "plugin"],
      a: "Every site comes with an admin panel: update your phone, hours, services and photos, see every lead in one inbox and publish blog posts — from your phone. It's not WordPress, so there are no plugins to update. <a href=\"/admin-panel/\">See the admin panel</a>." },
    { k: ["pages", "include", "included", "what do i get", "features", "storm", "insurance", "financing"],
      a: "Every site has 8–10 pages — home, roof replacement, repair, storm & hail damage, insurance claims help, about, projects, reviews, contact and service areas — plus click-to-call, a quote form, financing section, on-page SEO, Search Console + Analytics and a free month of SEO." },
    { k: ["existing", "redo", "redesign", "current site", "already have", "rebuild", "move"],
      a: "Yes — most projects are redesigns. We keep your domain, carry over what's worth keeping and redirect your old pages so you don't lose rankings you've already earned." },
    { k: ["where", "located", "office", "team", "who are you", "remote", "hours", "founder"],
      a: "We're a small remote team working US hours, Mon–Fri 8am–6pm Central. Our founder, [FOUNDER_NAME], runs every project personally. Call [US_PHONE] or email [EMAIL]." },
    { k: ["example", "portfolio", "work", "samples", "demo", "show me"],
      a: "You can see our roofing designs in desktop and phone views on <a href=\"/our-work/\">Our Work</a>. They're demo builds for fictional companies, clearly labeled — we don't pass off made-up clients as real." },
    { k: ["not included", "logo", "photo shoot", "photographer", "extra"],
      a: "Not included: ad spend (paid to Google), professional photo shoots, and logo design (an optional add-on). We'll tell you exactly which job photos to take on your phone." },
    { k: ["phone", "call", "talk", "human", "person", "contact", "email"],
      a: "Happy to talk: call [US_PHONE] (Mon–Fri 8am–6pm Central) or email [EMAIL]. Or tap “Leave my details” and we'll reach out within one business day." }
  ];
  var CHIPS = ["How does $0 upfront work?", "What does it cost?", "Do I own the website?", "How fast can you start?", "Do you do SEO?", "Leave my details"];

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
    if (/leave (my )?details|call me|contact me|get started|sign me up|growth plan|free preview/i.test(q)) return startLead();
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
    else botSay("Good question — I don't want to guess. Leave your details and [FOUNDER_FIRST] will answer it personally within one business day, or call <a href=\"tel:[US_PHONE_E164]\">[US_PHONE]</a>.");
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
    var el = botSay("Last thing: is it OK if we contact you by phone, text and email about your growth plan? You can reply STOP to opt out anytime.");
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
    fd.append("message", transcript.map(function (m) { return (m.role === "user" ? "Visitor: " : "Assistant: ") + m.text; }).join("\n"));
    typing(true);
    fetch("/send.php", { method: "POST", body: fd, headers: { "Accept": "application/json" } })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        typing(false); input.disabled = false; lead = null;
        if (!res.ok) throw new Error(res.error);
        track("generate_lead", { form: "chat" });
        if (typeof window.gtag === "function" && cfg.adsId && cfg.adsFormLabel) window.gtag("event", "conversion", { send_to: cfg.adsId + "/" + cfg.adsFormLabel });
        botSay("Done — thanks, " + esc(data.name.split(" ")[0]) + "! We'll be in touch within one business day (Mon–Fri, Central time). Want to pick a call time now? <a href=\"/free-preview/\">Request your growth plan</a> or call <a href=\"tel:[US_PHONE_E164]\">[US_PHONE]</a>.");
        setChips(["What does it cost?", "Do I own the website?"]);
      })
      .catch(function (e) {
        typing(false); input.disabled = false; lead = null;
        botSay("Sorry, that didn't send (" + esc(String(e.message || "error")) + "). Please call <a href=\"tel:[US_PHONE_E164]\">[US_PHONE]</a> or use the <a href=\"/free-preview/\">growth plan form</a>.");
        setChips(CHIPS);
      });
  }

  /* ---------- Open / close ---------- */
  function open() {
    panel.hidden = false; launcher.setAttribute("aria-expanded", "true"); root.classList.add("is-open");
    if (!log.children.length) {
      botSay("Hi! I'm the [BRAND] assistant. Ask me anything about getting more roofing jobs from Google — pricing, how the free growth plan works, SEO, ads.");
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
