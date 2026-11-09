// Screenshot each demo page at desktop (1440) and mobile (390) width. Full page.
const { chromium } = require('playwright');
(async () => {
  const paths = JSON.parse(process.argv[2]); const out = process.argv[3];
  const b = await chromium.launch();
  for (const [key, p] of Object.entries(paths)) {
    for (const [kind, w, h] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
      const pg = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: kind === 'mobile' ? 2 : 1 });
      await pg.goto('file://' + p); await pg.waitForTimeout(400);
      await pg.screenshot({ path: `${out}/${key}-${kind}.png`, fullPage: true });
      await pg.close();
    }
  }
  await b.close();
})();
