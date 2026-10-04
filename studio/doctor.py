#!/usr/bin/env python3
"""Checks that every tool in the repo actually works, not just that it is installed. Run after studio/setup.sh:

    python3 studio/doctor.py

Each check runs the real thing at a tiny size: Chromium draws WebGL 2, Blender's Cycles renders a cube, build123d
builds and exports a solid, HarfBuzz shapes the wordmark with the repo's font, the crossover simulator solves a
network, and the earmilk spec check passes.
Exits non-zero if anything fails.
"""
import os, shutil, subprocess, sys, tempfile, textwrap, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PY = ROOT / '.venv-fab' / 'bin' / 'python'
CHROMIUM = os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium')


def run(cmd, cwd=ROOT, timeout=180, env=None):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env={**os.environ, **(env or {})})
    return p.returncode, (p.stdout + p.stderr).strip(), time.time() - t0


def check_chromium():
    js = textwrap.dedent(f"""
        import {{ chromium }} from 'playwright-core';
        const b = await chromium.launch({{ executablePath: '{CHROMIUM}', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }});
        const p = await b.newPage();
        const ok = await p.evaluate(() => !!document.createElement('canvas').getContext('webgl2'));
        await b.close(); console.log(ok ? 'webgl2' : 'no-webgl2');
    """)
    f = ROOT / 'render' / '.doctor-check.mjs'
    f.write_text(js)
    try:
        code, out, dt = run(['node', str(f)], cwd=ROOT / 'render')
    finally:
        f.unlink(missing_ok=True)
    return code == 0 and 'webgl2' in out and 'no-webgl2' not in out, out.splitlines()[-1] if out else '', dt


def check_bpy():
    py = textwrap.dedent("""
        import bpy, numpy
        assert numpy.__version__.startswith('1.'), numpy.__version__
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.preferences.addon_enable(module='cycles')
        bpy.ops.mesh.primitive_cube_add()
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.scene.collection.objects.link(cam)
        cam.location = (4, -4, 3); cam.rotation_euler = (1.1, 0, 0.785); bpy.context.scene.camera = cam
        s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.samples = 4; s.cycles.device = 'CPU'
        s.render.resolution_x = s.render.resolution_y = 32; s.render.filepath = '/tmp/doctor-cycles.png'
        bpy.ops.render.render(write_still=True); print('cycles', bpy.app.version_string)
    """)
    code, out, dt = run(['python3', '-c', py])
    return code == 0 and 'cycles' in out, [l for l in out.splitlines() if l.startswith('cycles')][-1:] or out[-200:], dt


def check_cad():
    py = textwrap.dedent(f"""
        import tempfile, os
        from build123d import Box, Cylinder, export_step
        part = Box(20, 20, 20) - Cylinder(5, 30)
        p = os.path.join(tempfile.gettempdir(), 'doctor.step'); export_step(part, p)
        import ezdxf, uharfbuzz, matplotlib; matplotlib.use('Agg')
        import sys; sys.path.insert(0, r'{ROOT / 'studio'}')
        from typeset import Font, set_line
        c, w = set_line(Font('ArchivoBlack-Regular.woff'), 'earmilk', 44.0, -0.035, 0, 0)
        print(f'cad ok, volume {{part.volume:.0f}} mm3, wordmark {{w:.1f}} mm')
    """)
    if not VENV_PY.exists():
        return False, f'{VENV_PY} missing: run studio/setup.sh', 0.0
    code, out, dt = run([str(VENV_PY), '-c', py])
    return code == 0 and 'cad ok' in out, out.splitlines()[-1] if out else '', dt


def check_xover():
    py = textwrap.dedent(f"""
        import sys; sys.path.insert(0, r'{ROOT / 'studio' / 'xover'}')
        import xover, numpy as np
        d = {{'drivers': {{'w': {{'Re': 6.0, 'Le_mH': 1.0, 'Fs': 24, 'Qms': 2, 'Qes': 0.4, 'Vas_l': 150, 'Sd_cm2': 500,
                                'box': {{'type': 'sealed', 'Vb_l': 60}}}}}},
             'network': [{{'id': 'L1', 'type': 'L', 'nodes': ['in', 'a'], 'value': 2.0, 'dcr': 0.3}},
                         {{'id': 'W', 'type': 'driver', 'driver': 'w', 'nodes': ['a', '0']}}]}}
        s = xover.simulate(d)
        k = np.argmin(abs(s['f'] - 100)); print(f'xover ok, {{xover.spl(s["sum"])[k]:.1f}} dB at 100 Hz')
    """)
    code, out, dt = run([str(VENV_PY), '-c', py])
    return code == 0 and 'xover ok' in out, out.splitlines()[-1] if out else '', dt


def check_spec():
    code, out, dt = run(['npm', 'run', '--silent', 'check'], cwd=ROOT / 'render')
    bad = [l for l in out.splitlines() if l.startswith('FAIL') or l.startswith('fail')]
    return code == 0 and not bad, f'{sum(1 for l in out.splitlines() if l.startswith("ok"))} spec checks ok' + (f', {len(bad)} failed' if bad else ''), dt


def main():
    checks = [('Chromium + WebGL 2 (real-time renders)', check_chromium), ('Blender Cycles via bpy (path tracing)', check_bpy),
              ('CAD venv: build123d, ezdxf, HarfBuzz', check_cad), ('crossover simulator (studio/xover)', check_xover),
              ('earmilk spec check (render/)', check_spec)]
    failed = 0
    for name, fn in checks:
        try:
            ok, detail, dt = fn()
        except Exception as ex:  # a check that crashes is a failed check
            ok, detail, dt = False, repr(ex), 0.0
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'}  {name:42s} {dt:5.1f}s  {detail if isinstance(detail, str) else ' '.join(detail)}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
