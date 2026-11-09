// Renders brand bitmaps (OG image, founder placeholder, logo PNGs) from HTML with the site fonts.
// Usage: node tools/brand/render.js "<BRAND>" "<FOUNDER_NAME>"   (tools/build.py does NOT run this; run it when the brand changes)
const { chromium } = require('playwright'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..'); const F = 'file://' + ROOT + '/src/static/assets/fonts/'; const IMG = ROOT + '/src/static/assets/img/';
const brand = process.argv[2] || 'Roofrs'; const founder = process.argv[3] || 'Rakesh Dadhich';
const initials = founder.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase();
const css = `@font-face{font-family:Anton;src:url(${F}anton-latin-400-normal.woff2)}@font-face{font-family:B;font-weight:800;src:url(${F}barlow-condensed-latin-800-normal.woff2)}@font-face{font-family:B;font-weight:700;src:url(${F}barlow-condensed-latin-700-normal.woff2)}*{margin:0;box-sizing:border-box}body{background:#0F1E2E;color:#fff;font-family:B}`;
const mark = (w) => `<svg width="${w}" viewBox="0 0 38 24"><path d="M2.5 21.5L19 5.5l16.5 16" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="square"/><path d="M26.5 9.5V3h4.5v10.8" fill="none" stroke="#F26B1D" stroke-width="3.2" stroke-linecap="square"/></svg>`;
const tape = `background:repeating-linear-gradient(-45deg,#F26B1D 0 14px,#14181D 14px 28px)`;
const jobs = [
  ['og-default.jpg', 1200, 630, `<div style="height:630px;padding:64px 72px;position:relative;background:linear-gradient(90deg,rgba(15,30,46,.97) 0,rgba(15,30,46,.88) 55%,rgba(15,30,46,.5)),url(file://${IMG}hero-crew-1440.webp) 70% 50%/cover">
    <div style="display:flex;align-items:center;gap:14px">${mark(64)}<span style="font:400 46px Anton;text-transform:uppercase;letter-spacing:.03em">${brand}</span></div>
    <div style="font:400 92px/.95 Anton;text-transform:uppercase;margin-top:44px;max-width:900px">We build your roofing website first. <span style="color:#F26B1D">Pay only if you love it.</span></div>
    <div style="position:absolute;left:72px;bottom:56px;font:700 28px B;letter-spacing:.1em;text-transform:uppercase;color:#C9D1D8">$0 upfront · Free 5-day preview · Roofing only</div>
    <div style="position:absolute;left:0;right:0;bottom:0;height:16px;${tape}"></div></div>`],
  ['founder-placeholder.webp', 800, 1000, `<div style="height:1000px;position:relative;background:#1F2A37;display:grid;place-items:center">
    <div style="position:absolute;inset:40px;border:2px solid #2C3A4A"></div>
    <div style="font:400 360px/1 Anton;color:transparent;-webkit-text-stroke:3px #F26B1D">${initials}</div>
    <div style="position:absolute;left:0;right:0;bottom:90px;text-align:center;font:700 30px B;letter-spacing:.16em;text-transform:uppercase;color:#A9B3BB">Founder photo coming soon</div>
    <div style="position:absolute;left:0;right:0;bottom:0;height:22px;${tape}"></div></div>`],
  ['logo.png', 512, 512, `<div style="height:512px;display:grid;place-items:center;background:#0F1E2E">${mark(360)}</div>`],
  ['apple-touch-icon.png', 180, 180, `<div style="height:180px;display:grid;place-items:center;background:#0F1E2E">${mark(124)}</div>`],
];
(async () => {
  const b = await chromium.launch();
  for (const [name, w, h, body] of jobs) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const tmp = require('os').tmpdir() + '/brand-' + Date.now() + '.html'; require('fs').writeFileSync(tmp, `<style>${css}</style>${body}`); await p.goto('file://' + tmp); await p.waitForTimeout(300);
    const out = IMG + name;
    if (name.endsWith('.webp')) { await p.screenshot({ path: out.replace('.webp', '.png') }); }
    else await p.screenshot({ path: out, type: name.endsWith('.jpg') ? 'jpeg' : 'png', quality: name.endsWith('.jpg') ? 82 : undefined });
    await p.close();
  }
  await b.close();
})();
