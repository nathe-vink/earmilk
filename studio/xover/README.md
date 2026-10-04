# xover: passive crossover design

```
.venv-fab/bin/python studio/xover/xover.py design.json --optimize --out out/xover
```

A design is a JSON file with four parts (earmilk's is written by `fab/crossover.py`; open `fab/out/xover/design.json`
for a full example):

- **`drivers`**, by name. Either measurements, `"frd": "woofer.frd", "zma": "woofer.zma"` (SPL and phase at 2.83 V on
  the listening axis; impedance; a file without phase gets minimum phase), or Thiele-Small parameters (`Re`, `Le_mH`,
  `Fs`, `Qms`, `Qes`, `Vas_l`, `Sd_cm2`) with a `box` (`infinite`, `sealed` with `Vb_l`, or `vented` with `Vb_l`, `fb`,
  `QL`), plus `baffle_mm` for the baffle step and `hf: [f, Q]` for cone breakup and beaming. A tweeter with only
  datasheet numbers takes `Fs`, `Qts`, `sens_db`, `Re`, `Le_mH`. Every driver has a position: `z_mm` (height),
  `offset_mm` (acoustic centre behind the front face), `x_mm`, and a `polarity`.
- **`listener`**: `distance_mm` and `height_mm`. Delays come from the geometry, so a tweeter set 170 mm back in a bowl
  arrives 0.37 ms late at a seated listener, and the fit has to deal with it.
- **`network`**: elements `{"id", "type": R|L|C|driver, "nodes": [a, b], "value"}` in ohm, mH, uF. `in` is the amplifier
  (2.83 V), `0` is ground. Inductors take `awg` (DCR follows from it) or `dcr`; capacitors may take `esr`. Mark a part
  `"fixed": true` to keep it out of the fit.
- **`targets`**: `level_db`, the band the sum must hold flat (`sum_band`), the impedance floor (`z_min`, `z_weight`),
  how far a part may move from its start (`range`, a factor), and per way `lp` and/or `hp` with `order` and `align`
  (`LR` or `BW`), the band to fit (`from`, `to`) and a `weight`.

What it does: solves the network by nodal analysis at 480 frequencies; multiplies each driver's response by the
voltage the network leaves across it, its polarity and its delay; sums; fits the free parts in log space with
`scipy.optimize.least_squares` (each way to its target, the sum to flat, the impedance above the floor); snaps to E12
capacitors, E24 resistors and 0.05 or 0.1 mH inductors; and writes `response.png` and `.pdf`, `parts.csv` and
`design-out.json`.

What it is not: a substitute for measuring. Fit the network that gets built to each driver measured in its own box
(gated FRD on the listening axis, ZMA), check it off axis, and listen. A miniDSP or any DSP lets you audition the
target before winding a single inductor.
