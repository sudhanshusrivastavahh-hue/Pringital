#!/usr/bin/env node
// Save an edition's paper front page as a one-page A4 PDF with every link clickable.
//
// Usage: node scripts/make_pdf.js 2026-11-13 [2026-11-12 ...]
// Writes archive/YYYY-MM-DD/Pringital-News-D-Mon-YYYY.pdf for each date.
// Needs Playwright with Chromium, and network access to Google Fonts for the real typefaces.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const SITE = 'https://pringital.com';
const A4 = { w: 793.7, h: 1122.5 }; // CSS px at 96 dpi
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml', '.mp3': 'audio/mpeg', '.json': 'application/json' };

function pdfName(date) {
  const d = new Date(date + 'T00:00:00Z');
  const mon = d.toLocaleString('en-GB', { month: 'short', timeZone: 'UTC' });
  return `Pringital-News-${d.getUTCDate()}-${mon}-${d.getUTCFullYear()}.pdf`;
}

function serve() {
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (p.endsWith('/')) p += 'index.html';
    const f = path.join(ROOT, path.normalize(p));
    if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => r(server)));
}

(async () => {
  const dates = process.argv.slice(2);
  if (!dates.length) { console.error('Usage: node scripts/make_pdf.js YYYY-MM-DD ...'); process.exit(2); }
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch();
  try {
    for (const date of dates) {
      const page = await browser.newPage({ viewport: { width: 1300, height: 1000 } });
      await page.addInitScript(() => {
        try { localStorage.setItem('pn-mode', 'paper'); localStorage.setItem('pn-theme', 'light'); } catch (e) {}
      });
      await page.goto(`${base}/archive/${date}/`, { waitUntil: 'networkidle' });
      const size = await page.evaluate(async (SITE) => {
        document.documentElement.setAttribute('data-mode', 'paper');
        document.documentElement.setAttribute('data-theme', 'light');
        const pg = document.getElementById('page');
        // Links in the PDF must point at the live site, not at this local server.
        pg.querySelectorAll('a[href]').forEach(a => {
          const h = a.getAttribute('href');
          if (h.startsWith('/') || !/^[a-z]+:/i.test(h)) a.href = new URL(h, SITE + location.pathname).href;
        });
        pg.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager');
        await Promise.all([...pg.querySelectorAll('img')].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
        await document.fonts.ready;
        // Lay out the paper page on its own, unscaled, at the top-left of a blank sheet.
        const s = document.createElement('style');
        s.textContent = `@page{size:A4;margin:0}
          html,body{background:#fff!important;margin:0!important;padding:0!important}
          body>*:not(#fit){display:none!important}
          #fit{height:auto!important;margin:0!important;padding:0!important;width:auto!important}
          #fit>*:not(#page){display:none!important}
          #page{transform:none!important;margin:0!important;box-shadow:none!important}`;
        document.head.appendChild(s);
        if (!document.getElementById('fit').contains(pg)) document.body.prepend(pg);
        return { w: pg.scrollWidth, h: pg.scrollHeight };
      }, SITE);
      const scale = Math.min(A4.w / size.w, A4.h / size.h);
      const out = path.join(ROOT, 'archive', date, pdfName(date));
      await page.pdf({ path: out, format: 'A4', printBackground: true, scale, pageRanges: '1',
        margin: { top: 0, right: 0, bottom: 0, left: 0 } });
      console.log(`${path.relative(ROOT, out)}  (${size.w}x${size.h}px, scale ${scale.toFixed(3)})`);
      await page.close();
    }
  } finally {
    await browser.close();
    server.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
