# earmilk siblings: drivers and electronics for the bookshelf and the pint

Researched 2026-10-08. Companion data file: `drivers-small.json` (same folder), which holds every figure, the box simulations for each width, per-field confidence notes and the source URLs.

**Read this first**
- Pages could not be opened directly (WebFetch and curl were blocked). Every figure is a search-engine extract of the maker datasheet or retailer page listed under Sources. Check the drawing before you cut.
- "unconfirmed" means the figure came from one place only, was derived by me, or was read off an unlabelled drawing. Everything else agreed in at least two places.
- Box numbers are my own Thiele-Small calculations (sealed box; Small's vented box with leakage QL = 7). "DSP boost" is the low-frequency shelf a Linkwitz transform needs to reach the target f3 at Q 0.707.
- The shared search budget ran out before the Dayton RS180/RS180P-8A could be checked, so neither is covered.
- Prices are snapshots, often months old. Some products showed out of stock.

---

## The four sets at a glance

| Size | Set | Woofer | Tweeter | Amplifier | Box | Drivers + amp |
|---|---|---|---|---|---|---|
| Bookshelf, W 220 | **Recommended** | SB Acoustics **SB17NRX2C35-8** (171 mm) | Scan-Speak **Illuminator D3004/602200** (62 mm faceplate) | Hypex **FusionAmp FA122** | Sealed 10.1 L net, f3 62.5 Hz, +7.6 dB DSP shelf to 45 Hz | about USD 650-700 per speaker |
| Bookshelf, W 220 | **Budget** | Dayton **RS150P-8A** (150 mm); SB15NRX2C30-8 is a same-size upgrade | Dayton **ND25FN-4** element (41 mm) | Dayton **KABD-250** board | Vented 13.6 L, fb 50 Hz, port 35 x 57 mm, f3 51 Hz | about USD 155 per speaker, plus one USD 38 programmer |
| Pint | **Recommended** | Dayton **ND65-4** (64 mm) | SB Acoustics **SB14ST-C000-4** (24 mm face) | Dayton **KABD-430** (or Wondom JAB4): one per pair, three per crate | Sealed 1.3 L, f3 104 Hz, +4.9 dB to 80 Hz | about USD 24 + EUR 28 per pint; USD 70-90 per pair amp |
| Pint | **Budget** | Dayton **ND65-4** run full-range | Dayton **ND16FA-6** via one capacitor, or none | Two KABD-430 / JAB4 per crate (6 of 8 channels) | Same sealed 1.3 L | about USD 35 per pint |

---

## 1. Geometry that drives the choices

Assumptions: square plan W; body 2.2 W; roof rise 0.385 W (the flagship's 37.6 degree pitch); solid gable block not counted as air; 18 mm birch with separate top and bottom panels; net = gross x 0.95 - driver - port - 3.5 L when a Hypex plate needs its own sealed compartment (the sibling amp research, `amps.md`, puts that compartment at 3.5-4 L).

| W (mm) | Body (mm) | Roof rise (mm) | Slope length (mm) | Inside (mm) | Gross (L) | Net with FA122 (L) | Net with a board amp (L) |
|---|---|---|---|---|---|---|---|
| 200 | 440 | 77 | 126 | 164 x 164 x 404 | 10.9 | 6.0 | 9.6 |
| 220 | 484 | 85 | 139 | 184 x 184 x 448 | 15.2 | 10.1 | 13.6 |
| 240 | 528 | 92 | 151 | 204 x 204 x 492 | 20.5 | 15.2 | 18.6 |
| 250 | 550 | 96 | 158 | 214 x 214 x 514 | 23.5 | 18.1 | 21.5 |

The pint (100 mm square, 220 mm body) holds 1.79 L gross with 4 mm printed walls, 1.61 L with 6 mm ply and 1.36 L with 9 mm ply. Design for **about 1.3 L net**.

**Roof waveguide constraints (important for the tweeter choice).**
- The mouth is about 0.5 W wide: 110 mm at W 220, 125 mm at W 250, 50 mm on the pint.
- If the tweeter axis is horizontal, or only slightly tilted, the slope cuts the waveguide obliquely. The effective mouth height is then only about 0.61 x the length available along the slope: about 74 mm at W 220, 84 mm at W 250 and 34 mm on the pint. The waveguide becomes an ellipse, about 110 x 74 mm at W 220.
- The roof is only 0.385 W tall (85 mm at W 220). A 100-104 mm faceplate standing upright cannot sit wholly inside it.
- Keep the woofer high. At W 220, a 171 mm frame 12 mm below the eave and a tweeter 30% up the slope sit about 127 mm apart, centre to centre. That is under one wavelength at 2.2 kHz (156 mm), which is acceptable.

---

## A. Bookshelf woofers

Box results are for W 220 with the FA122 compartment (10.0-10.3 L net). "Vented" is the best flat alignment in the same volume. With a board amp the same carton gives about 13.6 L (see section E).

| Woofer | Frame / cutout / depth behind baffle (mm) | Fixing | Fs / Qts / Vas / Xmax | Sens. (2.83 V) | Price | W 220 result | Verdict |
|---|---|---|---|---|---|---|---|
| **SB Acoustics SB17NRX2C35-8** (8 ohm) | 171 / 144.9 (unconfirmed) / 75; 85.9 overall (unconfirmed) | 4 x 4.3 on 159 PCD; 6.5 mm flange (unconfirmed) | 36.5 Hz / 0.42 / 27 L / 5.5 mm | 87 dB | USD 76.70 Madisound | Sealed fc 70 Hz, Qtc 0.80, f3 62.5 Hz; vented needs 15 L or more | **Recommended** (sealed + DSP at W 220; vented at W 240-250) |
| **SB Acoustics SB15NRX2C30-8** (8 ohm) | 150 / 123.9 / 68.3; 78.9 overall | 4 x 4.3 on 138 PCD (unconfirmed) | 36.5 Hz / 0.34 / 20 L / 5.0 mm | 86.5 dB | USD 68 Madisound; CAD 93.33 Solen | Vented fb 43 Hz, port 35 x 129 mm, f3 48 Hz | Best vented fit at W 200-220 |
| **Dayton RS150P-8A** (8 ohm, paper) | 150 / 122 / 74 overall | n/f | 47.1 Hz / 0.34 / 16.7 L / 4.0 mm | 88.7 dB (Dayton) | USD 54.98 PE (44.52 for 4+) | Vented fb 53 Hz, port 35 x 73 mm, f3 58 Hz | **Budget** |
| Scan-Speak Revelator 15W/8530K00 (8 ohm) | 148 / 125 / 77 overall | 5 x 5-5.3 on 136 PCD (unconfirmed) | 39 Hz / 0.39 / 16 L / 6.5 mm (maker page); retailers list 30 / 0.27 / 27.4 | 86 dB | USD 237.80 Madisound | Vented fb 43 Hz, 41 x 178 mm port, f3 46 Hz | Premium; check which T/S set your units match |
| Seas Prestige L16RN-SL / H1480-08 (8 ohm, aluminium) | 146 / 126 / 76 overall (listings range 65.5-76) | n/f | 37 Hz / 0.45 / 19 L / 6.0 mm | 84 dB (basis n/f) | USD 148.60 Madisound | Sealed Qtc 0.76, f3 58 Hz | Proven sealed + DSP (LXmini) |
| Purifi PTT6.5X04-NFA-01 (4 ohm) | 176 / 145 / 90.2 overall | 6 x 5.1 on 166 PCD (unconfirmed) | 30 Hz / 0.27 / 25.9 L / 10 mm | n/f | USD 535 Madisound; EUR 355 ex VAT | Sealed Qtc 0.51; vented needs a 50 x 305 mm port | Overkill for a proof of concept |
| Dayton RS150-8 (aluminium) | 150 / 122 / 74 (unconfirmed) | six-hole frame | 47.8 Hz / 0.34 / 16.6 L / 4.0 mm | about 89 dB | EUR 80-83 (no US price found) | As RS150P-8A | Paper version preferred for a 2.5-3 kHz crossover |
| SB Acoustics SB16PFCR25-8 | dimensions unconfirmed (sibling listings give 160 or 176 frame) | n/f | 38 Hz / 0.40 / 27 L / 4.5 mm | n/f | n/f | Sealed Qtc 0.76 | Dropped: no reliable drawing |
| Scan-Speak 18W/8531G00 (7 in) | 182 / 156 (unconfirmed) / 78-83 | n/f | 28 Hz / 0.36 / 58.2 L / 6.5 mm | 87 dB | GBP 160-192 | W 250 only; sealed Qtc 0.74, f3 55 Hz | Too big except at W 250 |
| Scan-Speak Discovery 15W/8434G00 | n/f | n/f | 45 Hz / 0.25 / 12.8 L / 4.2 mm | n/f | EUR 70 / GBP 51 ex VAT | No flat alignment at 10-20 L; its B4 box is only about 3.6 L with f3 about 81 Hz (Keele estimate); sealed is overdamped | Dropped: wrong Qts for this volume, no drawing |

Notes
- **Why the SB17 at W 220.** Its 171 mm frame is 0.78 W, the same visual ratio as the flagship (314 mm woofer on 390 mm = 0.81 W). It has Le 0.15 mH and an SB-rated range high enough for a 2-2.5 kHz crossover. At 10.1 L it is a good sealed driver: the FA122 adds +7.6 dB of shelf to reach 45 Hz. The excursion limit at 45 Hz is about 85 dB at 1 m per speaker (full space). For a vented build, go to W 240-250: 15.2-18.1 L, fb 34-36 Hz, a 35 x 99-137 mm or 41 x 142-193 mm port, f3 43-47 Hz with no boost. Madisound's own suggestion is 17 L with a 51 x 178 mm vent, f3 45 Hz. It is also the floorstander research's alternate midrange (`drivers-floorstander.md`), so the CAD model can be shared.
- **The RS150P-8A and SB15NRX2C30-8 share a 150 mm frame,** so one CAD frame model covers both. Their cutouts are 122 and 123.9 mm.
- **In 10-14 L, the Qts 0.27-0.39 drivers want a port; the Qts 0.40-0.45 drivers want sealed + DSP.** The SB15, RS150P-8A, 15W/8530K00 and Purifi vent well. The SB17, SB16PFCR25 and L16RN-SL only give flat vented alignments with very low tuning and long ports, so they are listed as sealed. The Qts 0.25 Discovery 15W suits neither.

---

## B. Bookshelf tweeter

**Answer.** Of the flagship's candidates, only the **Bliesma T25** (68 mm faceplate) leaves room for a carved flare inside a 110-150 mm mouth. The SB26STAC (100 mm), Scan-Speak D2608/913000 (104 mm), Seas 27TFFC (103.8 mm) and Dayton ND25FW-4 (104 mm) faceplates fill about 70-95% of the mouth width. With a near-horizontal axis they are also taller than the 85 mm roof at W 220.

For the bookshelf, either use a small-faceplate tweeter in a counterbore at the throat, or use a faceplate-less element so the roof forms the whole waveguide. The best fit for a true 2-2.2 kHz crossover is the **Scan-Speak Illuminator D3004/602200**: a 62 mm faceplate and Fs 440 Hz. The sibling floorstander research (`drivers-floorstander.md`) reached the same size limit for the flagship. It now recommends the SB Satori TW29DN-B with its faceplate removed, with this same D3004/602200 as the alternate, so the D3004/602200 keeps the family together.

| Tweeter | Faceplate (mm) | Cutout / depth (mm) | Fs (Hz) | Sens. | Crossover in this use | Element-only version? | Price |
|---|---|---|---|---|---|---|---|
| **Scan-Speak Illuminator D3004/602200** (4 ohm) | 62 round, black anodised; 3 fixing holes | 48-50 / about 21.5 (unconfirmed: 50 and 21.5 are the predecessor D3004/602000's, 48 is from `drivers-floorstander.md`) | 440 | 90.5 dB | LR4 2.0-2.2 kHz | No (62 mm is already the small one). Ring twin **R3004/602200**: 62 mm, Fs 420, 43 mm cutout, USD 197.20 | CAD 222.71 Solen; no US price found |
| **Bliesma T25A-6 / T25B-6** (6 ohm) | 68 round | 48 / 26 (unconfirmed) | A-6 980 declared (814 measured); B-6 1050 (852 measured) | 91.5 / 92.5 dB | LR4 about 2.2 kHz | No; fixed grille. HiFiCompass publishes WG104 waveguides for it | A-6 EUR 148.60; B-6 EUR 386.80 |
| **SB Acoustics SB26STCN-C000-4** (4 ohm) | 72 round | 48-50 / n/f | 960 | 92.5 dB | LR4 about 2.5 kHz (SB suggests 2.6 kHz, 12 dB) | It *is* the small sibling of the SB26STAC | USD 40.50 Madisound |
| **Dayton ND25FN-4** (4 ohm) | none (element, 41 mm body) | - / 21 | 1350 | 90 dB | LR4 2.8-3 kHz | Yes, this is the element | USD 14.99 MSRP |
| Peerless OC25SC65-04 (4 ohm) | none (41.3 mm twist-lock body) | 38.6 / 25.5 | 1382 | 93.1 dB | LR4 2.8-3 kHz | Yes; made for custom faceplates and waveguides | USD 35.20 Madisound |
| SB Acoustics SB26STAC-C000-4 (4 ohm) | 100 round, metal (88.5 PCD, unconfirmed) | 72-74 / 33.2 behind front, 39.7 overall (unconfirmed) | 750 | 91.5 dB | 2-2.5 kHz possible | Use SB26STCN. Waveguide twin SB26STWGC-4 is also 100-104 mm | USD 52 Madisound |
| Scan-Speak Discovery D2608/913000 (8 ohm) | 104 round, die-cast | 72 / 32-38 (unconfirmed; conflict) | 700 | 91.3 dB | 2-2.5 kHz possible | None found. D2604/833000 is also 104 mm | EUR 75-104 |
| Seas Prestige 27TFFC / H0881-06 (6 ohm) | 103.8 | 85 / 42.5 overall (unconfirmed) | 550 | 91 dB | 2 kHz possible | None found. (H1189 is the 27TDFC, same frame) | EUR 70 / GBP 40 ex VAT |
| Dayton ND25FW-4 (4 ohm) | 104 waveguide faceplate | 73 (conflict) / 40 | 1350 | 91-94 dB | 2.5-3 kHz | Yes: ND25FN-4 | USD 13.98 PE |
| SB Satori TW29DN-B, faceplate removed (figures from `drivers-floorstander.md`, not re-checked) | bare body about 71-74 (unconfirmed) | pocket about 75 / about 32 (unconfirmed) | 650 (624 measured) | about 93 dB | about 2 kHz | Faceplate removable per SB | about EUR 150 |
| Seas 27TFFNC/G / H1396-04 (figures from `drivers-floorstander.md`, not re-checked) | 53 small flange | 46 / 22 (unconfirmed) | 1170 | 91 dB | 2.5-3 kHz | It is the small-flange Seas | about EUR 48 |

Keep the tweeter in the same family as whatever the flagship finally uses:

| If the flagship uses | Use on the bookshelf |
|---|---|
| SB26STAC-C000-4 | SB26STCN-C000-4 (cross at 2.5 kHz) |
| D2608/913000 | Illuminator D3004/602200 or R3004/602200 |
| 27TFFC | Seas 27TFFNC/G small flange (cross at 2.5-3 kHz), or the Illuminator for a 2 kHz crossover |
| Satori TW29DN-B (faceplate off) | the same TW29DN-B. Its 71-74 mm body fits the 85 mm roof at W 220 only near the ridge, or with the body dropping into the cabinet |
| ND25FW-4 | ND25FN-4 element |
| Bliesma T25 | the same T25 |

Two ways to mount it in the carved roof:
- **Front-mount.** Put a faceplate of 72 mm or less in a counterbore whose floor is perpendicular to the listening axis. The carved profile starts at the faceplate's edge.
- **Element.** Mill the full waveguide from a throat of about 38-41 mm, which is the best acoustic result in a mouth this small.

Measure in the finished roof whichever way you choose. The waveguide adds level at the bottom of the tweeter's range and changes its directivity.

---

## C. Pint drivers

The face is 100 mm wide and the roof scoop is about 50 mm wide. With a horizontal axis the scoop is only about 34 mm tall.

**Woofer / full-range**

| Driver | Frame / cutout / depth (mm) | Fs / Qts / Vas / Xmax | Price | Sealed 1.3 L | Verdict |
|---|---|---|---|---|---|
| **Dayton ND65-4** (4 ohm, black anodised Al cone) | 64 round / 52 / 48 overall | 89.5 Hz / 0.61 / 0.53 L (PE: 0.85 L; conflict) / 3.5 mm | USD 23.98 PE | fc 106 Hz, Qtc 0.72, f3 104 Hz; +4.9 dB to 80 Hz | **Recommended and budget** |
| SB Acoustics SB65WBAC25-4 (4 ohm, Al cone) | 64 square (corners on an 80 mm circle) / 59.5-60.5 / 32.7 behind, 38 overall; 4 x 3.8 on 72 PCD | 115 Hz / 0.68 / 0.43 L / 2.65 mm (unconfirmed) | USD 39.10 Madisound | fc 133 Hz, Qtc 0.78; +8.8 dB to 80 Hz | Alternative if you want a square frame |
| Dayton DMA70-4 | 70 / 64 / 38 (unconfirmed) | 113 Hz / 0.44 / 0.4 L (unconfirmed) / 2.0 mm | EUR 20.95 | Overdamped sealed; vented 1.0 L fb 92 Hz, 16 x 60 mm port, f3 82 Hz | Closest to the 68 mm drawn; less bass |
| Tang Band W3-881SJF (8 ohm) | 93 (unconfirmed) / 75 / 59 (unconfirmed) | 100 Hz / 0.39 / 1.89 L / 0.5 mm | USD 34.98 PE (clearance) | f3 185 Hz | Too wide for a 100 mm face; tiny Xmax |
| Tang Band W2-800SL (2 in Al-Mg) | 57 / 52 / 30 (unconfirmed, one listing) | 160 Hz / 0.25 / 0.23 L / 1 mm | clearance, n/f | f3 about 590 Hz | Not a woofer |
| Peerless TC6FD00-04 (2 in, not 2.5) | 57 x 57 square / 48 / 32 (unconfirmed) | 175 Hz / 0.98 / 0.22 L / 1 mm | EUR 12-19 | f3 145 Hz | Not a woofer |
| Markaudio Alpair 5.3 | 100 / n/f / 39 overall | 94.5 Hz / 0.50 / 1.78 L | EUR 85-99 per pair | - | Does not fit (frame = face width) |
| Dayton ND90-4 | 103.5 / 85 / 61 | 90.2 Hz / 0.63 / 1.06 L / 4 mm | USD 25.98 | - | Does not fit |

The 40 mm "mid" in the current drawing: drop it for the proof of concept. No real 40 mm unit was worth keeping, and the 2 in candidates above are 57 mm wide with poor bass.

**Micro tweeter**

| Tweeter | Face (mm) | Cutout / depth (mm) | Fs | Sens. | Price | Verdict |
|---|---|---|---|---|---|---|
| **SB Acoustics SB14ST-C000-4** (4 ohm) | 24.2 round | screwed from behind with an M4 thread (5 mm max engagement); cutout n/f; depth 19 or 37.25 (conflict: allow 38) | 1300 Hz | 86 dB (REV.3) / 87 dB | EUR 25-30 | **Recommended**: the only real dome that fits the 34 mm scoop with margin. LR4 at 3.5-4 kHz |
| **Dayton ND16FA-6** (6 ohm) | 32.5 round, front press-fit flush | 32.3-32.5 / 14.5 (unconfirmed) | 2125 Hz | 88 dB | USD 8.98 PE | **Budget**: one series cap of about 4.7 uF (about 5.6 kHz) |
| Dayton ND20FB-4 (4 ohm, rear mount) | 39.1 frame behind the panel | 35.8 hole / 19 | 2072 Hz | 90 dB | USD 12.98 PE | Good if only the dome should show through the scoop |
| Tang Band 20-2240S | 38.5 x 38.5 square | 31.6 / 38.9 overall | 850 Hz | 86 dB | listed unavailable | Single source |
| "Tang Band 25-1717" | not found; nearest is 25-1719S with a 66 mm plate | - | - | - | - | Too big |
| Peerless BC25 family | BC25TG15-04: 104 mm; BC25SC55-04: 70 mm with 54 mm flats | - | 1128 / 1401 Hz | - | - | Too big for the pint |

Pint box. Sealed is simplest. A vented ND65-4 needs a 16 mm x 103-140 mm port (fb 55-57 Hz), which is possible as a long rear or down-firing tube but fiddly in a 100 mm carton. Excursion limits 80 Hz output to about 73 dB at 1 m per pint (Sd estimated at 14.5 cm2, unconfirmed), so high-pass at 70-80 Hz. On a desk at 0.7 m with the desktop boundary, that is fine for near-field listening.

---

## D. Amplification

| Amplifier | Channels | DSP | Size / cutout | Supply | Price | Bookshelf | Crate of six |
|---|---|---|---|---|---|---|---|
| **Hypex FusionAmp FA122** | 2 x 125 W/4 ohm (75 W/8 ohm); bridged 200 W/4 or 250 W/8 | ADAU1450, IIR + FIR, 3 presets; HFD software (Windows) | Plate 315 H x 120 W x 55 D; recess **291 x 96** (Audiophonics drawing says 293); 815 g | Mains 100-120/200-240 V | EUR 425.92 incl. VAT; USD 397 ex VAT (KJF); USD 422.40 (PE listing) | **Recommended** | No |
| Hypex FusionAmp FA123 | 2 x 125 W/4 ohm + 1 x 100 W | as FA122 | Plate 360 x 120 x 55; recess **336 x 96**; 955 g | Mains | EUR 499 | Only for a 3-way | No |
| **Dayton KABD-250** | 2 x 50 W/4 ohm at 24 V | ADAU1701 + Bluetooth 5.0; KPX programmer (USD 37.98) for SigmaStudio | Board 91.4 x 68.6 x 22.9; holes 84 x 61 centres, 3.5 mm; KABD-PMV4 panel 120 x 95 x 2.3 | 12-24 V, 4 A | USD 49.98-63.98 | **Budget** | No (2 channels) |
| Wondom JAB4 (AA-JA33285) | 4 x 30 W/8 ohm (TPA3118, 4 ohm min); 2.1 and 2.0 modes | ADAU1701 + BT 5.0; ICP5 programmer; I2S out | Board 91.4 x 68.6 x about 20 | 10-26 V (24 V typical) | EUR 54.90 | - | **Yes** (EU-stocked equivalent of the KABD-430) |
| **Dayton KABD-430** | 4 x 30 W (2 x TPA3118); 2.1 and 2.0 modes | ADAU1701 + BT 5.0; KPX programmer | Probably 91.4 x 68.6 (Dayton: "same compact size") (unconfirmed) | 12-24 V | USD 69.98-89.98 | - | **Yes: recommended, three boards = 12 channels** |
| Wondom JAB3+ (AA-JA32173) | 2 x 50 W/4 ohm | ADAU1701 + BT 5.0 | 91.44 x 68.58 | n/f | EUR 48.90 | Budget alternative | No |
| Wondom JAB5 / Dayton KABD-4100 | 4 x 100 W | ADAU1701 + BT | JAB5 122 x 91 x 40 (unconfirmed, from `amps.md`); KABD-4100 n/f | KABD-4100: 12-39 V (unconfirmed) | EUR 69.90 / USD 90-93 | Could drive a stereo pair | Yes, but more power than needed |
| Dayton DSP-408 | 4 in / 8 out processor, no amp | ADAU1701, 10-band PEQ per output | 166 x 115 x 26 | 12 V 1.5 A | USD 179.98 (unconfirmed) / EUR 219-259 | - | Yes, with two 4-channel amp boards |
| ICEpower 50ASX2SE | 2 x 50 W/4 ohm, 2 x 25 W/8 ohm | none (no input buffer) | 110 x 80 x 35 | Mains 85-264 V | USD 129.98 PE | Power-only | Bulky (three modules plus a DSP) |
| Fosi V3 / AIYIMA A20 (TPA3255) | stereo boxed amps | none (A20 has an analog 60-200 Hz high-pass) | A20 190 x 142 x 46 | 32-48 V bricks | USD 90-110 / EUR 179 | Listening tests only | No |

**Crate recommendation.** Use three Dayton KABD-430 boards (or the EU-sourced Wondom JAB4). This matches the desk pick in the sibling `amps.md`. Each board takes the same stereo signal (line, Bluetooth or chained over I2S) and runs one pint pair fully active: left and right woofer plus tweeter. Three 91 x 69 mm boards and one 24 V, 5-6.5 A brick fit in a tray about 300 x 100 x 30 mm. For passive pints, two boards (8 channels) are enough.

Hypex mounting note: Hypex advises a sealed compartment for best performance, and a forum poster notes vents top and bottom. Soundimports says the plates are not airtight. Plan a separate sealed sub-box behind the plate; the sibling `amps.md` estimates it displaces 3.5-4 L, and 3.5 L is already deducted in the net volumes above. Confirm venting in the Installation chapter of the FusionAmp User Guide R4, pages 12-13.

---

## E. The sets in detail

**Bookshelf, recommended (about USD 650-700 per speaker)**
- SB17NRX2C35-8, D3004/602200 and FA122, in W 220 x body 484 mm (18 mm birch).
- Sealed, about 10.1 L net after the 3.5 L amp compartment: fc 70 Hz, Qtc 0.80, f3 62.5 Hz. DSP low shelf +7.6 dB gives f3 45 Hz. Use LR4 at 2.0-2.2 kHz plus baffle-step EQ.
- If you widen the carton, switch to vented. W 240: about 15.2 L, fb 34 Hz, a 35 x 137 mm (or 41 x 193 mm) port, f3 47 Hz. W 250: 18.1 L, fb 36 Hz, a 41 x 142 mm port, f3 43 Hz. Neither needs boost.
- Why: it matches the flagship's woofer-to-width ratio, the tweeter makes a 2 kHz crossover safe in a small waveguide, and one plate does the crossover, EQ and power. Both drivers are also the floorstander research's alternates (mid and tweeter), so their CAD models carry over.

**Bookshelf, budget (about USD 155 per speaker plus a USD 38 KPX)**
- RS150P-8A, ND25FN-4 element and KABD-250, the board on a KABD-PMV4 panel with a 24 V 4 A supply. Everything comes from Parts Express.
- Vented, about 13.6 L (the board takes no real volume): fb 50 Hz, a 35 x 57 mm port, f3 51 Hz. Use LR4 at 2.8-3 kHz.
- Upgrade: drop in the SB15NRX2C30-8 (same 150 mm frame) and retune to fb 39 Hz with a 35 x 109 mm port, for f3 43 Hz.
- Why: the element lets the roof be the whole waveguide; the board gives a programmable crossover for about one seventh of the FA122's price.

**Pint, recommended**
- ND65-4 and SB14ST-C000-4, sealed about 1.3 L, LR4 at 3.5-4 kHz, high-pass 70-80 Hz.
- One KABD-430 (or JAB4) per stereo pair; three per crate.
- Why: the ND65-4 is the deepest-reaching driver that fits the face, and the SB14ST is the only real dome small enough for the scoop.

**Pint, budget**
- ND65-4 full-range plus an ND16FA-6 on a single capacitor (or no tweeter), one amp channel per pint, two boards per crate.
- Same 1.3 L sealed box, with the board DSP used only for EQ and the high-pass.

---

## CAD appearance notes (recommended parts)

| Part | Model it as |
|---|---|
| SB17NRX2C35-8 | Round black cast-aluminium frame, 171 mm OD, 6.5 mm flange (unconfirmed), 4 x 4.3 mm holes on a 159 mm circle. Black Norex paper cone with curvilinear profile, effective cone about 123 mm across. Black Norex dome dust cap about 46 mm across (seen on the sibling SB17NRX2L35-8, unconfirmed here). Black NBR half-roll surround sitting just inside the 145 mm cutout. Four slim double spokes and the motor sit 75 mm behind the baffle. For a flush mount, rebate the baffle 172 mm x 6.5 mm. |
| SB15NRX2C30-8 / RS150P-8A | 150 mm OD round frame. SB: 123.9 mm cutout, 68.3 mm deep, 4 holes on a 138 mm circle (unconfirmed), magnet about 100 mm across (unconfirmed), same black Norex look as the SB17. RS150P-8A: 122 mm cutout, 74 mm deep, paper cone (colour not found; check photos). |
| D3004/602200 | 62 mm round black-anodised aluminium faceplate, 26 mm dome at the centre. Cutout 50 mm and depth 21.5 mm come from its predecessor (unconfirmed). |
| ND25FN-4 | 41 mm round element, 21 mm deep, 1 in silk dome; no faceplate, so the carved throat is the visible edge. |
| FA122 | Rear plate 315 x 120 mm, 55 mm total depth, recess 291 x 96 mm, 8-10 screws. On a 220 mm rear panel it leaves 50 mm each side. |
| KABD-250 + PMV4 | Panel 120 x 95 x 2.3 mm on the rear, board 91.4 x 68.6 x 22.9 mm behind it. |
| ND65-4 | 64 mm round black steel frame, black anodised aluminium cone, rubber surround, 52 mm cutout, 48 mm deep. It leaves 18 mm margins on the 100 mm face. |
| SB65WBAC25-4 (alt.) | 64 mm square black polymer frame with corners cut on an 80 mm circle, 4 x 3.8 mm holes on a 72 mm circle, 32.7 mm behind the baffle. |
| SB14ST-C000-4 | 24.2 mm round face (Madisound lists it with a grille), held by an M4 screw from behind. Allow 38 mm of depth. |
| ND16FA-6 | 32.5 mm round press-fit face, flush; 14.5 mm deep (unconfirmed). |
| KABD-430 / JAB4 board | 91.4 x 68.6 x about 20 mm (JAB4 confirmed; KABD-430 assumed the same, unconfirmed). Three side by side in the crate floor. |

---

## Gaps to close before ordering
- Dayton RS180/RS180P-8A were not checked (search budget ran out).
- D3004/602200: no US price; cutout and depth come from its predecessor.
- KABD-430/4100 and JAB5 board dimensions were not published in what was found.
- FusionAmp venting versus a sealed compartment: read the Installation chapter.
- ND65-4 Vas (0.53 or 0.85 L) and SB14ST-C000-4 depth (19 or 37.25 mm) conflict. Measure a sample.
- Colours and finishes for the RS150P-8A, SB65WBAC25-4, Purifi and Seas units need a photo check.

---

## Sources

Flagship research (2026-10-04), the source of the Illuminator, OC25SC65-04, ND25FN-4 and BC25SC55-04 figures: `scratchpad/research-drivers.md`. Sibling files from 2026-10-08 in this folder: `drivers-floorstander.md` (TW29DN-B and 27TFFNC/G figures; the flagship's alternates) and `amps.md` (FusionAmp compartment volume, desk-amp picks).

**Bookshelf woofers**
- SB17NRX2C35-8: [SB product](https://sbacoustics.com/product/6in-sb17nrx2c35-8-norex/), [SB PDF](https://sbacoustics.com/wp-content/uploads/2020/02/6in-SB17NRX2C35-8.pdf), [LDB](https://loudspeakerdatabase.com/SB/SB17NRX2C35-8), [TLHP](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb17nrx2c35-8-impedance-8-ohm-6-inch.html), [Madisound](https://www.madisoundspeakerstore.com/approx-6-7-woofers-sb-acoustics/sb-acoustics-sb17nrx2c35-8-6-woofer-paper-cone-new-version-8-ohm/), [Solen](https://solen.ca/en/products/sb-acoustics-sb17nrx2c35-8-17cm-norex-paper-cone-woofer-8ohm), [Willys](https://willys-hifi.com/products/sb-acoustics-sb17nrx2c35-8-norex-midwoofer), [Masori](https://masori.de/en/products/sb17nrx2c35-8-en), [Soundimports](https://www.soundimports.eu/en/sb-acoustics-sb17nrx2c35-8.html), [audioXpress test of the SB17NRX2L35-8](https://audioxpress.com/article/test-bench-the-sb17nrx2l35-8-6-woofer-from-sb-acoustics-norex-product-line)
- SB15NRX2C30-8: [SB product](https://sbacoustics.com/product/5in-sb15nrx2c30-8-norex/), [SB PDF](https://sbacoustics.com/wp-content/uploads/2020/02/5in-SB15NRX2C30-8.pdf), [LDB](https://loudspeakerdatabase.com/SB/SB15NRX2C30-8), [Willys](https://willys-hifi.com/products/sb-acoustics-sb15nrx2c30-8-norex-midwoofer), [TLHP](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb15nrx2c30-8-impedance-8-ohm-5-inch.html), [Madisound](https://www.madisoundspeakerstore.com/approx-5-woofers/sb-acoustics-sb15nrx2c30-8-5-woofer-new-version/), [Solen](https://solen.ca/en/products/sb-acoustics-sb15nrx2c30-8-15cm-norex-paper-cone-midwoofer-8ohm)
- RS150P-8A: [Dayton](https://daytonaudio.com/product/1419/rs150p-8a-6-reference-paper-woofer-8-ohm), [Parts Express](https://parts-express.com/Dayton-Audio-RS150P-8A-6-Reference-Paper-Woofer-8-Ohm-295-573), [LDB](https://loudspeakerdatabase.com/Dayton/RS150P-8A), [Audiophonics](https://www.audiophonics.fr/en/woofer/dayton-audio-rs150p-8a-reference-speaker-woofer-paper-40w-8-ohm-89db-49hz-10khz-o15cm-p-8496.html)
- RS150-8: [Dayton](https://daytonaudio.com/product/98/rs150-8-6-reference-woofer-8-ohm), [LDB](https://loudspeakerdatabase.com/Dayton/RS150-8), [Soundimports](https://www.soundimports.eu/en/dayton-audio-rs150-8.html), [Masori](https://masori.de/en/products/reference-rs150-en)
- 15W/8530K00: [Scan-Speak](https://www.scan-speak.dk/product/15w-8530k00/), [LDB](https://loudspeakerdatabase.com/ScanSpeak/15W-8530K00), [Soundimports](https://www.soundimports.eu/en/scan-speak-15w-8530k00.html), [Madisound](https://www.madisoundspeakerstore.com/approx-5-woofers/scanspeak-15w/8530k-00-5-revelator-woofer-low-qts/), [Wilmslow](https://wilmslowaudio.co.uk/scanspeak-55/ss-revelator-15w-8530k00-diameter149mm), [Rumoh](https://www.rumoh.eu/speakers/woofer/woofer-5-inch/705/scan-speak-15w/8530k00), [Willys](https://willys-hifi.com/products/scanspeak-15w-8530k00-bass-midrange)
- L16RN-SL: [Seas](https://www.seas.no/index.php?option=com_content&view=article&id=96%3Ah1480-l16rn-sl&catid=44&Itemid=461), [Madisound](https://www.madisoundspeakerstore.com/approx-5-woofers/seas-prestige-l16rn-sl-h1480-5-aluminum-cone-woofer/), [Falcon](https://www.falconacoustics.co.uk/seas-l16rnsl-h1480-prestige-series.html), [Soundimports](https://www.soundimports.eu/en/seas-l16rn-sl.html), [Rumoh](https://www.rumoh.eu/speakers/woofer/woofer-6-inch/1001/seas-l16rn-sl-h1480-08), [TLHP](https://en.toutlehautparleur.com/speaker-seas-l16rn-sl-8-ohm-5-75-inch.html), [Amazon](https://www.amazon.com/Seas-Prestige-L16RN-SL-Aluminum-H1480-08/dp/B00ZYSMK60), [Linkwitz Lab](https://linkwitzlab.com/LXmini/Construction.htm)
- Purifi PTT6.5X04-NFA-01: [Madisound](https://www.madisoundspeakerstore.com/approx-6-7-woofers-purifi/purifi-audio-ptt6.5x04-nfa-01-6.5-woofer-4-ohm/), [Audiohum](https://www.audiohum.com/gb/diy-components/drivers/mid-woofer/purifi-ptt65x04-nfa-01), [Soundimports](https://www.soundimports.eu/en/purifi-ptt65x04-nfa-01.html), [Solen](https://www.solen.ca/en/products/purifi-audio-ptt65x04-nfa-01-18cm-fiber-cone-woofer), [Wavemusicshop](https://www.wavemusicshop.com/product/purifi-ptt6-5x04-nfa-01-6-5%E2%80%B3-mid-woofer-4-ohm/), [Purifi -06](https://purifi-audio.com/shop/ptt6-5x04-nfa-06-ptt6-5x04-nfa-06-1920)
- SB16PFCR25-8: [LDB](https://loudspeakerdatabase.com/SB/SB16PFCR25-8), [Willys](https://willys-hifi.com/products/sb-acoustics-sb16pfcr25-8-paper-midwoofer), [TLHP](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb16pfcr25-8-impedance-8-ohm-6-inch.html)
- 18W/8531G00: [Scan-Speak](https://www.scan-speak.dk/product/18w-8531g00/), [LDB](https://loudspeakerdatabase.com/ScanSpeak/18W-8531G00), [Falcon](https://www.falconacoustics.co.uk/scanspeak-18w-8531g00-midwoofer-revelator-range.html), [Rumoh](https://www.rumoh.eu/speakers/woofer/woofer-6.5-inch/743/scan-speak-18w/8531g00)
- 15W/8434G00: [Scan-Speak](https://www.scan-speak.dk/product/15w-8434g00/), [datasheet (Falcon)](https://www.falconacoustics.co.uk/downloads/Scanspeak/15w-8434g00.pdf), [Soundimports](https://www.soundimports.eu/scan-speak-15w8434g00.html)

**Bookshelf tweeters**
- Illuminator: [D3004/602200](https://www.scan-speak.dk/product/d3004-602200/), [Solen](https://solen.ca/en/products/scan-speak-illuminator-d3004-602200-26mm-ring-dome-tweeter), [R3004/602200](https://www.scan-speak.dk/product/r3004-602200/), [Madisound R3004](https://www.madisoundspeakerstore.com/ring-radiator-tweeters/scan-speak-r3004/602200-illuminator-ring-radiator-tweeter/)
- Bliesma: [T25B-6 datasheet](https://www.bliesma.de/Datasheet%20T25B-6.pdf), [Solen T25A-6](https://www.solen.ca/en/products/bliesma-t25a6-25mm-aluminum-magnesium-dome-tweeter), [audio-hi.fi T25A-6](https://audio-hi.fi/en/bliesma_t25a-6-p-4942.html), [Falcon T25A-6](https://www.falconacoustics.co.uk/bliesma-t25a-6.html), [Falcon T25B-6](https://www.falconacoustics.co.uk/bliesma-t25b-6.html), [HiFiCompass review](https://hificompass.com/en/reviews/bliesma-t25a-6-t25b-6-t25d-6-t25s-6), [HiFiCompass WG104](https://hificompass.com/en/projects/horn/waveguide-wg104-xx/25-bliesma-t25b-6-t25d-6-t25t-6-and-t25s-6-tweeters)
- SB26STCN / SB26STAC / SB26STWGC: [Madisound STCN](https://www.madisoundspeakerstore.com/soft-dome-tweeters-sb-acoustics/sb-acoustics-sb26stcn-c000-4-tweeter-4-ohm/), [Willys STCN](https://willys-hifi.com/products/sb-acoustics-sb26stcn-c000-4-tweeter), [TLHP STCN](https://en.toutlehautparleur.com/dome-tweeter-sb-acoustics-sb26stcn-c000-4-impedance-4-ohm-voice-coil-26-mm.html), [Solen STCN](https://solen.ca/en/products/sb-acoustics-sb26stcn-c000-4-25mm-textile-dome-neodymium-tweeter), [SB STAC](https://sbacoustics.com/product/sb26stac-c000-4/), [Madisound STAC](https://www.madisoundspeakerstore.com/sb-acoustics-soft-dome-tweeters/sb-acoustics-sb26stac-c000-4-1-textile-dome-tweeter/), [Willys STAC](https://willys-hifi.com/products/sb-acoustics-sb26stac-c000-4-tweeter), [TLHP STAC](https://en.toutlehautparleur.com/dome-tweeter-sb-acoustics-sb26stac-c000-4-impedance-4-ohm-voice-coil-26-mm.html), [audioexcite STAC](https://www.audioexcite.com/?page_id=4041), [Willys STWGC](https://willys-hifi.com/products/sb-acoustics-sb26stwgc-4-tweeter)
- Scan-Speak D2608/D2604: [D2608/913000](https://www.scan-speak.dk/product/d2608-913000/), [Willys](https://willys-hifi.com/products/scanspeak-d2608-913000-tweeter), [Wilmslow](https://wilmslowaudio.co.uk/detailed-tweeters/scanspeak-discovery-d2608913000), [Falcon](https://www.falconacoustics.co.uk/scanspeak-d2608-913000-tweeter-discovery-range.html), [audio-hi.fi](https://audio-hi.fi/index.php?main_page=product_info&products_id=169), [D2604/833000](https://www.scan-speak.dk/product/d2604-833000/), [audioXpress D2604](https://audioxpress.com/article/test-bench-scan-speak-discovery-d2604-833000-1-wide-surround-silk-dome-tweeter)
- Seas: [TLHP 27TFFC](https://en.toutlehautparleur.com/dome-tweeter-seas-27tffc-6-ohm-voice-coil-27-mm.html), [Soundimports 27TFFC](https://www.soundimports.eu/en/seas-27tffc.html), [Falcon 27TFFC](https://www.falconacoustics.co.uk/seas-27tffc-h0881-tweeter-prestige-series.html), [Seas datasheet copy](https://img.audiomania.ru/data/seas_h881-06_27tffc_3899.pdf), [Falcon 27TDFC](https://www.falconacoustics.co.uk/seas-27tdfc-h1189-tweeter-prestige-series.html), [Zaph SR71](https://zaphaudio.com/SR71.html)
- Dayton: [ND25FW-4](https://www.daytonaudio.com/product/1280/nd25fw-4-1-soft-dome-neodymium-tweeter-with-waveguide-4-ohm), [PE ND25FW-4](https://www.parts-express.com/Dayton-Audio-ND25FW-4-1-Soft-Dome-Neodymium-Tweeter-with-Wa-275-051), [Soundimports ND25FW-4](https://www.soundimports.eu/en/dayton-audio-nd25fw-4.html), [ND25FN-4](https://www.daytonaudio.com/product/1194/nd25fn-4-1-neo-silk-dome-tweeter-element-4-ohm), [PE ND25FN-4](https://www.parts-express.com/Dayton-Audio-ND25FN-4-1-Silk-Dome-Neodymium-Tweeter-Element-4-Ohm-275-053)
- Peerless OC25SC65-04: [Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-vifa/peerless-oc25sc65-04-1-textile-dome-tweeter-4-ohm/), [Tymphany PDF](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6167/OC25SC65-04.pdf)

**Pint drivers**
- ND65-4: [Dayton](https://www.daytonaudio.com/product/63/nd65-4-2-1-2-aluminum-cone-full-range-driver-4-ohm), [Parts Express](https://www.parts-express.com/Dayton-Audio-ND65-4-2-1-2-Aluminum-Cone-Full-Range-Driver-290-204), [LDB](https://loudspeakerdatabase.com/Dayton/ND65-4), [Audiophonics](https://www.audiophonics.fr/en/midrange-midbass-full-range/dayton-audio-nd65-4-speaker-driver-full-range-aluminium-15w-4-ohm-83db-85hz-20khz-o63cm-p-12827.html)
- SB65WBAC25-4: [SB product](https://sbacoustics.com/product/2-5in-sb65wbac25-4/), [SB PDF REV.4](https://sbacoustics.com/wp-content/uploads/2020/02/2%C2%BDin-SB65WBAC25-4.pdf), [REV.2 PDF (Solen)](https://solen.ca/storage/media/oKZeDiFc0PV2D1v8jcaX2QslEfxmktJKzieMPXCl.pdf), [Madisound](https://www.madisoundspeakerstore.com/approx-2-fullrange/sb-acoustics-sb65wbac25-4-2.5-aluminum-full-range/), [LDB](https://loudspeakerdatabase.com/SB/SB65WBAC25-4)
- DMA70-4: [Dayton](https://daytonaudio.com/product/1616/dma70-4-2-1-2-dual-magnet-aluminum-cone-full-range-driver-4-ohm), [LDB](https://loudspeakerdatabase.com/Dayton/DMA70-4), [Soundimports](https://www.soundimports.eu/en/dayton-audio-dma70-4.html)
- Tang Band: [W3-881SJF PE](https://www.parts-express.com/Tang-Band-W3-881SJF-3-Full-Range-Speaker-264-911), [W3-881SJF LDB](https://loudspeakerdatabase.com/TangBand/W3-881SJF), [W3-881SJF Audiophonics](https://www.audiophonics.fr/en/midrange-midbass-full-range/tang-band-w3-881sjf-speaker-driver-full-range-15w-8-ohm-88db-100hz-20khz-o-76cm-p-9397.html), [W2-800SL PE](https://parts-express.com/Tang-Band-W2-800SL-2-Aluminum-Mg-Full-Range-Speaker-Driver-264-807), [20-2240S](https://en.toutlehautparleur.com/dome-tweeter-tang-band-20-2240s-4-ohm-38-5-x-38-5-mm-front-plate-20-mm-voice-coil.html), [25-1719S](https://en.toutlehautparleur.com/dome-tweeter-tang-band-25-1719s-4-ohm-66-mm-front-plate-25-mm-voice-coil.html)
- Peerless TC6FD00-04: [LDB](https://loudspeakerdatabase.com/Peerless/TC6FD00-04), [TLHP](https://en.toutlehautparleur.com/fullrange-speaker-peerless-tc6fd00-04-4-ohm-2-24-x-2-24-inch.html), [datasheet](https://www.Lautsprechershop.de/pdf/peerless/peerless_tc6fd00_04.pdf); BC25: [BC25TG15-04 Willys](https://willys-hifi.com/products/peerless-bc25tg15-04-tweeter), [BC25SC55-04 PE](https://www.parts-express.com/Peerless-BC25SC55-04-1-Square-Frame-Tweeter-264-1024)
- Markaudio Alpair 5.3: [TLHP](https://en.toutlehautparleur.com/pair-of-fullrange-speaker-markaudio-alpair-5-3-grey-4-ohm-100-mm.html), [Masori](https://masori.de/en/collections/mitteltoner/products/alpair-5); ND90-4: [Dayton](https://daytonaudio.com/product/65/nd90-4-3-1-2-aluminum-cone-full-range-driver-4-ohm), [PE](https://www.parts-express.com/Dayton-Audio-ND90-4-3-1-2-Aluminum-Cone-Full-Range-Driver-4-290-208)
- SB14ST-C000-4: [SB PDF REV.3](https://sbacoustics.com/wp-content/uploads/2025/11/SB14ST-C000-4.pdf), [TLHP](https://en.toutlehautparleur.com/dome-tweeter-sb-acoustics-sb14st-c000-4-impedance-4-ohm-voice-coil-14-mm.html), [Willys](https://willys-hifi.com/products/sb-acoustics-sb14st-c000-4-tweeter), [Soundimports](https://www.soundimports.eu/en/sb-acoustics-sb14st-c000-4.html), [Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-sb-acoustics/sb-acoustics-sb14st-c000-4-1-tweeter-w/grille-4-ohm/)
- ND16FA-6: [Dayton](https://www.daytonaudio.com/product/59/nd16fa-6-5-8-neodymium-dome-tweeter-6-ohm), [PE](https://www.parts-express.com/Dayton-Audio-ND16FA-6-5-8-Soft-Dome-Neodymium-Tweeter-275-025), [Soundimports](https://www.soundimports.eu/nl/dayton-audio-nd16fa-6.html), [MAC forum](https://diy.midwestaudio.club/discussion/comment/25815/)
- ND20FB-4: [Dayton](https://www.daytonaudio.com/product/61/nd20fb-4-rear-mount-3-4-neodymium-dome-tweeter-4-ohm), [PE](https://www.parts-express.com/Dayton-Audio-ND20FB-4-Rear-Mount-3-4-Soft-Dome-Neodymium-Tweeter-275-035)

**Amplification**
- Hypex: [FusionAmp User Guide R4](https://www.hypex.nl/media/df/df/c2/1678368740/Fusion%20Manual%20R4.pdf), [Hypex Direct FA122](https://www.hypexdirect.com/products/fusion-amplifiers/fusionamp-fa122), [Soundimports FA122](https://www.soundimports.eu/en/hypex-fa122.html), [Audiophonics FA122](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa122-plate-ncore-amplifier-2x125w-dsp-adau1450-dac-ak4454-192khz-p-13530.html), [KJF Audio](https://kjfaudio.com/product/hypex-fusionamp-fa122/), [Wilmslow](https://wilmslowaudio.co.uk/hypex-fusion-2-way-plate-amplifiers/hypex-fusion-fa122), [Hypex FAQ: building in a Fusion amp](https://www.hypex.nl/FAQ-Hypex/Fusion-Amp-Family/I-want-to-build-in-one-of-the-Fusion-Amps-in-my-speaker-cabinets-how-to-do), [Fusion screws](https://hypex.nl/products/accessories/fastening-materials/fusion-mounting-screws), [Audiophonics FA123](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa123-plate-ncore-amplifier-2x125w-1x100w-dsp-adau1450-dac-ak4454-192khz-p-13531.html), [Soundimports FA123](https://www.soundimports.eu/en/hypex-fa123.html), [PE FA123](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA123-Mono-3-Way-Plate-Amplifier-2-x-250W-75W-221-007)
- Dayton boards: [KABD-250](https://daytonaudio.com/product/1863/kabd-250-2-x-50w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd), [PE KABD-250](https://www.parts-express.com/Dayton-Audio-KABD-250-2-x-50W-DSP-Amplifier-Board-aptX-HD-Bluetooth-5.0-325-107?quantity=1), [KABD line promo](https://parts-express.com/promo/kabd-line), [KABD-430](https://daytonaudio.com/product/1869/kabd-430-4-x-30w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd), [PE KABD-430](https://www.parts-express.com/Dayton-Audio-KABD-430-4-x-30W-Bluetooth-Amp-Board-with-DSP-325-430), [KABD-430 manual](https://www.daytonaudio.com/images/resources/325-430--dayton-audio-kabd-430-manual.pdf), [KABD-4100](https://daytonaudio.com/product/1870/kabd-4100-4-x-100w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd), [KABD-PMV4](https://daytonaudio.com/product/2058/kabd-pmv4-panel-mount-with-function-kit-and-potentiometers), [KPX](https://www.parts-express.com/Dayton-Audio-KPX-In-Circuit-Programmer-USB-325-139), [SigmaStudio guide](https://daytonaudio.com/images/resources/sigmastudio-programming-for-the-dayton-audio-kabd-series-of-amplifiers-v1.pdf), [DSP-408 PE](https://parts-express.com/Dayton-Audio-DSP-408-4x8-DSP-Digital-Signal-Processor-for-Home-and-Car-Audio-230-500), [DSP-408 Audiophonics](https://www.audiophonics.fr/en/dsp-av-processors/dayton-audio-dsp-408-4x8-digital-audio-processor-dsp-adau1701-sigmadsp-2556bit-4-to-8-channels-p-13043.html)
- Wondom: [JAB4 Audiophonics](https://www.audiophonics.fr/en/amplifier-boards/wondom-jab4-aa-ja33285-amplifier-board-4-ways-tpa3118-bluetooth-50-dsp-adau1701-4x30w-8-ohm-p-15454.html), [JAB4 notice](https://store.sure-electronics.com/document/notice/35), [JAB4 datasheet](https://store.sure-electronics.com/upload/download/2/Datasheet%20of%20JAB4%204%20x%2030W%20Class%20D%20Amplifier%20Board%20with%20ADAU1701%20DSP%20&%20BT.pdf), [JAB4 connection guide](https://store.sure-electronics.com/upload/download/2/Connection%20Guide%20of%20WONDOM%20JAB4%204CH%20Amplifier%20Board%20with%20BT%20&%20ADAU1701.pdf), [JAB5](https://www.audiophonics.fr/en/amplifier-boards/wondom-jab5-aa-ja33286-amplifier-module-class-d-bluetooth-50-dsp-adau1701-4x100w-6-ohm-p-15064.html), [JAB5 datasheet](https://files.sure-electronics.com/download/JAB5_Datasheet.pdf), [JAB3+](https://www.audiophonics.fr/en/amplifier-boards/wondom-jab3-aa-ja32173-amplifier-module-class-d-bluetooth-50-dsp-adau1701-2x50w-4-ohm-p-15063.html), [APM2](https://www.audiophonics.fr/en/dsp-modules/wondom-adau1701-apm2-audio-digital-signal-processor-dsp-for-active-filtering-sigma-studio-p-14773.html)
- ICEpower: [PE 50ASX2SE](https://parts-express.com/ICEpower-50ASX2SE-Class-D-Audio-Amplifier-with-Power-Supply-Module-2-x-50W-326-212), [ICEpower shop](https://shop.icepoweraudio.com/product/50asx2se/), [diyAudio thread](https://www.diyaudio.com/community/threads/icepower-50asx2-modules.190311/post-4838804)
- TPA3255 boxes and others: [Fosi V3](https://fosiaudio.com/ja/products/fosi-audio-v3-300w-x2-2-0-channel-hi-fi-stereo-audio-amplifier-with-tpa3255-chip), [AIYIMA A20](https://www.audiophonics.fr/en/integrated-amplifiers/aiyima-a20-p-21311.html), [Tinysine TSA7800C](https://uk.robotshop.com/products/tinysine-2-x-50w-100w-21-channels-spdif-coaxialdsp-amplifier-board-tsa7800c)

## Datasheet check, 2026-10-09

`datasheets-2026-10-09.json` holds each number with its source. **SB17NRX2C35-8**: SB's drawing gives the flange 6.5,
the cut-out 144.9, four ø4.3 holes (with a ø8.5 counterbore, probably) on 159, the frame 171, the magnet 100 and 75
behind the baffle; the 10.9 a shop lists as front thickness is everything in front of the baffle (85.9 less 75), the
surround standing about 4.4 above the flange, so the bookshelf's 10.5 rebate stands. **D3004/602200**: shops give the
cut-out 47.8 (SoundImports) and 48 (Willy's), so the 48 body holds; three ø3.3 holes (circle unpublished); SoundImports
lists it 45.3 deep without saying from where. The bookshelf's bore holds 26 behind the faceplate (a CAD check): a
deeper body moves the boss and the bay back. Scan-Speak itself gives no mechanical numbers in text.
