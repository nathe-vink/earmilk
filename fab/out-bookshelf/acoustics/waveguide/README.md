# The bookshelf's waveguide, by simulation (2026-10-08)

The same method as the floorstander's (`fab/out/acoustics/waveguide/README.md`): the oblate-spheroidal wall cut by the
roof's 37.6 degree slope (`fab/waveguide.py`), the whole gable on a 150 mm stub of the cabinet in a boundary-element
model (`fab/bem.py`), every surface rigid, a piston at the throat for the dome. The bookshelf is the floorstander's
carton at 0.564 scale, so its roof, and with it the waveguide's mouth, is 0.564 the size: everything the floorstander's
waveguide does at 2 kHz, this one does near 3.5 kHz.

## Candidates

| | Throat y, z | r0 | Tweeter | Mouth (wide, up the slope) |
|---|---|---|---|---|
| BkD | **95, 514** | 17 | **Scan-Speak Illuminator D3004/602200** (26 mm dome, 62 mm faceplate) | 161, 8 to 101 |
| BkE | 100, 524 | 15 | a faceplate-less 25 mm element (Dayton ND25FN-4 class) | 155, 9 to 113 |

Both: the wall leaving the throat at 4 degrees (the throat is small against the roof, so a gentle start leaves room
for the mouth), coverage 45 degrees horizontally, 35 up and 30 down, the mouth's lowest point at least 10 mm up the
slope from the eave, a 7 mm lip.

## Results

| f | BkD: H half-angle, DI, loudest | axis below loudest (dB) | BkE: H half-angle, DI, loudest | axis below loudest (dB) |
|---|---|---|---|---|
| 1.6 kHz | >90, 1.9, +50 | 5.5 | 78, 3.3, +45 | 4.1 |
| 2.5 kHz | 56, 5.8, +55 | 0.8 | 80, 4.2, +45 | 2.8 |
| 4 kHz | 47, 7.4, +20 | 2.5 | 43, 8.4, +15 | 1.4 |
| 6.3 kHz | 32, 11.4, +10 | 0.8 | 36, 11.8, +10 | 0.9 |
| 10 kHz | 32, 13.0, +5 | 0.3 | 33, 13.5, 0 | 0.0 |

![BkD's polar maps](BkD-polar.png)

## What it says

- **The small roof steers late.** Below about 3.5 kHz both candidates radiate as if set in the slope, whose face looks
  52 degrees up, so their loudest direction is 45 to 55 degrees up. But the upward lobe is broad: at 2.5 kHz BkD's
  listening axis is only 0.8 dB below it, so the response on the axis stays smooth.
- **BkD is the better of the two.** At 2.5 kHz it holds +-56 degrees horizontally with the axis 0.8 dB below the
  loudest direction; BkE spreads to +-80 degrees with the axis 2.8 dB down. From 4 kHz they are alike.
- **The crossover.** A 6.5 in cone's directivity (the SB17NRX2C35-8's 118 cm2 as a piston) rises faster than this
  waveguide's, so the two never quite meet; the gap is smallest, about 2.5 dB of DI, around 2.2 to 2.5 kHz, where
  BkD's axis is also within about 1 dB of its loudest direction. So the bookshelf crosses at 2.4 kHz. Higher would
  widen the directivity gap; lower would put the tweeter where the slope, not the waveguide, aims it.

## Decision and consequences

- **The throat is BkD,** with the Illuminator D3004/602200: 95 mm behind the front face, r0 17 (`params.py`, the
  bookshelf block). The axis is at 517 in the CAD, 3 mm above the simulated 514, so the 62 mm faceplate clears the
  top panel with 2 mm of insert under it; at 2.4 kHz and above that is under a fiftieth of a wavelength.
- **The insert** is the floorstander's in small: 159 wide, the faceplate screwed to its back in a 62.4 x 4.7
  counterbore, four 8 x 3 magnets and two 4 mm pins, the lead into a 26 mm connector bay and down a 14 mm channel.
- **For the owner.** If the bookshelf's waveguide must control lower (a lower crossover, closer to the woofer's
  directivity), the lever is size: a wider plan makes a bigger roof and mouth. At 260 mm instead of 220 the control
  would reach about 18 % lower.

## Still to do

- Measure the printed insert with a calibrated microphone (fab/README.md, step 1) against `BkD-polar.png`.
- If a denser polar map is wanted, run BkD at 1, 1.25, 2, 3.15, 5 and 8 kHz too (`bem.py`, about ten minutes each).
