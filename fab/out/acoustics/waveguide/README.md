# The tweeter's waveguide, by simulation (2026-10-08)

The owner, 2026-10-08: what matters for the tweeter is that it disperses sound correctly, and its shape should be
optimised for that whatever it looks like. So the bowl that was drawn for looks is replaced by a waveguide designed
and checked by simulation.

## What was simulated

- **The shape** (`fab/waveguide.py`). The wall follows the oblate-spheroidal profile (Geddes's OS waveguide, in the
  form the Ath tools use).
  - The throat is matched to the dome and its surround (r0 15 mm).
  - The wall leaves the throat at 12 degrees and opens to 45 degrees horizontally, 35 up and 30 down.
  - The roof's 37.6 degree slope cuts the mouth at an angle. Each direction's wall therefore runs until it meets the
    roof, and the downward walls are narrowed until they meet it at least 15 mm above the eave.
  - The mouth is rounded into the roof on a 12 mm radius, tangent to the wall and to the roof, so it doesn't
    diffract.
- **The sound field** (`fab/bem.py`).
  - Method: a boundary-element model (bempp-cl, Burton–Miller, direct solve).
  - The model: the whole gable (both slopes, the gable ends, the fin) on a 250 mm stub of the cabinet. Every surface
    is rigid, and a piston at the throat stands in for the dome.
  - The mesh is fine at the waveguide and coarse elsewhere, at least six elements per wavelength at the mouth.
  - The solver was checked against the pulsating sphere's exact answer.
- **The comparison** (`fab/wg_study.py`). The 6.5 in mid it crosses to is modelled as a rigid piston of its
  effective area (118 cm²) in an infinite baffle.

## Candidates

All share the profile; they differ in where the throat sits (mm behind the front face, and height of the axis):

| | Throat y, z | Mouth (wide, up the slope) | Notes |
|---|---|---|---|
| A | 125, 903.5 | 207, 12 to 137 | where the owner put the tweeter for looks (2026-10-08) |
| B | 150, 925 | 236, 13 to 171 | |
| B6 | as B, axis tipped 6 degrees down | | |
| C | **176, 935** | 281, 13 to 194 | **chosen** |
| C6 | as C, axis tipped 6 degrees down | | |

## Results

