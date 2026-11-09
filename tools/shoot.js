// QA screenshots. Usage: node tools/shoot.js <outdir> <width> <path> [path...]
// Serve public_html first, e.g.: php -S 127.0.0.1:8080 -t public_html
const { chromium } = require('playwright');
(async () => {
  const [out, width, ...paths] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: +width, height: +width < 800 ? 844 : 900 }, deviceScaleFactor: 1 });
  for (const p of paths) {
    await pg.goto('http://127.0.0.1:8080' + p, { waitUntil: 'networkidle' });
    await pg.evaluate(async () => { document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')); for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } window.scrollTo(0, 0); });
    await pg.waitForTimeout(300);
    const sw = await pg.evaluate(() => document.documentElement.scrollWidth);
    if (sw > +width) console.log('HORIZONTAL SCROLL', p, sw);
    const name = (p.replace(/\//g, '_') || '_') + '-' + width;
    await pg.screenshot({ path: `${out}/${name}.png`, fullPage: true });
    await pg.screenshot({ path: `${out}/${name}-fold.png` });
  }
  await b.close();
})();
