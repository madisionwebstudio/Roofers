/* Roofrs — site script. Vanilla JS, loaded with `defer`. */
(function () {
  "use strict";
  var d = document, cfg = window.SITE || {};
  d.documentElement.classList.remove("no-js");
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Mobile nav ---------- */
  var burger = d.querySelector(".burger"), mnav = d.getElementById("mnav");
  if (burger && mnav) {
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") !== "true";
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      burger.querySelector("use").setAttribute("href", "/assets/img/icons.svg#" + (open ? "i-x" : "i-menu"));
      mnav.setAttribute("data-open", String(open));
      d.body.style.overflow = open ? "hidden" : "";
    });
    d.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && mnav.getAttribute("data-open") === "true") { burger.click(); burger.focus(); }
    });
  }

  /* Hide the mobile bottom bar while a form is on screen (it would cover fields) */
  var mbar = d.querySelector(".mbar"), forms = d.querySelectorAll("form.form");
  if (mbar && forms.length && "IntersectionObserver" in window) {
    var io0 = new IntersectionObserver(function (es) {
      es.forEach(function (e) { var h = e.isIntersecting ? "true" : "false"; mbar.setAttribute("data-hide", h); var c = d.getElementById("chatbot"); if (c && !c.classList.contains("is-open")) c.setAttribute("data-hide", h); });
    }, { threshold: 0.05 });
    forms.forEach(function (f) { io0.observe(f); });
  }

  /* ---------- Reveal + count-up ---------- */
  var reveals = d.querySelectorAll(".reveal"), counts = d.querySelectorAll("[data-count]");
  function countUp(el) {
    var end = parseFloat(el.getAttribute("data-count")), pre = el.getAttribute("data-pre") || "", suf = el.getAttribute("data-suf") || "";
    var fmt = function (n) { return pre + Math.round(n).toLocaleString("en-US") + suf; };
    if (reduce) { el.textContent = fmt(end); return; }
    var t0 = null, dur = 1200;
    function step(t) { if (!t0) t0 = t; var p = Math.min((t - t0) / dur, 1); el.textContent = fmt(end * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        if (e.target.hasAttribute("data-count")) countUp(e.target); else e.target.classList.add("in");
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
    counts.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Tabs (admin showcase) ---------- */
  d.querySelectorAll("[role=tablist]").forEach(function (list) {
    var tabs = list.querySelectorAll("[role=tab]");
    function sel(tab) {
      tabs.forEach(function (t) {
        var on = t === tab; t.setAttribute("aria-selected", String(on)); t.tabIndex = on ? 0 : -1;
        d.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { sel(t); });
      t.addEventListener("keydown", function (e) {
        var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (k) { var n = tabs[(i + k + tabs.length) % tabs.length]; sel(n); n.focus(); e.preventDefault(); }
      });
    });
  });

  /* ---------- Analytics (only when IDs are configured) ---------- */
  function track(name, params) {
    params = params || {};
    params.page_path = location.pathname;
    if (typeof window.gtag === "function") window.gtag("event", name, params);
    (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name }, params));
  }
  function adsConversion(label) {
    if (typeof window.gtag === "function" && cfg.adsId && label) window.gtag("event", "conversion", { send_to: cfg.adsId + "/" + label });
  }
  d.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a,button");
    if (!a) return;
    var cta = a.getAttribute("data-cta");
    if (cta) track("cta_click", { cta: cta, text: (a.textContent || "").trim().slice(0, 60) });
    if (a.href && a.href.indexOf("tel:") === 0) { track("phone_click", { cta: cta || "tel" }); adsConversion(cfg.adsCallLabel); }
    if (a.href && a.href.indexOf("wa.me/") !== -1) { track("whatsapp_click", { cta: cta || "whatsapp" }); adsConversion(cfg.adsCallLabel); }
    if (a.href && a.href.indexOf("mailto:") === 0) { track("email_click", { cta: cta || "email" }); adsConversion(cfg.adsCallLabel); }
  });

  /* ---------- Before/after slider ---------- */
  d.querySelectorAll("[data-ba]").forEach(function (ba) {
    var r = ba.querySelector(".ba__range");
    var set = function () { ba.style.setProperty("--pos", r.value + "%"); };
    r.addEventListener("input", set); set();
  });

  /* ---------- Ad attribution: UTM + gclid -> hidden fields (kept for the visit) ---------- */
  var ATTR = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];
  var qs = new URLSearchParams(location.search), attrib = {};
  try { attrib = JSON.parse(sessionStorage.getItem("attrib") || "{}"); } catch (e) {}
  ATTR.forEach(function (k) { if (qs.get(k)) attrib[k] = qs.get(k).slice(0, 200); });
  if (!attrib.landing_page) attrib.landing_page = location.pathname;
  try { sessionStorage.setItem("attrib", JSON.stringify(attrib)); } catch (e) {}
  d.querySelectorAll("form.form").forEach(function (f) {
    ATTR.concat(["landing_page"]).forEach(function (k) {
      if (!attrib[k] || f.querySelector('[name="' + k + '"]')) return;
      var i = d.createElement("input"); i.type = "hidden"; i.name = k; i.value = attrib[k]; f.appendChild(i);
    });
  });
  /* Preselect the service from ?service=web-design|seo|google-ads */
  var svc = qs.get("service"), sel = d.querySelector("select[name=service]");
  if (svc && sel) { Array.prototype.forEach.call(sel.options, function (o) { if (o.value === svc) sel.value = svc; }); }
  window.__attrib = attrib;

  /* ---------- Forms ---------- */
  d.querySelectorAll("form.form").forEach(function (form) {
    var started = Date.now();
    var ts = form.querySelector("[name=_ts]"); if (ts) ts.value = String(started);
    var status = form.querySelector(".form-status");
    function setErr(field, msg) {
      var wrap = field.closest(".field"); if (!wrap) return;
      wrap.setAttribute("data-invalid", msg ? "true" : "false");
      var e = wrap.querySelector(".err"); if (e && msg) e.textContent = msg;
      var inputs = wrap.querySelectorAll("input,select,textarea");
      inputs.forEach(function (i) { if (msg) i.setAttribute("aria-invalid", "true"); else i.removeAttribute("aria-invalid"); });
    }
    function validate() {
      var bad = null;
      form.querySelectorAll("[required]").forEach(function (f) {
        var msg = "";
        if (f.type === "checkbox" && !f.checked) msg = f.getAttribute("data-msg") || "Please tick this box.";
        else if (f.type !== "checkbox" && !f.value.trim()) msg = f.getAttribute("data-msg") || "This one is required.";
        else if (f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.value.trim())) msg = "That email doesn't look right.";
        else if (f.type === "tel" && f.value.replace(/\D/g, "").length < 10) msg = "Please enter a 10-digit US phone number.";
        setErr(f, msg); if (msg && !bad) bad = f;
      });
      return bad;
    }
    form.addEventListener("input", function (e) { var w = e.target.closest(".field"); if (w && w.getAttribute("data-invalid") === "true") validate(); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = validate();
      if (bad) { bad.focus(); return; }
      var btn = form.querySelector("[type=submit]"), label = btn.innerHTML;
      btn.disabled = true; btn.textContent = "Sending…";
      if (status) status.setAttribute("data-show", "false");
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { "Accept": "application/json" } })
        .then(function (r) { return r.json().catch(function () { return { ok: false, error: "Server error (" + r.status + ")." }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.error || "Something went wrong.");
          track("generate_lead", { form: form.getAttribute("data-form") });
          adsConversion(cfg.adsFormLabel);
          setTimeout(function () { location.href = res.redirect || "/thank-you/"; }, 250);
        })
        .catch(function (err) {
          btn.disabled = false; btn.innerHTML = label;
          if (status) { status.textContent = err.message + " You can also call or email us — details are at the bottom of the page."; status.setAttribute("data-show", "true"); status.focus(); }
        });
    });
  });

  /* ---------- Calendly (thank-you page) ---------- */
  var cal = d.getElementById("calendly");
  if (cal) {
    var url = cfg.calendly;
    if (url && /^https:\/\/calendly\.com\//.test(url)) {
      cal.innerHTML = '<div class="calendly-inline-widget" data-url="' + url + '?hide_gdpr_banner=1" style="min-width:300px;height:720px"></div>';
      var s = d.createElement("script"); s.src = "https://assets.calendly.com/assets/external/widget.js"; s.async = true; d.body.appendChild(s);
    }
  }

  /* ---------- Chat assistant: load chat.js on first intent ---------- */
  var chatBtn = d.getElementById("chat-launcher");
  if (chatBtn) {
    var loaded = false;
    var load = function (openNow) {
      if (openNow) d.getElementById("chatbot").setAttribute("data-open-on-load", "true");
      if (loaded) { return; } loaded = true;
      var s = d.createElement("script"); s.src = "/assets/js/chat.js"; s.async = true; d.body.appendChild(s);
    };
    chatBtn.addEventListener("pointerenter", function () { load(false); }, { once: true });
    chatBtn.addEventListener("focus", function () { load(false); }, { once: true });
    chatBtn.addEventListener("click", function onFirst(e) {
      if (!window.__chatReady) { e.stopImmediatePropagation(); load(true); }
    }, { once: true });
  }

  /* ---------- Year ---------- */
  d.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
