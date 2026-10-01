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

  return { wordmark, engravedLabel, gradient, birch, planks, radialShadow, endGrain, canvasTexture };
}
