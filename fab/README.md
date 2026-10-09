# Fabrication

Everything needed to have earmilk made, in two sizes, from one file of numbers (`params.py`): the **floorstander**, a
three-way, and the **bookshelf**, its two-way little sibling. Both are active: a Hypex FusionAmp plate amplifier in
the back drives each driver from its own channel, and its DSP is the crossover. Change a number, run `build.sh`, and
every cut file, model, drawing, chart and the renders' model follow. `fab/out/` holds the floorstander,
`fab/out-bookshelf/` the bookshelf.

The outside is the spec (`spec/geometry.md`; the bookshelf is the same carton at 0.564 scale with its own plinth and
type sizes). What is inside, and how it goes together, is this folder's **proposal**, marked `PROPOSAL` in `params.py`;
the bought parts' sizes are the research's, marked `PLACEHOLDER` until the parts are in hand.

![The roof in section: the waveguide insert, the tweeter rear-mounted on it, the connector bay and the cable down to the amplifier](../renders/2026-10-08/engine/08b-final.png)

## The two speakers

| | Floorstander | Bookshelf |
|---|---|---|
| Size | 390 x 390 mm, 1,055 tall | 220 x 220 mm, 594 tall |
| Ways | three, active | two, active |
| Woofer | Dayton Audio RSS315HF-4, 12 in, in 81 L vented to 32 Hz (port 171 mm): f3 about 28 Hz | SB Acoustics SB17NRX2C35-8, 6.5 in, in 9.2 L sealed: f3 63 Hz, a DSP shelf takes it to 45 Hz |
| Mid | SB Acoustics Satori MR16P-8, 6.5 in, in its own 7.6 L sealed chamber | none |
| Tweeter | SB Acoustics Satori TW29DN-B, its faceplate off, rear-mounted on the waveguide insert | Scan-Speak Illuminator D3004/602200, its 62 mm faceplate on the insert's back |
| Waveguide | C22: throat 176 behind the face, 935 up; holds about +-40 degrees horizontally from 2 to 8 kHz | BkD: throat 95 behind the face, 517 up; about +-56 degrees at 2.5 kHz, +-32 from 6.3 kHz |
| Amplifier | Hypex FusionAmp FA253: 250 + 250 + 100 W into 4 ohm, DSP, on its side across the back's foot | Hypex FusionAmp FA122: 2 x 125 W into 4 ohm, DSP, upright on the back |
| Crossovers | 300 Hz and 2.8 kHz, Linkwitz-Riley 24 dB/octave | 2.4 kHz, Linkwitz-Riley 24 dB/octave |
| Wood | 24.9 kg of 18 mm Baltic birch | 6.2 kg |
| Drivers and amplifier, the pair | about $2,520 | about $1,330 |

The figures are simulations and datasheets (below); measure the built speakers before printing the Facts.

## Read this before ordering anything

- **Measure the bought parts first.** Every cutout, rebate and the tweeter's counterbore comes from the research
  (`research/`), which could not open the makers' drawings from this environment: the TW29DN-B's size with its
  faceplate off, the woofers' flanges, the FusionAmps' screw patterns. Buy one of each, measure, edit `params.py`, run
  `build.sh`. The CAD checks its own clearances on every build (`cad.json`, "checks") and stops if a change makes two
  parts collide.
- **The Facts' "8 ohm" and "91 dB" mean nothing on an active speaker.** Its inputs are line level, so impedance and
  sensitivity are not the buyer's business. The bookshelf's Facts already say power and inputs instead; the
  floorstander's should too (an owner's decision).
- **The floorstander's port runs out of air at full power.** At the amplifier's full 250 W near 30 Hz the port's air
  reaches about 50 m/s and will chuff; at a loud 100 dB it is 12 m/s and silent. Set the DSP's high-pass at about
  25 Hz and its limiter to the woofer's excursion.
- **The bookshelf's bass shelf costs excursion.** Its +8.3 dB shelf to 45 Hz needs a 35 Hz high-pass in the DSP.
- **Print the waveguide insert fine.** Its walls are the acoustic surface the simulation was run on: 0.1 mm layers or
  finer (SLA resin, or MJF nylon), filled and sanded smooth before the paint.
- **The wordmark is 172 mm wide** at the spec's 44 mm type size (the spec says "about 155"); say if 155 matters and
  the type shrinks to 39.6 mm.

## The build, in order

The two sizes are built the same way; only the numbers differ. Drawings: `out*/drawings/earmilk-sheets.pdf`, five
A3 sheets per size: (1) the general arrangement, (2) the centre section, (3) the waveguide insert and the tweeter's
mount and wiring, (4) the back, the amplifier and the wiring, (5) the assembly.

