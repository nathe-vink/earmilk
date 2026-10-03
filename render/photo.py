#!/usr/bin/env python3
"""Photoreal pass: send a rendered frame to Google's Gemini image model and keep the result beside it.

The frame is the control image; the prompt is the shot's text-to-image paragraph from prompts/ under the constant block,
plus an instruction to keep every shape where it is. The key is read from IMAGE_API_KEY or from the file named by
IMAGE_API_KEY_FILE; it is never written anywhere by this script.

    python3 render/photo.py --shots 01,04 --variants 2 --date 2026-10-03 [--model gemini-3.1-flash-image] [--v 11]
"""
import argparse, base64, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
KEEP = ("Treat the attached image as the exact layout: keep every object, edge, proportion, position and camera angle precisely where "
        "it is, including the carton's silhouette, the gable, the fin, the drivers, the plinth and the lettering. Change only the light "
        "and the materials so that it reads as a photograph: satin lacquer on the cabinet, real paper cones and rubber surrounds, "
        "cast metal letters, a real floor and walls with grain and bounce light, soft contact shadows, a plausible camera lens. "
        "Do not add, remove or move anything. Do not add text. Output one image at the same framing as the input.")

def key():
    k = os.environ.get('IMAGE_API_KEY')
    if not k and os.environ.get('IMAGE_API_KEY_FILE'):
        k = Path(os.environ['IMAGE_API_KEY_FILE']).read_text().strip()
    if not k:
        sys.exit('no key: set IMAGE_API_KEY or IMAGE_API_KEY_FILE')
    return k

def constant_block():
    s = (REPO / 'prompts' / 'README.md').read_text()
    m = re.search(r'^> (A floorstanding speaker.*?)$', s, re.M)
    am = re.search(r'^\*Amended 2026-10-02 \(v6 on\): (.*?)\*$', s, re.M)
    later = re.search(r'\*Later the same day: (.*?)\*', s)
    return m.group(1).strip() + ' ' + (am.group(1).strip() if am else '') + ' ' + (later.group(1).strip() if later else '')

def shot_paragraph(nn, v):
    files = sorted((REPO / 'prompts').glob(f'shot-{nn}-v*.md'), key=lambda p: int(p.stem.split('-v')[1]))
    f = next((p for p in files if p.stem.endswith(f'-v{v}')), files[-1])
    s = f.read_text()
    m = re.search(r'## Text-to-image form\n(.*?)\n\n## ', s, re.S)
    text = m.group(1).strip() if m else ''
    return re.sub(r'^Constant block, then:\s*', '', text), f.name

def frames(nn, v, date_in):
    d = REPO / 'renders' / date_in
    return sorted(d.glob(f'shot-{nn}-v{v}*.png'))

def call(model, k, prompt, png_bytes, timeout=180):
    body = {
        'contents': [{'parts': [
            {'inline_data': {'mime_type': 'image/png', 'data': base64.b64encode(png_bytes).decode()}},
            {'text': prompt},
        ]}],
        'generationConfig': {'responseModalities': ['IMAGE', 'TEXT']},
    }
    req = urllib.request.Request(ENDPOINT.format(model=model), data=json.dumps(body).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def images_from(resp):
    out = []
    for cand in resp.get('candidates', []):
        for part in cand.get('content', {}).get('parts', []):
            inline = part.get('inlineData') or part.get('inline_data')
            if inline and inline.get('data'):
                out.append((inline.get('mimeType') or inline.get('mime_type') or 'image/png', base64.b64decode(inline['data'])))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shots', default='01,02,03,04,05,06')
    ap.add_argument('--v', default='11')
    ap.add_argument('--date-in', default='2026-10-02')
    ap.add_argument('--date', default=time.strftime('%Y-%m-%d'))
    ap.add_argument('--variants', type=int, default=1)
    ap.add_argument('--model', default='gemini-3.1-flash-image')
    ap.add_argument('--extra', default='')
    a = ap.parse_args()
    k = key()
    const = constant_block()
    out_dir = REPO / 'renders' / a.date; out_dir.mkdir(parents=True, exist_ok=True)
    for nn in [s.strip().zfill(2) for s in a.shots.split(',')]:
        para, pfile = shot_paragraph(nn, a.v)
        prompt = f'{const}\n\n{para}\n\n{KEEP}' + (f'\n\n{a.extra}' if a.extra else '')
        for frame in frames(nn, a.v, a.date_in):
            for i in range(a.variants):
                suffix = chr(ord('A') + i)
                target = out_dir / f'{frame.stem}-photo-{suffix}.png'
                t0 = time.time()
                try:
                    resp = call(a.model, k, prompt, frame.read_bytes())
                except urllib.error.HTTPError as e:
                    msg = e.read().decode(errors='replace')[:300]
                    print(f'{frame.name} {suffix}: http {e.code} {msg}', flush=True); continue
                imgs = images_from(resp)
                if not imgs:
                    txt = ' '.join(p.get('text', '') for c in resp.get('candidates', []) for p in c.get('content', {}).get('parts', []))[:200]
                    print(f'{frame.name} {suffix}: no image returned; {resp.get("promptFeedback", "")} {txt}', flush=True); continue
                mime, data = imgs[0]
                if mime != 'image/png':
                    tmp = target.with_suffix('.' + mime.split('/')[-1]); tmp.write_bytes(data)
                    os.system(f'convert "{tmp}" "{target}" && rm -f "{tmp}"')
                else:
                    target.write_bytes(data)
                print(f'{target.relative_to(REPO)}  {time.time() - t0:.1f}s  prompt from {pfile}', flush=True)

if __name__ == '__main__':
    main()