Half-angles are to −6 dB from the horizontal (the seated listener's axis). DI is the directivity index. "Peak" is the
vertical angle of the loudest direction. The full table is in `study.md` and the curves in `study.png`.

| f | mid: H, DI | A: H, DI, peak | B: H, DI, peak | C: H, DI, peak |
|---|---|---|---|---|
| 1.25 kHz | >90, 4.4 | 79, 4.4, +70 | >90, 2.1, +60 | >90, 1.8, +45 |
| 2 kHz | 80, 6.6 | 74, 3.6, **+30** | 52, 7.0, +20 | 40, 8.6, +15 |
| 3.15 kHz | 39, 11.0 | 43, 8.3, +20 | 42, 9.7, +15 | 42, 10.7, +15 |
| 5 kHz | 23, 14.8 | 37, 11.0, +10 | 37, 12.2, +5 | 35, 12.8, 0 |
| 8 kHz | 15, 19.0 | 34, 12.6, +5 | 36, 12.9, 0 | 38, 12.7, 0 |

How far the listening axis sits below the loudest direction (dB):

| | 2 kHz | 3.15 kHz | 5 kHz |
|---|---|---|---|
| A | **4.0** | 2.0 | 1.1 |
| B | 1.5 | 0.9 | 0.1 |
| C | 0.4 | 0.8 | 0 |

## What it says

- **The roof tips the sound upward.** The mouth lies in a slope that faces 52 degrees up. Below the frequency where
  the walls take control, the tweeter radiates as if set in that slope and beams up.
- **A deeper, higher throat makes longer walls, which take control lower down.**
  - A, the owner's position, beams 30 degrees up at 2 kHz with the listening axis 4 dB down: a dip in the response
    exactly where the tweeter meets the mid.
  - C keeps the axis within 0.8 dB of the peak from 2 to 8 kHz.
  - C holds about ±40 degrees horizontally from 2 to 8 kHz: constant directivity.
- **Tipping the axis down does nothing useful.** B6 and C6 differ from B and C by less than the mesh can resolve. The
  mouth's geometry, not the axis, decides where the sound goes.
- **The crossover.** C's directivity meets the mid's near 2.8 kHz in both measures (horizontal half-angle about 43
  degrees, DI about 10.5 dB). So the DSP crossover belongs at about 2.8 kHz (B's would be about 2 kHz). A 6.5 in mid
  crossed at 2.8 kHz is within normal practice, and a 1 in dome loaded by a waveguide is comfortable there.

## C22: C for the chosen tweeter

The tweeter is now chosen: SB Acoustics' Satori TW29DN-B with its faceplate off (fab/research/drivers-floorstander.md),
a 29 mm dome on an 8 mm surround, about 45 mm across. So the throat's radius r0 is 22.5 (C had 15): the wall runs on
from the surround with no flat ring. C22 is C with that throat; C22a8 tried the wall leaving it at 8 degrees instead of
12 and changed nothing that matters, so C22 stands. Then C22 was run densely, eleven frequencies from 1 to 10 kHz:

| f | H half-angle | up / down | DI | loudest vertically |
|---|---|---|---|---|
| 1 kHz | 82 | - / 46 | 3.2 | +45 |
| 1.25 kHz | - | - / 63 | 2.3 | +45 |
| 1.6 kHz | 63 | 71 / 61 | 6.1 | +40 |
| 2 kHz | 40 | 50 / 47 | 8.7 | +15 |
| 2.5 kHz | 40 | 43 / 32 | 9.4 | +10 |
| 3.15 kHz | 41 | 34 / 30 | 11.2 | +10 |
| 4 kHz | 33 | 25 / 31 | 12.5 | +5 |
| 5 kHz | 32 | 17 / 27 | 13.4 | 0 |
| 6.3 kHz | 36 | 15 / 24 | 13.3 | 0 |
| 8 kHz | 31 | 16 / 19 | 14.2 | 0 |
| 10 kHz | 28 | 10 / 19 | 15.2 | 0 |

![C22's polar maps](C22-polar.png)

Read the maps the way a designer does: straight, parallel -6 dB lines (the black ones) mean the pattern holds. C22's
horizontal lines are nearly straight at about +-40 degrees from 2 to 4 kHz and +-30 above; below 1.6 kHz they flare,
which is where the slope takes over and the sound tips up (the vertical map's dark upper corner). The crossover at
2.8 kHz sits inside the controlled band with an octave to spare, and the DSP's 24 dB/octave slope keeps the tweeter
out of the uncontrolled region below it.

## Decision and consequences

- **The throat is C22:** 176 mm behind the front face, the axis at 935, r0 22.5 (`params.WAVEGUIDE`).
- **The mouth** is 279 wide and runs from 13 mm above the eave to 52 mm below the ridge.
- **The waveguide is a separate insert** (`params.INSERT`, `cad.waveguide_insert()`, drawing sheet 3):
  - The tweeter screws to the insert's back (rear mount): its flange sits in a 73.4 x 6.2 counterbore behind the
    throat, and its dome and surround fill the 45 mm throat.
  - The insert slides out forward, level, like a drawer, with the tweeter on it; four 12 x 4 magnets hold it and two
    6 mm pins locate it.
  - The tweeter's 120 mm lead plugs into the cabinet's lead in a 36 mm bay behind the insert's boss; that lead runs
    down a 14 mm channel through the gable block and the top panel, sealed by a grommet, to the amplifier.
  - The seam runs round the mouth just outside the lip, and along the eave where the mouth comes near it.
- **For the owner.** The mid's centre (z 690) is 245 mm below the tweeter's axis, two wavelengths at 2.8 kHz. That
  puts the first vertical nulls about 14 degrees above and below the listening axis. Raising the mid to z 760 (the
  highest its frame allows under the gable's shadow line) widens that to about 20 degrees. The geometry is the
  owner's, so this is a proposal, not a change.

## Still to do

- Measure one TW29DN-B with its faceplate off; if its diaphragm is not 45 mm across, set r0 and re-run C22.
- Measure the printed insert with a calibrated microphone (fab/README.md, step 1) against `C22-polar.png`.