1. **Prove the tweeter and its waveguide (a weekend).** Print the gable (`stl/gable-print/`: four pieces for the
   floorstander, one for the bookshelf) and the insert (`stl/waveguide-insert.stl`; the floorstander's also comes in
   halves, `-left` and `-right`, for a 256 mm printer). Mount the tweeter on the insert (sheet 3), set the gable on a
   box of the right plan, and measure on the axis and every 15 degrees horizontally and vertically with a calibrated
   USB microphone and REW. Compare with `out*/acoustics/waveguide/*-polar.png`. If it holds, carry on; the
   simulation's levers are the throat's depth and height (`WAVEGUIDE` in `params.py`, then `bem.py`).
2. **Buy the drivers and the amplifier** (`bom.csv`) and check each against `params.py` before any wood is cut.
3. **Cut the panels.** `out*/dxf/` to a local CNC cabinet or sign shop or a makerspace ShopBot: front, back, two
   sides, top, bottom, the amplifier box's floor, lid and front; the floorstander adds the window brace and the mid
   chamber's shelf and divider. Each DXF layer names its operation (through cuts, the 3 mm shadow-line and rebate
   pockets, the drivers' and amplifier's rebates). No instant online service cuts 18 mm plywood.
4. **Glue up the box.** Front and back run the full width; the sides sit between them; everything else sits inside.
   Glue (Titebond II or III), clamp, square. Cut the shadow lines across the front and back panels' edges at the side
   corners and round the four vertical corners (6 mm on the floorstander, 4 on the bookshelf). The amplifier's box
   goes in before the top: its floor, front and lid between the sides, sealed, with the gland in its lid.
5. **Make the gable.** Laminated birch (`dxf/gable-layer-*.dxf`), CNC-milled to `step/gable-block.step`: the insert's
   pocket is a prism along the depth, so it mills from the front face with the block on its back. Or printed
   (`stl/gable-print/`), filled and painted. Round the hips and the fin's edges. Glue it on four 10 mm dowels.
6. **Run the tweeter's cabinet lead** (sheets 3 and 4) before the insert goes in: from the amplifier box's gland,
   through the brace's window (floorstander, 30 mm in from its back edge), up the 14 mm channel through the top panel
   and the gable block to the socket of a two-pole locking connector (JST VH), 250 mm past the grommet (100 on the
   bookshelf); seal the grommet under the top panel.
7. **Fit the insert** (sheet 3). Heat-set M3 x 5.7 inserts in the seat round the throat; the tweeter in from behind
   through its bore, its flange on a 0.5 mm gasket on the seat, screwed to the inserts; the magnets in the insert's back
   and their partners in the pocket's back wall, opposite poles out; the two pins pressed in. Plug its 120 mm lead into
   the cabinet's socket and slide the insert home.
8. **Wire the woofer and the mid** (sheet 4) to the same gland, the drivers on 1.5 mm foam gaskets in their rebates,
   M4 button heads into T-nuts (sheet 1), the trim rings over them. Seal the gland: the woofer's box must be airtight,
   and the insert's pocket is open to the room through its 0.3 mm seam. **The amplifier**: its module goes through the
   back's cutout into its sealed box, the plate on 3 mm EPDM tape flush in its 4.5 mm rebate, ten 4.3 x 25 screws in
   pilot holes drilled to Hypex's drawing.
9. **Finish.** Fill the grain and edges, 2K high-build primer, block flat, the body colour everywhere, mask the marks
   with the vinyl stencils (`out*/marks/`), the accent colour on the plinth and gable, peel; then the Nutrition Facts
   (`marks/facts-print.pdf`, on the back of the floorstander and the right side of the bookshelf) as a screen print in
   a 2K ink or a water-slide decal, and 2K clear over everything, flatted until the print's edge disappears. The
   insert is painted with the gable; the trim rings satin black.
10. **Metal.** The letters (`metal/wordmark-letters.dxf`, 1.5 mm stainless or aluminium, polished; four sets of
    eight pieces a pair) glued on with the 1:1 templates (`metal/wordmark-template-*.pdf`).
11. **Tune it** (`out*/dsp/*.md`). Load the channels and crossovers into Hypex Filter Design over USB, then measure
    each driver on the tweeter's axis at 1 m (REW, a UMIK-1), set levels and delays from the measurements, check the
    reverse null at each crossover, and EQ the sum flat on axis. The files' numbers are where to start.

## Files and who gets them

