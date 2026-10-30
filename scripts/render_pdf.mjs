// Run after knitting the Rmd: node scripts/render_pdf.mjs [input.html] [output.pdf]
// Requires Playwright and a Chromium installation; no network content is loaded.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let playwright;
try { playwright = await import('playwright'); }
catch (error) {
  if (!process.env.PLAYWRIGHT_MODULE) throw new Error('Install playwright or set PLAYWRIGHT_MODULE to its index.mjs file.');
  playwright = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
}
const input = path.resolve(process.argv[2] || path.join(root, 'public-article-kp.html'));
const output = path.resolve(process.argv[3] || path.join(root, 'public-article-kp-print.pdf'));
const css = await fs.readFile(path.join(root, 'styles/article-print.css'), 'utf8');
const launch = { headless: true };
if (process.env.CHROME_BIN) launch.executablePath = process.env.CHROME_BIN;
const browser = await playwright.chromium.launch(launch);
try {
  const page = await browser.newPage();
  await page.route(/^https?:/, route => route.abort());
  await page.goto(pathToFileURL(input).href, { waitUntil: 'load' });
  await page.evaluate(() => {
    document.querySelectorAll('details').forEach(d => { d.open = true; });
    const authorNote = document.getElementById('author-note');
    const opening = document.querySelector('.opening');
    if (authorNote && opening) opening.append(authorNote);
    document.querySelectorAll('img').forEach(img => img.closest('p')?.classList.add('figure-print'));
    // Keep each figure-led argument together; the two closing sections share a page.
    [...document.querySelectorAll('.main-container > .section.level2')].slice(0, 6)
      .forEach(section => section.classList.add('print-section-start'));
    [...document.querySelectorAll('.main-container > .section.level2')].slice(5)
      .forEach(section => section.classList.add('print-closing'));
    const notes = document.querySelector('.footnotes');
    if (notes) {
      const h = document.createElement('h2'); h.textContent = 'Sources and notes'; notes.prepend(h);
    }
  });
  await page.addStyleTag({content: css});
  await page.emulateMedia({ media: 'print' });
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(img => img.decode()));
  });
  const audit = await page.evaluate(() => ({
    title: document.title,
    images: [...document.images].map(i => ({loaded:i.complete && i.naturalWidth > 0, alt:i.alt})),
    badLocalLinks: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => !/^(#|https?:|mailto:)/.test(h))
  }));
  if (audit.images.some(i => !i.loaded) || audit.badLocalLinks.length) throw new Error(JSON.stringify(audit));
  await page.pdf({path: output, format: 'A4', preferCSSPageSize: true,
    printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;padding:0 15mm;font-family:Arial,sans-serif;font-size:8px;color:#596870;display:flex;justify-content:space-between"><span>Kyle Peyton · Melbourne’s Nominal Tertiary Education Union</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    tagged: true, outline: true});
  console.log(JSON.stringify({output,...audit},null,2));
} finally { await browser.close(); }
