// Prints the derived numbers and fails if they drift from spec/geometry.md.
import { FS, derived, slopePoint } from './spec.mjs';

const d = derived(FS);
const b = FS.bowl;
const s0 = b.mouthCenterS - b.mouthLength / 2, s1 = b.mouthCenterS + b.mouthLength / 2;
const lower = slopePoint(FS, s0), upper = slopePoint(FS, s1), centre = slopePoint(FS, b.mouthCenterS);
const apexY = FS.tweeter.faceplateY - FS.tweeter.apexForward;
const deg = r => r * 180 / Math.PI;
const angFrom = (y, p) => deg(Math.atan2(p.z - FS.tweeter.z, y - p.y));
const rows = [
  ['slope panel length', d.slope.toFixed(1), '246.0'],
  ['slope angle (deg)', deg(d.angle).toFixed(1), '37.6'],
  ['ridge z', d.ridgeZ, '1010'],
  ['overall height', d.total, '1055'],
  ['mouth lower lip (y, z)', `${lower.y.toFixed(1)}, ${lower.z.toFixed(1)}`, '15.9, 872.2'],
  ['mouth centre (y, z)', `${centre.y.toFixed(1)}, ${centre.z.toFixed(1)}`, '62.6, 908.2'],
  ['mouth upper lip (y, z)', `${upper.y.toFixed(1)}, ${upper.z.toFixed(1)}`, '109.4, 944.1'],
  ['pattern from apex, lower (deg)', (-angFrom(apexY, lower)).toFixed(1), '17.2'],   // 12.1 before 2026-10-08 (the tweeter at 170)
  ['pattern from apex, upper (deg)', angFrom(apexY, upper).toFixed(1), '79.4'],   // 37.7 before
  ['throat bottom above body top', (FS.tweeter.z - b.throat / 2 - FS.body).toFixed(1), '6.5'],   // 10.5 before
  ['internal gross volume (L)', (((FS.plan - 2 * FS.wall) ** 2 * (FS.body - 2 * FS.wall)) / 1e6).toFixed(1), '103.3'],
];
let bad = 0;
for (const [name, got, want] of rows) {
  const ok = String(got) === want;
  if (!ok) bad++;
  console.log(`${ok ? 'ok  ' : 'DRIFT'} ${name.padEnd(34)} ${String(got).padEnd(14)} spec ${want}`);
}
if (bad) { console.error(`${bad} value(s) drift from spec/geometry.md`); process.exit(1); }