| File (in `out/` and `out-bookshelf/`) | What | Goes to |
|---|---|---|
| `step/earmilk-*.step` | the whole speaker, every part in place | anyone, any CAD program |
| `dxf/*.dxf`, `dxf/sheet-*.dxf`, `dxf/sheets.svg` | flat panels, one per file, layers by operation; nested sheets | CNC shop or makerspace |
| `cutlist.csv` | every panel, size and operation for a pair | the shop, and you |
| `step/gable-block.step`, `dxf/gable-layer-*.dxf` | the gable: the milled block and its glue-up layers | CNC millwork or pattern shop |
| `stl/gable-print/` | the gable for printing | a printer |
| `stl/waveguide-insert*.stl`, `step/waveguide-insert.step` | the insert with the waveguide, the tweeter's counterbore, magnet and pin holes | SLA or MJF service, or CNC |
| `stl/port-*.stl` | the floorstander's port, two pieces | a printer |
| `drawings/earmilk-sheets.pdf` | the five A3 drawings, from the same solids | the builder |
| `acoustics/waveguide/` | the waveguide study: candidates, polar maps, the choice | you |
| `dsp/*.md`, `dsp/*.json` | the DSP's starting setup: channels, crossovers, delays, levels, EQ | you, at Hypex Filter Design |
| `acoustics.json`, `acoustics/` | the box: volumes, port, simulated response | you |
| `marks/facts-print.pdf`, `marks/stencil-*.svg` | the Facts at 1:1; vinyl masks for the two marks | a screen printer or decal paper; a sign shop or Cricut |
| `metal/` | the letters and their 1:1 templates | SendCutSend, OSHCut, Xometry |
| `render/` (not in git) | the renders' model, one named part each (`render_model.py`) | the studio engine |
| `../bom.csv` | parts for a pair, both sizes, prices and sources | you |
| `../research/` | the sourcing research behind every bought part | you, before ordering |

## Proposals (not decisions)

None of these changes the outside; each is a choice someone had to make.

- **Joinery:** butt joints, plain 2D cuts any shop can make.
- **The waveguide insert:** the waveguide is a separate printed part in a pocket in the roof, so the waveguide's
  surface can be made finer than milled birch and the tweeter can be serviced: it slides out level, like a drawer,
  held by four magnets and located by two pins, with the tweeter on it and its lead unplugging at a connector in a bay
  behind it.
- **The amplifier's box:** FusionAmps are not airtight, so each module sits in its own sealed box of three 18 mm
  panels behind the plate, its leads out through a gland. In the bookshelf it also does the brace's job.
- **The floorstander's mid chamber:** a shelf and a divider close a 7.6 L sealed box behind the mid.
- **The brace:** one window brace in the floorstander (z 500); none in the bookshelf (above).
- **The drivers flush:** each frame in a rebate as deep as its flange plus a 3 mm printed trim ring over its screws,
  the ring level with the finish.
- **The bookshelf's Facts on its right side,** as on a real carton, because its back holds the amplifier.

## Acoustics

**The woofers.** From the solids, the floorstander's woofer chamber holds 85.1 L of air after the inside panels, the
port and the amplifier's box; less the driver, 81.1 L net. The RSS315HF-4 vented there at 32 Hz simulates to an f3
of 28 Hz at 90.7 dB/2.83 V (Dayton quotes 90.3). The bookshelf's 9.5 L is 9.2 L net: the SB17NRX2C35-8 sealed in it
has fc 73 Hz at Qtc 0.83 and f3 63 Hz, and a Linkwitz transform in the DSP moves the corner to 45 Hz (+8.3 dB).
`acoustics.py`, results in `out*/acoustics.json`.

**The waveguides.** The tweeter's waveguide is shaped for how it spreads sound, not for its looks: a boundary-element
simulation (`bem.py`, bempp-cl) of each candidate in the roof of the whole cabinet, at frequencies from 1 to 10 kHz,
for the horizontal and vertical response and the directivity index (`wg_study.py` compares candidates; `wg_polar.py`
draws the maps). The roof's slope tips the sound upward below about 2 kHz in the floorstander and 3.5 kHz in the
bookshelf; a deeper, higher throat brings control lower, and tipping the axis down did nothing. Each size crosses
where its waveguide's directivity comes nearest the cone below it and the listening axis is within about 1 dB of the
loudest direction: 2.8 kHz in the floorstander, 2.4 kHz in the bookshelf. Details:
`out/acoustics/waveguide/README.md` and `out-bookshelf/acoustics/waveguide/README.md`.

