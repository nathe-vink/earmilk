// Canvas-generated textures: wordmarks, the engraved label, the bowl gradient, birch grain, floor planks.
// Everything is drawn in millimetres at a chosen pixels-per-millimetre so the decal planes can be sized exactly.

export function makeTextures(THREE) {
  const cache = new Map();

  function canvasTexture(canvas, { srgb = true, repeat = null } = {}) {
    const t = new THREE.CanvasTexture(canvas);
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    t.needsUpdate = true;
    return t;
  }

  function memo(key, fn) { if (!cache.has(key)) cache.set(key, fn()); return cache.get(key); }

  // A single line of text as a transparent decal, any weight, optional arrow after it (exploration marks).
  function label({ text, sizeMm, color, weight = 700, family = 'Archivo', trackingEm = 0.04, pxPerMm = 8, arrow = false }) {
    return memo(`lb|${text}|${sizeMm}|${color}|${weight}|${family}|${trackingEm}|${arrow}`, () => {
      const fontPx = sizeMm * pxPerMm;
      const c = document.createElement('canvas');
      let ctx = c.getContext('2d');
      const font = `${weight} ${fontPx}px "${family}"`;
      ctx.font = font; ctx.letterSpacing = `${trackingEm * fontPx}px`;
      const tw = ctx.measureText(text).width;
      const arrowW = arrow ? fontPx * 1.6 : 0;
      c.width = Math.ceil(tw + arrowW + fontPx * 0.2); c.height = Math.ceil(fontPx * 1.3);
      ctx = c.getContext('2d');
      ctx.font = font; ctx.letterSpacing = `${trackingEm * fontPx}px`; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = color;
      ctx.fillText(text, fontPx * 0.1, fontPx * 1.0);
      if (arrow) {
        const x0 = fontPx * 0.1 + tw + fontPx * 0.35, y = fontPx * 0.64, h = fontPx * 0.5;
        ctx.fillRect(x0, y - h * 0.18, fontPx * 0.7, h * 0.36);
        ctx.beginPath(); ctx.moveTo(x0 + fontPx * 0.7, y - h * 0.5); ctx.lineTo(x0 + fontPx * 1.2, y); ctx.lineTo(x0 + fontPx * 0.7, y + h * 0.5); ctx.closePath(); ctx.fill();
      }
      return { texture: canvasTexture(c), widthMm: c.width / pxPerMm, heightMm: c.height / pxPerMm };
    });
  }

  // Inkjet date-stamp lettering: the text rasterised, then shown only as a grid of dots.
  function dotText({ text, sizeMm, color, pxPerMm = 8, pitchMm = null }) {
    return memo(`dt|${text}|${sizeMm}|${color}`, () => {
      const fontPx = sizeMm * pxPerMm;
      const src = document.createElement('canvas');
      let ctx = src.getContext('2d');
      const font = `700 ${fontPx}px "Archivo"`;
      ctx.font = font; ctx.letterSpacing = `${0.08 * fontPx}px`;
      const w = Math.ceil(ctx.measureText(text).width + fontPx * 0.2);
      src.width = w; src.height = Math.ceil(fontPx * 1.3);
      ctx = src.getContext('2d'); ctx.font = font; ctx.letterSpacing = `${0.08 * fontPx}px`; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#000';
      ctx.fillText(text, fontPx * 0.1, fontPx * 1.0);
      const data = ctx.getImageData(0, 0, src.width, src.height).data;
      const c = document.createElement('canvas'); c.width = src.width; c.height = src.height;
      const out = c.getContext('2d'); out.fillStyle = color;
      const pitch = (pitchMm || sizeMm / 7) * pxPerMm, r = pitch * 0.34;
      for (let y = pitch / 2; y < c.height; y += pitch) for (let x = pitch / 2; x < c.width; x += pitch) {
        const i = (Math.floor(y) * src.width + Math.floor(x)) * 4 + 3;
        if (data[i] > 90) { out.beginPath(); out.arc(x, y, r, 0, Math.PI * 2); out.fill(); }
      }
      return { texture: canvasTexture(c), widthMm: c.width / pxPerMm, heightMm: c.height / pxPerMm };
    });
  }

  // A barcode as a decal: bars from the digits, the digits set below (proposal mark).
  function barcode({ digits, widthMm, heightMm, color, pxPerMm = 8 }) {
    return memo(`bc|${digits}|${widthMm}|${heightMm}|${color}`, () => {
      const c = document.createElement('canvas'); c.width = Math.ceil(widthMm * pxPerMm); c.height = Math.ceil(heightMm * pxPerMm);
      const ctx = c.getContext('2d'); ctx.fillStyle = color;
      const textPx = heightMm * pxPerMm * 0.2, barsH = c.height - textPx * 1.3;
      const code = digits.replace(/\s/g, '');
      let x = c.width * 0.04; const unit = (c.width * 0.92) / (code.length * 7 + 11);
      const guard = () => { ctx.fillRect(x, 0, unit, barsH + textPx * 0.5); x += unit * 2; ctx.fillRect(x, 0, unit, barsH + textPx * 0.5); x += unit * 2; };
      guard();
      for (const ch of code) {
        const n = ch.charCodeAt(0);
        const widths = [1 + (n % 3), 1 + ((n >> 2) % 2), 1 + ((n >> 1) % 3)];
        const gaps = [1 + ((n >> 3) % 2), 1 + (n % 2)];
        ctx.fillRect(x, 0, widths[0] * unit, barsH); x += (widths[0] + gaps[0]) * unit;
        ctx.fillRect(x, 0, widths[1] * unit, barsH); x += (widths[1] + gaps[1]) * unit;
        ctx.fillRect(x, 0, widths[2] * unit, barsH); x += (widths[2] + 1) * unit;
      }
      guard();
      ctx.font = `500 ${textPx}px "Archivo"`; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(digits, c.width / 2, c.height - textPx * 0.15);
      return { texture: canvasTexture(c), widthMm, heightMm };
    });
  }

  // A stamped roundel: two rings, text around the top and the bottom, a letter in the middle.
  function roundel({ top, bottom, diameterMm, color, pxPerMm = 6 }) {
    return memo(`rd|${top}|${bottom}|${diameterMm}|${color}`, () => {
      const D = diameterMm * pxPerMm, R = D / 2;
      const c = document.createElement('canvas'); c.width = c.height = Math.ceil(D);
      const ctx = c.getContext('2d');
      ctx.strokeStyle = color; ctx.fillStyle = color;
      ctx.lineWidth = D * 0.025; ctx.beginPath(); ctx.arc(R, R, R - D * 0.02, 0, Math.PI * 2); ctx.stroke();
      ctx.lineWidth = D * 0.012; ctx.beginPath(); ctx.arc(R, R, R - D * 0.19, 0, Math.PI * 2); ctx.stroke();
      const ring = (text, fontPx, radius, startAngle, flip) => {
        ctx.font = `700 ${fontPx}px "Archivo"`; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
        const widths = [...text].map(ch => ctx.measureText(ch).width + fontPx * 0.12);
        const total = widths.reduce((a, b) => a + b, 0);
        let a = startAngle - (flip ? -1 : 1) * (total / radius) / 2;
        [...text].forEach((ch, i) => {
          const da = (widths[i] / radius) * (flip ? -1 : 1);
          const mid = a + da / 2;
          ctx.save(); ctx.translate(R + radius * Math.cos(mid), R + radius * Math.sin(mid)); ctx.rotate(mid + (flip ? -Math.PI / 2 : Math.PI / 2)); ctx.fillText(ch, 0, 0); ctx.restore();
          a += da;
        });
      };
      ring(top, D * 0.16, R - D * 0.105, -Math.PI / 2, false);
      ring(bottom, D * 0.072, R - D * 0.105, Math.PI / 2, true);
      ctx.font = `900 ${D * 0.3}px "Archivo Black"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('A', R, R + D * 0.02);
      return { texture: canvasTexture(c), widthMm: diameterMm, heightMm: diameterMm };
    });
  }

  // The wordmark as a transparent decal. Returns the texture and its size in mm, with the baseline 1.0 em from the top.
  function wordmark({ text = 'earmilk', sizeMm, color, trackingEm = -0.035, pxPerMm = 8 }) {
    return memo(`wm|${text}|${sizeMm}|${color}|${trackingEm}`, () => {
      const fontPx = sizeMm * pxPerMm;
      const c = document.createElement('canvas');
      let ctx = c.getContext('2d');
      ctx.font = `${fontPx}px "Archivo Black"`;
      ctx.letterSpacing = `${trackingEm * fontPx}px`;
      const w = Math.ceil(ctx.measureText(text).width + fontPx * 0.1);
      c.width = w; c.height = Math.ceil(fontPx * 1.3);
      ctx = c.getContext('2d');
      ctx.font = `${fontPx}px "Archivo Black"`;
      ctx.letterSpacing = `${trackingEm * fontPx}px`;
      ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = color;
      ctx.fillText(text, fontPx * 0.05, fontPx * 1.0);
      return { texture: canvasTexture(c), widthMm: c.width / pxPerMm, heightMm: c.height / pxPerMm };
    });
  }

  // The engraved Nutrition Facts panel, 266 x 240 mm plus the footnote that sits below the frame (copy/label.md).
  function engravedLabel({ color = '#6B5232', pxPerMm = 4 } = {}) {
    return memo(`label|${color}`, () => {
      const W = 266, H = 262;
      const c = document.createElement('canvas');
      c.width = W * pxPerMm; c.height = H * pxPerMm;
      const ctx = c.getContext('2d');
      const mm = v => v * pxPerMm;
      ctx.fillStyle = color; ctx.strokeStyle = color;
      ctx.lineWidth = mm(1.2);
      ctx.strokeRect(mm(0.6), mm(0.6), mm(W - 1.2), mm(240 - 1.2));
      const x0 = mm(14), x1 = mm(W - 14);
      const rule = (y, thick) => ctx.fillRect(x0, mm(y - thick / 2), x1 - x0, mm(thick));
      const fit = (text, font, maxW) => { let size = font.size; for (;;) { ctx.font = `${font.weight || ''} ${size}px "${font.family}"`.trim(); if (ctx.measureText(text).width <= maxW || size < 4) return; size *= 0.97; } };
      ctx.textBaseline = 'alphabetic';
      ctx.letterSpacing = `${-0.02 * mm(34)}px`;
      fit('Nutrition Facts', { size: mm(34), family: 'Archivo Black' }, x1 - x0);
      ctx.fillText('Nutrition Facts', x0, mm(44));
      ctx.letterSpacing = '0px';
      rule(54, 1.4); rule(78, 7.6);
      const rows = [['Sensitivity', '91 dB'], ['Frequency response', '32 Hz to 20 kHz'], ['Impedance', '8 ohm'], ['Woofer', '12 in'], ['Midrange', '6.5 in'], ['Tweeter', '1 in']];
      rows.forEach(([k, v], i) => {
        const base = 104 + 22 * i;
        ctx.font = `700 ${mm(12)}px "Archivo"`; ctx.textAlign = 'left'; ctx.fillText(k, x0, mm(base));
        ctx.font = `400 ${mm(12)}px "Archivo"`; ctx.textAlign = 'right'; ctx.fillText(v, x1, mm(base));
        rule(111 + 22 * i, 1.4);
      });
      ctx.textAlign = 'left';
      rule(232, 7.6);
      ctx.font = `400 ${mm(11)}px "Archivo"`; ctx.fillText('Contains no milk.', x0, mm(254));
      return { texture: canvasTexture(c), widthMm: W, heightMm: H };
    });
  }

  // Vertical gradient for the bowl: UV v = 0 at the mouth, 1 at the throat (the canvas top row is v = 1).
  function gradient(mouth, throat) {
    return memo(`grad|${mouth}|${throat}`, () => {
      const c = document.createElement('canvas'); c.width = 4; c.height = 256;
      const ctx = c.getContext('2d');
      const g = ctx.createLinearGradient(0, 0, 0, 256);
      g.addColorStop(0, throat); g.addColorStop(1, mouth);
      ctx.fillStyle = g; ctx.fillRect(0, 0, 4, 256);
      return canvasTexture(c);
    });
  }

  function rand(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  // Birch face: #EAD8B0 with soft vertical grain.
  function birch({ base = '#EAD8B0', streaks = ['#DFCB9E', '#E4D2A9', '#D5BE8F', '#CFB686'], size = 1024, seed = 7 } = {}) {
    return memo(`birch|${base}|${size}|${seed}`, () => {
      const c = document.createElement('canvas'); c.width = size; c.height = size;
      const ctx = c.getContext('2d'); const r = rand(seed);
      ctx.fillStyle = base; ctx.fillRect(0, 0, size, size);
      for (let i = 0; i < 260; i++) {
        const x = r() * size, w = 1 + r() * 5, len = size * (0.2 + r() * 0.8), y0 = r() * size - len / 2;
        ctx.strokeStyle = streaks[Math.floor(r() * streaks.length)];
        ctx.globalAlpha = 0.12 + r() * 0.3; ctx.lineWidth = w;
        ctx.beginPath();
        const amp = 2 + r() * 6, f = 0.004 + r() * 0.01, ph = r() * 7;
        for (let y = y0; y < y0 + len; y += 6) ctx.lineTo(x + Math.sin(y * f + ph) * amp, y);
        ctx.stroke();
      }
      ctx.globalAlpha = 0.06;
      for (let i = 0; i < 4000; i++) { ctx.fillStyle = r() > 0.5 ? '#B89C6E' : '#FFF6DC'; ctx.fillRect(r() * size, r() * size, 2, 1 + r() * 8); }
      ctx.globalAlpha = 1;
      return canvasTexture(c, { repeat: [1, 1] });
    });
  }

  // Floor planks: a 1.2 m square tile, planks run along the canvas y (world depth). Colors per room.
  function planks({ base, dark, light, plankW = 0.15, tile = 1.2, size = 2048, seed = 3 }) {
    return memo(`planks|${base}|${dark}|${light}|${seed}`, () => {
      const c = document.createElement('canvas'); c.width = size; c.height = size;
      const ctx = c.getContext('2d'); const r = rand(seed);
      const pw = size * plankW / tile, n = Math.round(tile / plankW);
      for (let i = 0; i < n; i++) {
        const x = i * pw;
        let y = -r() * size * 0.5;
        while (y < size) {
          const len = size * (0.5 + r() * 0.6);
          const mix = r();
          ctx.fillStyle = mix < 0.22 ? dark : mix < 0.44 ? light : base;
          ctx.fillRect(x, y, pw, len);
          ctx.globalAlpha = 0.1;
          for (let k = 0; k < 40; k++) { ctx.fillStyle = r() > 0.5 ? dark : light; const gx = x + r() * pw; ctx.beginPath(); for (let yy = y; yy < y + len; yy += 24) ctx.lineTo(gx + Math.sin(yy * 0.01 + k) * 1.5, yy); ctx.lineWidth = 0.6 + r() * 1.6; ctx.strokeStyle = ctx.fillStyle; ctx.stroke(); }
          ctx.globalAlpha = 1;
          ctx.fillStyle = 'rgba(0,0,0,0.22)'; ctx.fillRect(x, y + len - 2, pw, 2);
          y += len;
        }
        ctx.fillStyle = 'rgba(0,0,0,0.22)'; ctx.fillRect(x, 0, 2, size);
      }
      return canvasTexture(c, { repeat: [1, 1] });
    });
  }

  // Radial falloff for contact shadows: white at the centre to black at the edge (used as an alphaMap).
  function radialShadow() {
    return memo('radialShadow', () => {
      const c = document.createElement('canvas'); c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
      g.addColorStop(0, '#ffffff'); g.addColorStop(0.35, '#b0b0b0'); g.addColorStop(0.7, '#303030'); g.addColorStop(1, '#000000');
      ctx.fillStyle = g; ctx.fillRect(0, 0, 256, 256);
      return canvasTexture(c, { srgb: false });
    });
  }

  // End grain for the cut edges of crate boards: tight dark arcs on a tan base.
  function endGrain() {
    return memo('endGrain', () => {
      const c = document.createElement('canvas'); c.width = 512; c.height = 512;
      const ctx = c.getContext('2d'); const r = rand(21);
      ctx.fillStyle = '#c9ad82'; ctx.fillRect(0, 0, 512, 512);
      ctx.strokeStyle = '#8f7149';
      for (let i = 0; i < 90; i++) { ctx.globalAlpha = 0.25 + r() * 0.4; ctx.lineWidth = 1 + r() * 2; ctx.beginPath(); ctx.arc(256 + (r() - 0.5) * 80, 700, 180 + i * 5.5 + r() * 3, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
      ctx.globalAlpha = 1;
      return canvasTexture(c, { repeat: [1, 1] });
    });
  }

  // The "Have you heard me?" side panel: headline, a halftone portrait placeholder, and rows the owner chooses.
  function heardPanel({ headline = 'HAVE YOU HEARD ME?', rows = [['NAME', '[YOUR NAME]'], ['HEARD SINCE', '[DATE]'], ['LAST HEARD', '[YOUR ROOM]'], ['IF HEARD, CALL', '[YOUR NUMBER]']], ink = '#000000', W = 300, H = 330, pxPerMm = 4, seed = 5 } = {}) {
    return memo(`heard|${headline}|${JSON.stringify(rows)}|${ink}|${W}|${H}`, () => {
      const c = document.createElement('canvas'); c.width = W * pxPerMm; c.height = H * pxPerMm;
      const ctx = c.getContext('2d'); const mm = v => v * pxPerMm; const r = rand(seed);
      ctx.fillStyle = ink; ctx.strokeStyle = ink; ctx.textBaseline = 'alphabetic';
      ctx.lineWidth = mm(3); ctx.strokeRect(mm(1.5), mm(1.5), mm(W - 3), mm(H - 3));
      const fit = (text, family, weight, maxSize, maxW) => { let size = maxSize; for (;;) { ctx.font = `${weight} ${mm(size)}px "${family}"`; if (ctx.measureText(text).width <= maxW || size < 4) return; size *= 0.97; } };
      ctx.letterSpacing = '0px';
      fit(headline, 'Archivo Black', '400', 30, mm(W - 28));
      ctx.textAlign = 'center'; ctx.fillText(headline, mm(W / 2), mm(40)); ctx.textAlign = 'left';
      ctx.fillRect(mm(14), mm(49), mm(W - 28), mm(2.2));
      // Portrait placeholder: a halftone bust, lit from the upper left.
      const px0 = 14, py0 = 62, pw = 125, ph = 152;
      ctx.lineWidth = mm(1.5); ctx.strokeRect(mm(px0), mm(py0), mm(pw), mm(ph));
      const cx = px0 + pw / 2, headY = py0 + 52, headR = 30, shY = py0 + ph + 8, shRx = 62, shRy = 52;
      const inside = (x, y) => {
        if (y > py0 + ph - 1 || x < px0 + 1 || x > px0 + pw - 1) return false;
        const h = ((x - cx) ** 2) / (headR ** 2) + ((y - headY) ** 2) / ((headR * 1.12) ** 2) <= 1;
        const neck = Math.abs(x - cx) < 11 && y > headY && y < shY;
        const sh = ((x - cx) ** 2) / (shRx ** 2) + ((y - shY) ** 2) / (shRy ** 2) <= 1 && y > headY + 20;
        return h || neck || sh;
      };
      const pitch = 4.2;
      for (let y = py0 + 3; y < py0 + ph - 2; y += pitch) for (let x = px0 + 3; x < px0 + pw - 2; x += pitch) {
        if (!inside(x, y)) continue;
        const lx = (x - (cx - 22)), ly = (y - (headY - 26));
        const shade = Math.max(0.12, Math.min(1, 0.25 + Math.hypot(lx, ly) / 95 + (r() - 0.5) * 0.12));
        ctx.beginPath(); ctx.arc(mm(x), mm(y), mm(pitch * 0.5 * shade), 0, Math.PI * 2); ctx.fill();
      }
      // Rows: label over value, stacked on the right.
      const rx0 = px0 + pw + 14, rw = W - 14 - rx0;
      rows.slice(0, 4).forEach(([k, v], i) => {
        const y = py0 + 16 + i * 36;
        ctx.font = `700 ${mm(8.5)}px "Archivo"`; ctx.letterSpacing = `${mm(0.6)}px`; ctx.fillText(String(k).toUpperCase(), mm(rx0), mm(y));
        ctx.letterSpacing = '0px';
        fit(String(v), 'Archivo', '400', 12.5, mm(rw)); ctx.fillText(String(v), mm(rx0), mm(y + 15));
        ctx.fillRect(mm(rx0), mm(y + 20), mm(rw), mm(0.8));
      });
      // Footer rule and a line of small type.
      ctx.fillRect(mm(14), mm(H - 56), mm(W - 28), mm(2.2));
      ctx.font = `400 ${mm(9)}px "Archivo"`; ctx.fillText('Printed to order. Any flavor, any face.', mm(14), mm(H - 36));
      ctx.font = `400 ${mm(9)}px "Archivo"`; ctx.fillText('[YOUR LINE]', mm(14), mm(H - 20));
      return { texture: canvasTexture(c), widthMm: W, heightMm: H };
    });
  }

  return { wordmark, engravedLabel, gradient, birch, planks, radialShadow, endGrain, heardPanel, canvasTexture, label, dotText, roundel, barcode };
}
