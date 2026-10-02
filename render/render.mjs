// Renders the shot list through headless Chromium (SwiftShader WebGL) and writes PNGs to renders/<date>/.
//   node render.mjs                 all shots, v1, today's date
//   node render.mjs --only 01,03    some shots
//   node render.mjs --v 2           version suffix for the file names (match the prompt version)
//   node render.mjs --scale 2       supersample 2x and downscale with ImageMagick
//   node render.mjs --date 2026-10-01 --out /tmp/x
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { shots, explore, explore2, explore3, explore4, retired, SIZE } from './src/shots.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..');
const args = {};
for (let i = 0; i < process.argv.length; i++) if (process.argv[i].startsWith('--')) args[process.argv[i].slice(2)] = process.argv[i + 1];

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.woff': 'font/woff', '.css': 'text/css', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  const f = path.join(repo, p);
  if (!f.startsWith(repo) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const scale = Number(args.scale || 1);
const size = [SIZE[0] * scale, SIZE[1] * scale];
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.goto(`http://127.0.0.1:${port}/render/page.html`);
await page.waitForFunction(() => window.earmilk && (window.earmilk.ready || window.earmilk.error), null, { timeout: 180000 });
const initError = await page.evaluate(() => window.earmilk.error || null);
if (initError) { console.error(initError); process.exit(1); }

const date = args.date || new Date().toISOString().slice(0, 10);
const v = args.v || '1';
const isExplore = ['explore', 'explore2', 'explore3', 'explore4'].includes(args.list);
const isRetired = args.list === 'retired';
const outDir = args.out || path.join(repo, isExplore ? 'explore' : 'renders', date);
fs.mkdirSync(outDir, { recursive: true });
const only = args.only ? args.only.split(',').map(s => s.trim().padStart(2, '0')) : null;

const list = isExplore ? ({ explore, explore2, explore3, explore4 })[args.list].map(e => ({ id: e.id, frames: [e] })) : isRetired ? retired : shots;
for (const shot of list) {
  const nn = isExplore ? shot.id : shot.id.slice(5);
  if (only && !only.includes(nn)) continue;
  for (const frame of shot.frames) {
    const t0 = Date.now();
    const cfg = { ...frame, size };
    const url = await page.evaluate(c => window.earmilk.renderShot(c), cfg);
    const file = path.join(outDir, isExplore ? `${shot.id}.png` : `${shot.id}-v${v}${frame.suffix || ''}.png`);
    fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
    if (scale !== 1) execFileSync('convert', [file, '-filter', 'Lanczos', '-resize', `${SIZE[0]}x${SIZE[1]}`, file]);
    console.log(`${path.relative(repo, file)}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
}
await browser.close();
server.close();