![Floorstander waveguide](out/acoustics/waveguide/C22-polar.png)
![Bookshelf waveguide](out-bookshelf/acoustics/waveguide/BkD-polar.png)

The simulation treats the tweeter as a flat piston across its dome and surround, which beams more than a dome does;
the on-axis fall above the crossover (about 7 dB to 10 kHz in the floorstander) is mostly that, and the DSP's shelf
takes out what the measurement shows. The TW29DN-B's 96.5 dB against the mid's 88 dB leaves 8.5 dB for it.

The insert's CAD is a ruled loft through the wall's meridians. Below the axis the coverage is narrowed so that every
wall meets the roof above the eave, which puts a crease in the wall (at 205 and 335 degrees in the floorstander, 199 and 341 in the bookshelf) and makes
neighbouring walls very different in length where the sides turn into the floor. A meridian lies on each crease and
more are added wherever neighbours differ by over 2 mm (`Waveguide.phis`: 256 in the floorstander, 160 in the
bookshelf); with 96 evenly spaced, the quads between
them twisted into a sawtooth along both creases, small on a print and plain in a gloss coat.

## The crossover (active, a starting point)

`dsp.py` writes each size's starting setup from the geometry and the datasheets (`out*/dsp/`):

| | Floorstander: woofer / mid / tweeter | Bookshelf: woofer / tweeter |
|---|---|---|
| crossovers | 300 Hz, 2.8 kHz, LR4 | 2.4 kHz, LR4 |
| acoustic centre behind the front | 53 / 32 / 172 mm | 32 / 91 mm |
| delay to start | 0.347 / 0.407 / 0 ms | 0.173 / 0 ms |
| gain to start | -2.3 / 0 / -8.5 dB | 0 / -3.5 dB |
| woofer EQ | -3.3 dB at 37 Hz, Q 1.2 (the vented bump) | Linkwitz transform, 73 Hz Q 0.83 to 45 Hz Q 0.71 |

## Rough budget, the pair

Drivers and amplifiers: about $2,520 for the floorstanders ($1,294 of FusionAmps, $1,224 of drivers), about $1,330
for the bookshelves ($844 and $484). The rest (birch, CNC, printing, finish, metal, hardware) from the services
research: about $1,700 doing most of it yourself up to about $9,900 with everything outsourced for the floorstanders;
roughly a third of that for the bookshelves. Add the measurement kit (about $110 for a UMIK-1). `bom.csv` has the
lines.

## Regenerating

The CAD tools need numpy 2 and Blender's `bpy` needs numpy 1, so the CAD tools live in their own environment:

    python3 -m venv .venv-fab && .venv-fab/bin/pip install -r fab/requirements.txt
    fab/build.sh                      # both sizes; SIZES=bookshelf fab/build.sh for one
    EARMILK_SIZE=bookshelf .venv-fab/bin/python fab/cad.py     # any one step, for one size

`build.sh` runs, per size: `cad.py` (solids, STEP, STL, volumes, the clearance checks), `acoustics.py` (the box;
the floorstander's port settles in two passes with the CAD), `dsp.py` (the crossover's starting setup), `flats.py`
(DXF, nesting, cut list), `typeset.py` (letters, the Facts, stencils, templates), `sheets.py` (the drawings) and
`render_model.py` (the engine's model). The waveguide study is separate and slow (minutes per frequency):
`bem.py --throat Y Z --r0 R ...`, then `wg_study.py` and `wg_polar.py`.

## Checks the files pass

Every build checks, on the solids: the insert above the top panel and with material under the tweeter's counterbore,
birch over the connector bay, the drivers' rebates clear of each other and of the shadow lines, the amplifier's plate
clear of the plinth's shadow line and inside the back, the port clear of the amplifier's box, the box clear of the
brace (`cad.json`, "checks"; a failure stops the build).

The floorstander: overall 1,055; ridge 1,010; body 860; slope 246 at 37.6 degrees; fin 45 x 8; plinth 110 with the
groove at 110 to 113 and the gable's at 857 to 860; corners and hips R6, the fin R3; woofer at z 320, mid at 690;
the waveguide's mouth 279 wide, the insert 283; the Facts 266 x 260, top at z 770; port 100 at z 405; the FA253's
plate 360 x 135 at z 185. The bookshelf: overall 594, body 484, plinth 62, R4 and R2, the woofer at z 380, the mouth
156 wide and the insert 159, the Facts 150 x 147 on the right side, the FA122's plate 120 x 315 at z 235. All from
`params.py`, which follows `spec/geometry.md`; where they disagree, the spec wins.
