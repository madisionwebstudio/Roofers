/* ==========================================================================
   ROOFRS — main.js (vanilla, deferred)
   Header · nav · accordions · reveal · count-up · calculator · forms ·
   analytics (opt-in via config.js) · Calendly embed · CTA tracking
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.SITE_CONFIG || {};
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var isPlaceholder = function (v) { return !v || /^\[.*\]$/.test(String(v)); };

  /* ---------- Analytics (GA4 + Google Ads), loads only when enabled ---------- */
  var A = CFG.analytics || {};
  var analyticsOn = A.enabled && !isPlaceholder(A.ga4Id);
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  if (analyticsOn) {
    var gs = document.createElement("script");
    gs.async = true;
    gs.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(A.ga4Id);
    document.head.appendChild(gs);
    window.gtag("js", new Date());
    window.gtag("config", A.ga4Id);
    if (!isPlaceholder(A.adsConversionId)) window.gtag("config", A.adsConversionId);
  }
  function track(name, params) {
    if (!analyticsOn) return;
    window.gtag("event", name, params || {});
  }
  function trackConversion(formType) {
    track("generate_lead", { form_type: formType });
    if (analyticsOn && !isPlaceholder(A.adsConversionId) && !isPlaceholder(A.adsConversionLabel)) {
      window.gtag("event", "conversion", { send_to: A.adsConversionId + "/" + A.adsConversionLabel });
    }
  }

  /* CTA click tracking: any element with data-track="name" */
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("[data-track]");
    if (el) track("cta_click", { cta: el.getAttribute("data-track"), page: location.pathname });
  });

  /* ---------- Header: shrink on scroll + mobile CTA bar ---------- */
  var header = $("[data-header]");
  var bar = $("[data-mobile-bar]");
  var ticking = false;
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-scrolled", y > 24);
    if (bar) bar.classList.toggle("is-visible", y > 420);
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  /* ---------- Mobile nav ---------- */
  var burger = $("[data-burger]");
  var mnav = $("#mobile-nav");
  function setMenu(open) {
    if (!burger || !mnav) return;
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    mnav.classList.toggle("is-open", open);
    document.body.style.overflow = open ? "hidden" : "";
    if (open) { var f = $("a", mnav); if (f) f.focus(); }
  }
  if (burger) burger.addEventListener("click", function () { setMenu(burger.getAttribute("aria-expanded") !== "true"); });

  /* ---------- Services dropdown ---------- */
  $$("[data-dropdown]").forEach(function (item) {
    var btn = $("button", item);
    var closeT;
    function set(open) { item.setAttribute("data-open", String(open)); btn.setAttribute("aria-expanded", String(open)); }
    btn.addEventListener("click", function () { set(btn.getAttribute("aria-expanded") !== "true"); });
    item.addEventListener("mouseenter", function () { clearTimeout(closeT); set(true); });
    item.addEventListener("mouseleave", function () { closeT = setTimeout(function () { set(false); }, 120); });
    item.addEventListener("focusout", function (e) { if (!item.contains(e.relatedTarget)) set(false); });
    document.addEventListener("click", function (e) { if (!item.contains(e.target)) set(false); });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    $$("[data-dropdown][data-open='true']").forEach(function (item) {
      item.setAttribute("data-open", "false");
      var b = $("button", item); b.setAttribute("aria-expanded", "false"); b.focus();
    });
    if (burger && burger.getAttribute("aria-expanded") === "true") { setMenu(false); burger.focus(); }
  });

  /* ---------- Accordions (FAQ) ---------- */
  $$("[data-accordion] .faq__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      if (panel) panel.hidden = open;
    });
  });

  /* ---------- Reveal + count-up ---------- */
  var reveals = $$(".reveal");
  var counters = $$("[data-count]");
  function fmtCount(el, v) {
    var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var n = v.toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec });
    el.textContent = (el.getAttribute("data-prefix") || "") + n;
  }
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    if (reduceMotion || isNaN(target)) { fmtCount(el, target); return; }
    var start = null, dur = 1100;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      fmtCount(el, target * eased);
      if (p < 1) window.requestAnimationFrame(step); else fmtCount(el, target);
    }
    window.requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        if (el.hasAttribute("data-count")) countUp(el); else el.classList.add("is-in");
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.15 });
    reveals.forEach(function (el) { io.observe(el); });
    counters.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Missed-call calculator ---------- */
  var money = function (n) { return "$" + Math.round(n).toLocaleString("en-US"); };
  $$("[data-calc]").forEach(function (calc) {
    var get = function (name) { var i = $("[name='" + name + "']", calc); return i ? parseFloat(i.value) || 0 : null; };
    function render() {
      var calls = get("calls");
      var missedPct = get("missed") / 100;
      var realPct = get("real");
      realPct = realPct === null ? 0.5 : realPct / 100; /* mini version assumes half */
      var value = get("value");
      var closePct = get("close") / 100;

      var missedMonth = calls * 4.33 * missedPct;
      var leadsMonth = missedMonth * realPct;
      var jobsMonth = leadsMonth * closePct;
      var lossMonth = jobsMonth * value;

      $$("[data-out]", calc).forEach(function (o) {
        var k = o.getAttribute("data-out");
        if (k === "month") o.textContent = money(lossMonth);
        if (k === "year") o.textContent = money(lossMonth * 12);
        if (k === "missed") o.textContent = Math.round(missedMonth).toLocaleString("en-US");
        if (k === "leads") o.textContent = leadsMonth.toFixed(1);
        if (k === "jobs") o.textContent = jobsMonth.toFixed(1);
      });
      $$("input[type='range']", calc).forEach(function (r) {
        var out = $("output[for='" + r.id + "']", calc);
        if (out) out.textContent = r.value + (r.getAttribute("data-unit") || "");
      });
    }
    calc.addEventListener("input", render);
    render();
  });

  /* ---------- Forms → /send.php (fetch with no-JS fallback) ---------- */
  $$("form[data-form]").forEach(function (form) {
    var ts = $("input[name='form_ts']", form);
    if (ts) ts.value = String(Date.now());
    var pg = $("input[name='page']", form);
    if (pg) pg.value = location.pathname;
    var plan = $("input[name='plan']", form);
    var m = /[?&]plan=(starter|growth|premium)/.exec(location.search);
    if (plan && m) plan.value = m[1];
    var status = $(".form__status", form);
    var submit = $("button[type='submit']", form);

    function clearErrors() {
      $$(".field--error", form).forEach(function (f) { f.classList.remove("field--error"); });
      $$(".field__err", form).forEach(function (e) { e.remove(); });
    }
    function showError(input, msg) {
      var field = input.closest("fieldset.field, .field, .consent") || input.parentNode;
      field.classList.add("field--error");
      input.setAttribute("aria-invalid", "true");
      var err = document.createElement("span");
      err.className = "field__err";
      err.id = (input.id || input.name) + "-err";
      err.textContent = msg;
      input.setAttribute("aria-describedby", err.id);
      field.appendChild(err);
    }
    function say(type, msg) {
      if (!status) return;
      status.className = "form__status is-" + type;
      status.textContent = msg;
    }

    form.addEventListener("submit", function (e) {
      if (!window.fetch || !window.FormData) return; /* fall back to normal POST */
      e.preventDefault();
      clearErrors();

      var firstBad = null, seenRadio = {};
      $$("input, select, textarea", form).forEach(function (el) {
        if (el.closest(".hp")) return;
        el.removeAttribute("aria-invalid");
        if (!el.checkValidity()) {
          var msg = el.getAttribute("data-msg") || el.validationMessage || "Please check this field.";
          if (el.type === "radio") {
            if (seenRadio[el.name]) return;
            seenRadio[el.name] = true;
            var lead = form.querySelector("input[name='" + el.name + "'][data-msg]");
            if (lead) msg = lead.getAttribute("data-msg");
          }
          showError(el, msg);
          if (!firstBad) firstBad = el;
        }
      });
      if (firstBad) { say("error", "Please fix the highlighted fields."); firstBad.focus(); return; }

      var label = submit ? submit.innerHTML : "";
      if (submit) { submit.disabled = true; submit.textContent = "Sending…"; }
      say("ok", "Sending…");

      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "Accept": "application/json", "X-Requested-With": "fetch" },
        credentials: "same-origin"
      }).then(function (r) {
        return r.json().catch(function () { return { ok: false, message: "Unexpected server response." }; });
      }).then(function (res) {
        if (res && res.ok) {
          trackConversion(form.getAttribute("data-form"));
          say("ok", res.message || "Got it. Redirecting…");
          window.location.href = res.redirect || "/thank-you/";
          return;
        }
        if (res && res.errors) {
          Object.keys(res.errors).forEach(function (name) {
            var el = form.querySelector("[name='" + name + "']");
            if (el) showError(el, res.errors[name]);
          });
        }
        say("error", (res && res.message) || "Something went wrong. Email us instead and we'll handle it by hand.");
        if (submit) { submit.disabled = false; submit.innerHTML = label; }
      }).catch(function () {
        say("error", "Couldn't reach the server. Check your connection, or email " + (CFG.email || "us") + ".");
        if (submit) { submit.disabled = false; submit.innerHTML = label; }
      });
    });
  });

  /* ---------- Calendly embed (only when a real URL is configured) ---------- */
  $$("[data-calendly]").forEach(function (box) {
    var url = CFG.calendlyUrl;
    if (isPlaceholder(url)) return;
    var w = document.createElement("div");
    w.className = "calendly-inline-widget";
    w.setAttribute("data-url", url + (url.indexOf("?") > -1 ? "&" : "?") + "hide_gdpr_banner=1&primary_color=f26b1d");
    box.replaceWith(w);
    var s = document.createElement("script");
    s.src = "https://assets.calendly.com/assets/external/widget.js";
    s.async = true;
    document.body.appendChild(s);
  });

  /* ---------- Article table of contents: active section ---------- */
  var tocLinks = $$(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var tio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
          map[en.target.id].classList.add("is-active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) tio.observe(h); });
  }
})();
