#!/usr/bin/env node
// SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
// SPDX-License-Identifier: Apache-2.0
// Build one editable HTML poster with a strict 32 CSS px print-text floor.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { pathToFileURL } = require('node:url');
let playwright;
try { playwright = require('playwright'); }
catch {
  const moduleRoot = process.env.CODEX_NODE_MODULES || path.join(os.homedir(),
    '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
  playwright = require(path.join(moduleRoot, 'playwright'));
}
const root = __dirname;
const outArg = process.argv.indexOf('--out-dir');
if (outArg < 0 || !process.argv[outArg + 1]) {
  throw new Error('Usage: node build-poster.cjs --out-dir /absolute/review-directory [--check-only]');
}
const output = path.resolve(process.argv[outArg + 1]);
const checkOnly = process.argv.includes('--check-only');
fs.mkdirSync(output, { recursive: true });
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

(async () => {
  const browser = await playwright.chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 4224, height: 4224 }, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    // Every asset is local; building never needs website content.
    await page.route(/^https?:/, route => route.abort());
    await page.goto(pathToFileURL(path.join(root, 'index.html')).href, { waitUntil: 'load' });
    await page.emulateMedia({ media: 'print' });
    await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
    const audit = await page.evaluate(() => {
      const poster = document.querySelector('.poster');
      const bounds = poster.getBoundingClientRect();
      const rect = r => ({ x: r.x - bounds.x, y: r.y - bounds.y, width: r.width, height: r.height });
      const text = [], small = [], outside = [], regionOverflow = [], internalOverflow = [], unlinkedImages = [], sectionOverlap = [];
      const walker = document.createTreeWalker(poster, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (!node.textContent.trim()) continue;
        const el = node.parentElement;
        const style = getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        const range = document.createRange(); range.selectNodeContents(node);
        if (!range.getClientRects().length) continue;
        const row = { text: node.textContent.trim(), px: parseFloat(style.fontSize), element: el.tagName };
        text.push(row);
        if (row.px < 32) small.push(row);
      }
      for (const el of poster.querySelectorAll('*')) {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        if (r.left < bounds.left - 1 || r.top < bounds.top - 1 || r.right > bounds.right + 1 || r.bottom > bounds.bottom + 1) {
          outside.push({ element: el.tagName, class: el.className, rect: rect(r) });
        }
        const s = getComputedStyle(el);
        if (s.display !== 'inline' && el.clientWidth && el.scrollWidth > el.clientWidth + 2) {
          internalOverflow.push({ element: el.tagName, class: el.className, width: el.clientWidth, scroll: el.scrollWidth });
        }
      }
      // The page can contain an overlapping footer even if every element fits
      // its outer canvas. Check the four original template regions separately.
      for (const region of poster.children) {
        const area = region.getBoundingClientRect();
        for (const el of region.querySelectorAll('*')) {
          const r = el.getBoundingClientRect();
          if (r.width && r.height && (r.top < area.top - 1 || r.bottom > area.bottom + 1)) {
            regionOverflow.push({ region: region.className, element: el.tagName, class: el.className, rect: rect(r) });
          }
        }
      }
      for (const parent of poster.querySelectorAll('.study-main, .outcomes')) {
        const sections = [...parent.children];
        for (let i = 1; i < sections.length; i++) {
          const previous = sections[i - 1].getBoundingClientRect();
          const next = sections[i].getBoundingClientRect();
          if (next.top < previous.bottom - 1) sectionOverlap.push({ parent: parent.className, previous: sections[i - 1].className, next: sections[i].className });
        }
      }
      const images = [...poster.querySelectorAll('img')].map(img => {
        const link = img.closest('a');
        if (!link || !link.href.startsWith('https://')) unlinkedImages.push(img.src);
        return { src: img.getAttribute('src'), loaded: img.complete && img.naturalWidth > 0, href: link?.href, rect: rect(img.getBoundingClientRect()) };
      });
      const qrs = [...poster.querySelectorAll('[data-qr]')].map(a => ({ name: a.dataset.qr, url: a.href, rect: rect(a.querySelector('img').getBoundingClientRect()) }));
      const links = [...new Set([...poster.querySelectorAll('a')].map(a => a.href))];
      const blocks = [...poster.querySelectorAll('.property-section, .property-table, .property-table tbody tr, .stages-section, .section-heading, .stage-cards, .stages-figure, .scientific-results, .scope-note, .outcomes > section')].map(el => ({ element: el.tagName, class: el.className, rect: rect(el.getBoundingClientRect()) }));
      return { size_css_px: { width: bounds.width, height: bounds.height }, minimum_text_px: Math.min(...text.map(t => t.px)), text_node_count: text.length, small, outside, regionOverflow, internalOverflow, sectionOverlap, unlinkedImages, images, qrs, links, blocks };
    });
    audit.browser = browser.version();
    audit.created_utc = new Date().toISOString();
    audit.source_sha256 = Object.fromEntries(['index.html', 'template.css', 'poster.css', 'build-poster.cjs', 'verify-pdf.py', 'verify-links.py', 'make-logo-qrs.py', 'source-manifest.json', 'update-results.py', 'results-data.json'].map(n => [n, sha(path.join(root, n))]));
    audit.errors = errors;
    fs.writeFileSync(path.join(output, 'html-audit.json'), JSON.stringify(audit, null, 2) + '\n');
    if (errors.length || audit.small.length || audit.outside.length || audit.regionOverflow.length || audit.internalOverflow.length || audit.sectionOverlap.length || audit.unlinkedImages.length || audit.images.some(i => !i.loaded)) {
      throw new Error('HTML layout or asset audit failed; inspect html-audit.json.');
    }
    if (!checkOnly) {
      await page.pdf({ path: path.join(output, 'stamped-ai-poster.pdf'), preferCSSPageSize: true, printBackground: true, tagged: true });
      await page.screenshot({ path: path.join(output, 'html-fullsize.png'), fullPage: true });
    }
    console.log(JSON.stringify({ output, check_only: checkOnly, minimum_text_px: audit.minimum_text_px, qrs: audit.qrs.length, links: audit.links.length }));
  } finally { await browser.close(); }
})().catch(e => { console.error(e.stack); process.exitCode = 1; });
