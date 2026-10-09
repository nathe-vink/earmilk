# earmilk floorstander: driver research, 2026-10-08

These are the buyable drivers and hardware for the 12 in / 6.5 in / 1 in-waveguide three-way. The machine-readable version, with every field, source and confidence note, is in `drivers-floorstander.json` in the same folder.

## Read first

- **How the numbers were found.** Every figure comes from web-search extracts of maker, retailer and database pages; no page could be opened directly. The session's shared search budget ran out before every gap was closed, so some fields are missing.
- **What the marks mean.** "unconfirmed" means one source only, or sources that disagree. "estimate" means my own calculation. "n/f" means not found.
- **Not found anywhere:** the bolt circles and the surround outer diameters. Measure the bought parts before cutting rebates or modelling trim rings.
- **The tweeter flange is limited by the gable.** The tweeter axis (z 903.5) is only **43.5 mm above the body's top panel**. In the throat plane (y 125) the 37.6° slope is 52.8 mm above the axis. So anything round and coaxial in that plane can be **about 80 mm across at most**, whether it is a visible faceplate or a flange hidden just behind a thin throat ring.
  - The 100–104 mm faceplates do not fit as sold. That rules out the SB26 family, the Seas 27TBFC/G, the Scan-Speak D2608 and D2604, the Peerless DX25 and XT25BG60, the Satori TW29 with its faceplate on, and the Purifi WG104. Many of these are popular in DIY waveguides.
  - They would fit only if the tweeter moved at least 10 mm further back and its pocket cut 7–9 mm into the 18 mm top panel. Both are spec changes.
  - That is why the tweeter ranking favours elements, small flanges and removable faceplates.
- **Woofer frame size.** The drawn frame is about ø310, and the owner wants it about 52 mm clear of the plinth's shadow line. A frame up to about **314 mm** keeps that. The SB34 woofers' 346 mm frames would not (34 mm clear). One retailer also lists a 13–14 mm 'front thickness' for them. If that is the flange, a flush rebate would be 16–17 mm deep in an 18 mm baffle.
- **Mid frame size.** Drawn at about ø170. Candidates range from 165 to 184 mm.

## D. Recommendation

| | **Recommended (active POC, Hypex FA253)** | **Alternate (works passive, lower cost)** |
|---|---|---|
| Woofer | **Dayton Audio RSS315HF-4** (4 Ω), USD 239.98 | **Dayton DS315-8** (8 Ω, coated paper). The DSA315-8 uses the same frame with an aluminium cone, USD 128.98. |
| Mid | **SB Acoustics Satori MR16P-8**, about EUR 180–190 / USD 207 | **SB Acoustics SB17NRX2C35-8** (price n/f, roughly EUR 70–90, estimate) |
| Tweeter | **SB Acoustics Satori TW29DN-B** (4 Ω; TW29DN-B-8 is the 8 Ω version), faceplate removed, about EUR 150 | **Scan-Speak Illuminator D3004/602200**, 62 mm faceplate, about EUR 150 / GBP 124 |
| Crossover | LR4 at about 300–350 Hz and about 2.0 kHz in the DSP. One PEQ takes out the woofer's 37 Hz bump. Delay the woofer and mid to align with the tweeter, which arrives about 0.24 ms late. | Passive 350 Hz / 2.2 kHz is realistic (tweeter Fs 425–440 Hz). Active down to about 1.6–2 kHz also works. |
| Drivers per speaker | about USD 610, plus the FA253 at about USD 650 | about USD 405 |

**Why the recommended set:**

- **Woofer.** The RSS315HF-4's frame is 314 mm against the drawn 310, so the outside does not change. Its Qts 0.39 and Vas 84 L are the closest natural match to 88 L of any candidate. Xmax 14.3 mm gives Vd 736 cm³, which is 2.6× the DSA315-8. That means about 6 dB more clean output at 30–40 Hz in the simulation, or about 4–5 dB once the bump is EQ'd out. The 4 Ω load suits the FA253's 250 W channel.
- **Woofer caveat.** In this cabinet the port can only be about 200 mm long, so the tuning is limited to about 30–32 Hz. That leaves a +2.5 to +3.3 dB bump at 36–37 Hz. The DSP removes it, but the woofer is not a passive choice for this box.
- **Mid.** The MR16P-8 is a dedicated midrange (Le 0.11 mH, rated 32 Hz to 8 kHz) on a 165 mm frame. In 8 L sealed it gives fc 82 Hz and Qtc 0.77. Its dark papyrus cone is the nearest real part to the renders' charcoal paper.
- **Tweeter.** The TW29DN-B is the only buyable dome of 1 in class or larger I found whose maker documents removing the faceplate for a waveguide. SB's WG29-187 sheet gives the steps. With the faceplate off, the carved wall meets the surround with no flat ring.
  - Fs is 650 Hz (624 Hz measured by audioXpress) and power handling is 80 W, which together allow a crossover around 2 kHz with the waveguide's gain.
  - The bare motor is no wider than the 71–74 mm cutout and about 32 mm deep, so it fits the 80 mm limit.
  - The same throat geometry takes SB's other TW29 diaphragms (ring, beryllium, Textreme) as upgrades. Confirm each one's diaphragm diameter.
- **Buy one TW29DN-B first** for the bowl test slice, and design the oblate-spheroidal throat around its measured diaphragm.

**Why the alternate set:**

- No CAD change for the woofer: the DS315-8 has the same 314/272/130 frame as today's placeholder.
- The DS315-8 is flat in 88 L at fb 32 Hz with no EQ, at f3 about 31.6 Hz. Its limit is about 110 dB at 40 Hz (1 m, half space).
- The SB17NRX2C35-8's 171 mm frame matches the drawn 170.
- The D3004/602200 has the lowest Fs of anything that fits, and it seats in the existing 62 mm pocket. It leaves a flat ring of about 14 mm around the dome unless it is rear-mounted behind a thin lip.

**Upgrade paths:**

- **Woofer:** the SB34NRXL75-8, if a 346 mm frame is acceptable. It is the best passive fit: flat at fb 32 Hz with about 5 dB more headroom. The Scan-Speak 30W/4558T00 also works (308 mm frame, needs EQ, EUR 350).
- **Mid:** the Purifi PTT6.5M08-NFA-01 (176 mm frame, made to order).
- **Tweeter:** the Satori TW29BN or TW29TXN in the same throat, or the BlieSMa T25B-6.

## Key mechanical numbers for CAD

| Driver | Frame OD | Cutout | Depth behind flange | Holes / bolt circle | Rebate (OD + 2 × 0.8) |
|---|---|---|---|---|---|
| RSS315HF-4 | 314 | 282 | 146 | 8 holes (Dayton); circle 295 (Audiophonics; Dayton gives none) | 315.6 (as today) |
| DS315-8 / DSA315-8 | 314 | 272 | 130 | DS: 5 holes (unconfirmed); circle about 296 (estimate) | 315.6 |
| MR16P-8 | 165 | 140.3 | 75.6 (front 7.5) | n/f; about 154 (estimate) | 166.6 |
| SB17NRX2C35-8 | 171 | 144.9 (SB drawing) | 75; flange 6.5 (SB drawing), 10.9 in front of the baffle in all (85.9 - 75) | 4 x 4.3 on 159 (SB drawing) | 172.6 |
| TW29DN-B, faceplate off | about 71–74 body | pocket about 75 | about 32 (unconfirmed) | faceplate screws (2.5 mm hex, likely M3 or M4; count n/f) | throat ring ID = measured diaphragm OD, about 45 (estimate) |
| D3004/602200 | 62 faceplate | 48 (unconfirmed) | about 21.5 (602000 figure) | 3 holes; circle about 55 (estimate) | 62–64 seat, as in the current CAD |

- **Rebate depth** = the measured flange thickness + the compressed gasket (about 1–2 mm) + the 3 mm trim ring.
- **Mid chamber.** The MR16P-8 ends about 82 mm behind the front face, which leaves 26 mm to the back of the 90 mm chamber.
- **Woofer depth.** The RSS315HF-4 ends about 154 mm behind the front face.

## A. Woofers (12 in) in 88 L net, vented

| | RSS315HF-4 | DS315-8 | DSA315-8 | SB34NRX75-6 | SB34NRXL75-8 | 30W/4558T00 | 32W/4878T00 |
|---|---|---|---|---|---|---|---|
| Ω / Re | 4 / 3.1 | 8 / 6.1 | 8 / 6.0 | 6 / 4.2 | 8 / n/f | 4 / n/f | 4 / 3.1 |
| Fs / Qts / Vas | 24.2 / 0.39 / 84 L | 24.2 / 0.31 / 159 L | 24.2 / 0.33 / 147 L | 19 / 0.40 / 260 L | 22 / 0.28 / 205 L | 17 / 0.32 / 197 L | 18 / 0.32 / 207.5 L |
| Sd / Xmax | 515 / 14.3 | 506.7 / 5.5 | 506.7 / 5.5 | n/f / 11 (or 13) | n/f / 10 | 466 / 12.5 | 531 / 14 |
| Le (mH) | 0.96 | 1.43 | 1.11 | n/f | n/f | 0.83 or 1.51 | 0.5 or 1.93 |
| Sensitivity, 2.83 V | 90.3 | 91 | 90.3 | 88–90 | 91 | 89 | 90 |
| Power (W) | 400 | 120 | 120 | 200 | 200 | 150 | 350 |
| OD / cutout / depth | 314 / 282 / 146 | 314 / 272 / 130 | 314 / 272 / 130 | **346** / 305.2 / 142 | **346** / 305.2 / 146 | 308 / 280 / 144 | 320 / 290 / 152 |
| Frame | steel | steel, cosmetic lip | cosmetic lip | cast Al, vented | cast Al | n/f | die-cast Al |
| Cone | black anodized Al | coated paper, black | black anodized Al | Norex paper | Norex paper | aluminium | paper sandwich |
| Surround | rubber, tall roll | half-roll rubber | half-roll rubber | SBR rubber, single roll | rubber | n/f | n/f |
| Price (each) | USD 239.98 (PE), EUR 299 | USD 149.99 MSRP | USD 128.98 (PE) | EUR 219.95 | EUR 309.95 | EUR 349.95 | EUR 699.95 |

**Box in 88 L, from my lumped-element simulation** (QL 7, half space at 1 m; tune by the impedance dip after building):

| Woofer | fb 32: f3 / shape | fb 30: f3 / shape | Clean SPL at 40 Hz (fb 32) | Suggestion |
|---|---|---|---|---|
| RSS315HF-4 | 27.5 Hz / +3.3 dB @37 | 26.3 / +2.5 @36 | 116.6 dB (power-limited) | fb 32, 101.6 × 194 mm port, one PEQ; active only |
| DS315-8 | 31.6 / +0.1 | 31.0 / flat | 110.0 (Xmax) | fb 32, flat passive |
| DSA315-8 | 30.7 / +0.7 @44 | 30.0 / flat | 110.0 (Xmax) | fb 30–32 |
| SB34NRXL75-8 | 32.1 / flat | 31.7 / flat | 115.1 (power) | fb 32, flat passive (frame too big) |
| SB34NRX75-6 | 31.0 / +3.6 @48 | 30.3 / +3.1 | 115.5 | wants 150–200 L; EQ if used |
| 30W/4558T00 | 28.0 / +4.0 @39 | 26.9 / +3.2 | 113.4 | EQ (assumed Qms 5) |
| 32W/4878T00 | 28.9 / +3.1 @41 | 27.8 / +2.3 | 117.4 | EQ; premium |

- **Port length** (101.6 mm ID, physical, flares included): 194 mm at 32 Hz, 231 mm at 30 Hz. The 92 mm bore needs 152 mm and 183 mm.
- **Port space.** A 194 mm port's inner mouth ends about 40 mm from the RSS315HF-4's magnet plane, 85 mm above its axis. Ports longer than about 200 mm (or 185 mm with the 92 mm bore) collide with the woofer.
- **Port noise.** At 17 m/s, the 101.6 mm port is good to about 105.5 dB at 32 Hz, against about 103.8 dB for the 92 mm bore.

**Noted and rejected:**

- **Purifi PTT12** does not exist. Purifi's largest is the 10 in PTT10.0X04/X08: Fs 24/22 Hz, Xmax 14.8 mm, 86.8/84.8 dB, made to order with an 8–12 week lead time.
- **Seas L26RO4Y** is a 10 in with a frame of about 269 mm.
- **Faital Pro 12PR320, 12RS1066 and 12FH520** have Fs of 42–50 Hz, too high for 32 Hz in 88 L.
- **Dayton DC300-8** reaches f3 31 Hz but has only 215 cm³ of displacement.
- **Fostex FW305** is over-damped in this box.

## B. Midranges (6.5 in), sealed about 8 L, 350 Hz to about 2 kHz

| | MR16P-8 | SB17NRX2C35-8 | 18W/8531G00 | Purifi PTT6.5W04 / M08 | 18WU/8741T00 |
|---|---|---|---|---|---|
| Fs / Qts / Vas | 32 / 0.30 / 44.3 L | 36.5 / 0.42 / 27 L | 28 / 0.36 / 58.2 L | W04 33 / – ; M08 52 / 0.34 / 12 L | 35 or 31 / 0.39 or 0.33 / 37 or 48.6 L |
| Le / Xmax | 0.11 / 3.1–4.8 (unconfirmed) | 0.15 / 5.5 | n/f / 6.5 | M08 0.39 / 3.9; W04 Xmax 5.9 | n/f |
| Sensitivity | 88 dB | 86.4–87 | 87 | M08 90.9; W04 90.3 @2.83 V | 85.5 |
| OD / cutout / depth | **165** / 140.3 / 75.6 | **171** / 144.9 / 75 | 182 / 156 / 78 | 176 / 145 / 85 | 184 / 158 / **105** |
| Cone / look | dark-dyed papyrus-paper cone and cap | black coated Norex paper | black woven glass fibre | n/f | n/f |
| 8 L sealed (my calc) | fc 82 Hz, Qtc 0.77 | 76 Hz, 0.88 | 81 Hz, 1.04 | M08 82 Hz, 0.54 | 83 Hz, 0.92 |
| Price | EUR 180–190; USD 206.60 | n/f | EUR 215; GBP 192 | W04 EUR 430; M08 made to order | EUR 360–370 |
| Verdict | **Recommended** | **Alternate** | frame 12 mm over the drawn 170 | premium upgrade | too big and too deep |

**Also checked:**

- **Seas MCA17RCY** was not found anywhere. The nearest is the 5.5 in MCA15RCY.
- **SB17NAC35-8** is listed as discontinued. Its sibling SB17NBAC35-8 has a 171 mm frame and costs EUR 86.
- **Seas U18RNX/P** (Fs 43, 88 dB, EUR 152–175) is a 7 in class driver, frame n/f.
- **Dayton RS180P-8 and ES180TiA-8** were not re-checked this pass (search budget). The RS180-8's frame is 180.6 mm.

## C. Tweeters for the carved waveguide, ranked on acoustic fit

| # | Tweeter | Dome / radiating OD | Fs / power / sens. | Faceplate: size, removable? | DIY waveguide use, published r0/a0 | Rear-mount: fixing, body dia × depth | Price |
|---|---|---|---|---|---|---|---|
| 1 | **SB Satori TW29DN-B** (also TW29R-B ring, TW29BN Be, TW29TXN) | 29 mm coated cloth, 8 mm surround; about **45 mm** OD (estimate) | 650 Hz (624 measured) / 80 W / 96.5 dB at 4 Ω (unconfirmed), 93 dB at 8 Ω | 104 mm two-part aluminium; **removable per SB** (2.5 mm hex screws; glue at the rim, go slowly) | Factory waveguides: SB WG29-187 and the TW29BNWG/TXNWG (170 mm). Not common in Ath threads. No r0/a0 published. | Faceplate screws into the motor (likely M3/M4; count and circle n/f); body ≤ 71–74 × about 32 | about EUR 150 |
| 2 | **Scan-Speak D3004/602200** (R3004/602200 is the ring version, Fs 420) | 26 mm textile, large roll; about 34 mm (estimate) | **425–440 Hz** / 50 W RMS / 90.5 dB | **62 mm** black anodised die-cast; **not removable**; protective grille | No published waveguide | 3 holes, circle about 55 (estimate); cutout 48; depth about 21.5 | EUR 150, GBP 124 (out of stock at capture) |
| 3 | **BlieSMa T25A-6** (Al/Mg) / T25B-6 (Be) | 24–25 mm metal dome, flush surround; 29.7 mm (forum profile) | 870–980 Hz / n/f / 91.5–93 dB, 6 Ω | 68 mm; removable: no evidence | diyAudio "T25A simple profile": throat 29.7, 104 × 6 mm circular arc (simulated, not built); HTGuide tried 4 printed guides on the T34B | cutout 48, depth 26, M3 (unconfirmed) | GBP 129 ex VAT; EUR 145 ex VAT; end-of-life at Soundimports |
| 4 | **Peerless XT25SC90-04** (dual ring with central plug) | about 32 (estimate) | 825 Hz / 100 W (or 50) / 90.1 dB | 65 mm moulded, not removable | XT family used in diyAudio and Midwest Audio waveguide threads; a printable adapter fits the Visaton WG148R | cutout 46.5–48; depth 25–33 | USD 21.29 |
| 5 | **Seas 27TFFNC/G** (H1396-04) | about 26–27 dome; about 33 (estimate) | 1170 Hz / 80 W / 91 dB | **53 mm** small flange (no separate faceplate) | Linkwitz LX521 tweeter | cutout 46, depth 22 (unconfirmed) | EUR 48 |
| 6 | **Peerless OC25SC65-04** | 29.7 mm effective (datasheet); about 32 | 1382 Hz / 25 W / 93.2 dB | **element**, 41.3 mm body, twist-lock for custom faceplates | marketed for waveguides; a horn write-up exists | bayonet (dims on the datasheet drawing); cutout 38.6, depth 25.5 | USD 35 (clearance) |
| 7 | **Dayton ND25FN-4** | 1 in silk; about 30 | 1290–1350 Hz / 20 W / 90 dB | **element**, 41 mm | budget throat-test unit; Dayton posts a 3D file | 4 holes, cutout 34, depth 21 | USD 15 |

No faceplate thickness was published for ranks 1–7; measure it. The few that were published belong to tweeters below: the SB26STAC's 'front' is 6.5 mm thick and the Peerless DX25's 5 mm.

**Do not fit the gable as sold (100–104 mm faceplates), though common in DIY waveguides:**

- **SB26ADC-C000-4.** Fs 680 Hz, 120 W. Used with Augerpro/Somasonus round guides, the ATH Tritonia S/XS and Ascilab guides; one builder crosses it at 1.1 kHz. Forum reports suggest the diaphragm is glued to the faceplate.
- **SB26CDC-C000-4.** Fs 690 Hz.
- **SB26STAC-C000-4.** Fs 750 Hz. A diyAudio photo shows the dome glued to the faceplate.
- **SB26STWGC-4.** The faceplate is itself the waveguide.
- **Seas 27TBFC/G.** Fs 550 Hz. Fits a WG148R or WG-300 once their throat is opened 2 mm.
- **Scan-Speak D2608/913000.** Fs 700 Hz, 8 Ω.
- **Scan-Speak D2604/833000.** Fs 475 Hz, 93 dB, 100 W, with a plastic faceplate that could be turned down (a mod).
- **Peerless DX25BG60-04, DX25TG59-04 and XT25BG60-04.**
- **Purifi PTT1.3T04 WG104/WG147.** A 1.3 in dome with an integral waveguide; OEM, about EUR 500–630.
- **Dayton ND25FW-4.** Integral waveguide.

**Unsuitable:**

- **Dayton ND20FB-4.** Fs 2072 Hz, 15 W.
- **Wavecor TW022WA01/03.** The bare units are sold to OEMs only.
- **SB21RDCN.** A 21 mm ring dome with a 58 mm plate. It fits, but it is smaller than 1 in.

**Waveguide matching.** No published Ath r0/a0 pair was found for any candidate.

- Set r0 to half the measured dome-plus-surround diameter: about 22.5 mm for the TW29, about 15–17 mm for a 1 in dome.
- Pick a0 in the simulation.
- **Mounting option for the TW29.** Make a module: the bare motor plus a printed or turned throat ring that forms the first few millimetres of the oblate-spheroidal wall. Screw the ring to the motor with the faceplate screws, as SB's adapter ring does. Insert the module from the front into brass inserts in the birch. The joint then falls just outside the surround.

## E. Hardware

**Port**

- **Precision Port 4 in Flared Kit PSP4-BKHT** (Parts Express 268-352), USD 20.89.
  - 101.6 mm ID, flared both ends; the tube is cut to length.
  - Outer flare is 184 mm OD on a 159 mm cutout; inner flare is 157 mm OD.
  - Spare parts: tube 268-382, outer flare 268-376, inner flare 268-377, joining ring 268-380.
  - The 184 mm rim is much bigger than the drawn ø112 flange. Rebate it flush if it is used (rim thickness n/f).
- **Jet Set 100** (Lautsprechershop): 100 mm bore, flared both ends, 105–452 mm long, 149 mm cutout, six screws.
- **Monacor MBR-100** (99 mm bore, 121 mm flange) looks closest to the drawn port but is flared at one end only.
- Or reprint the fab's port at 100 mm ID to keep the spec's look.
- **Length:** 194 mm at fb 32 Hz in 88 L (101.6 mm ID). Build it long and trim it to the impedance dip.

**Terminals, if passive**

- Dayton BPP-G pair, USD 22.98: keyed 11.5 mm hole, 25 mm thread. Re-drill the printed cup's 10 mm holes to suit.
- WBT-0703 Cu at EUR 35.30 per post.
- Mundorf TPCU67OC at CAD 291 per set of four.
- The usual double-banana spacing is 19 mm.

**Active plate amp**

- **Hypex FA253:** 2 × 250 W + 100 W at 4 Ω. The plate is 360 × 135 × 55 mm with a 336 × 111 mm cutout. USD 646.80 at Parts Express, EUR 649 in Europe.
- **Hypex FA503:** 2 × 500 W + 100 W. The plate is 420 × 150 × 90 mm with a 396 × 126 mm cutout. EUR 790.
- Either one changes the back's layout, which is the owner's call. Both ship without a filter loaded.

**Gaskets**

- Parts Express gasketing tape 260-542 (1/8 × 1/2 in, USD 13.98) for the woofer.
- 260-540 (3/8 in) for the mid.
- 1–2 mm Poron or neoprene for the tweeter.

**T-nuts and inserts**

- **Woofer:** #10-32 hurricane nuts (Parts Express 081-1082, 50 pieces) or M5 inserts.
- **Mid:** #8-32 or M4.
- **Tweeter:** M3 brass inserts.
- Measure each bolt circle before drilling; none were published. Use stainless button-head screws under the trim rings.

**Damping**

- **Woofer box:** line the walls with Sonic Barrier Acousta-Blue denim, 30 mm (USD 34.98) or 50 mm (USD 59.98). Do not stuff it, and keep a port diameter of space clear of the port mouth.
- **Mid chamber:** about 65 g of Acousta-Stuf polyfill (0.5 lb per cubic foot × 8 L, up to about twice that), loosely filled. A 1 lb bag is USD 15.98.
- **Optional:** Sonic Barrier 1 in foam with adhesive backing (USD 15) and VE-1 vinyl sheets on the panels.
- **Tweeter pocket:** seal the wire hole with putty or epoxy.

## Appearance notes for CAD and rendering

- **RSS315HF-4.**
  - Satin black anodized aluminium cone (black per Dayton) inside a wide black rubber roll, subwoofer style.
  - The steel frame and its screws (eight per Parts Express; unconfirmed) sit under the 3 mm trim ring.
  - Effective radiating diameter is about 256 mm (from Sd). Expect the surround's outer edge at about 280–295 mm (estimate).
  - The dust cap's shape and colour are n/f.
  - It reads as all black with a faint metallic sheen, not the renders' charcoal ribbed paper. None of the shortlisted woofers has pressed concentric ribs. The closest paper looks are the DS315-8 (black coated paper) and the SB34 Norex (frame too big).
- **MR16P-8.**
  - Matte, fibrous, dark papyrus cone and a cap of the same material, on a 165 mm frame.
  - Visible radiating diameter is about 123 mm (from Sd 119 cm²).
  - The MR16PNW-8 is the undyed twin, if a light natural cone is ever wanted.
- **TW29DN-B in the bowl.**
  - Only the coated-cloth dome and its 8 mm surround show, about 45 mm across (estimate). Colour n/f; coated cloth is usually black. The carved wall runs straight into the surround.
  - The 104 mm decoupled aluminium faceplate is removed and is not seen.
  - The render would change from a 62 mm faceplate on a ø62→74 seat to a bare dome of about 45 mm at the end of a smooth throat. That is a change to the look, so the owner decides it.
- **D3004/602200 (alternate).**
  - A 62 mm black anodised plate with a black protective grille over a 26 mm textile dome. This is what the current CAD models.
- **Trim rings.** Model each one to the measured frame. The flush rebate depth = flange + compressed gasket + 3 mm ring.

## What to measure when the parts arrive

- Each frame's flange thickness, bolt circle and hole size.
- Each surround's outer glue diameter, which sets the trim ring's inner diameter.
- The TW29DN-B with its faceplate off:
  - the diaphragm and surround outer diameters, and the dome's height above the mounting face;
  - the screw count, size and circle;
  - the body's diameter and depth.
- Thiele-Small parameters of each woofer (DATS) before the port is trimmed.

## Sources

**Woofers**
- [Dayton RSS315HF-4](https://daytonaudio.com/product/121/rss315hf-4-12-reference-hf-subwoofer-4-ohm) · [Parts Express](https://www.parts-express.com/Dayton-Audio-RSS315HF-4-12-Reference-Series-HF-Subwoofer-4-Ohm-295-464) · [loudspeakerdatabase](https://loudspeakerdatabase.com/Dayton/RSS315HF-4) · [Masori](https://masori.de/en/products/reference-rss315hf-4) · [Audiophonics](https://www.audiophonics.fr/en/hautparleurs-subwoofers/dayton-audio-rss315hf-4-reference-speaker-driver-subwoofer-aluminium-400w-4-ohm-90db-23hz-1000hz-o305cm-p-4944.html)
- [Dayton DS315-8](https://www.daytonaudio.com/product/1059/ds315-8-12-designer-series-woofer-speaker-8-ohm) · [Parts Express](https://www.parts-express.com/Dayton-Audio-DS315-8-12-Designer-Series-Woofer-295-434) · [Audiophonics](https://www.audiophonics.fr/en/woofer/dayton-audio-ds315-8-speaker-driver-woofer-aluminum-120w-8-ohm-91db-25hz-2500hz-o305cm-p-15751.html) · [loudspeakerdatabase](https://loudspeakerdatabase.com/Dayton/DS315-8)
- [Dayton DSA315-8](https://daytonaudio.com/product/1317/dsa315-8-12-designer-series-aluminum-cone-woofer-8-ohm) · [Parts Express](https://www.parts-express.com/Dayton-Audio-DSA315-8-12-Designer-Series-Aluminum-Cone-Woofer-295-534) · [loudspeakerdatabase](https://loudspeakerdatabase.com/Dayton/DSA315-8) · [speakerboxlite](https://speakerboxlite.com/es/subwoofers/dayton-audio-dsa315-8/specifications)
- [SB34NRX75-6 (SB)](https://sbacoustics.com/product/12-sb34nrx75-6-norex/) · [Willys](https://willys-hifi.com/products/sb-acoustics-sb34nrx75-6-norex-woofer) · [TLHP](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb34nrx75-6-impedance-6-ohm-12-inch.html) · [Soundimports](https://www.soundimports.eu/sb-acoustics-sb34nrx75-6.html) · [loudspeakerdatabase](https://loudspeakerdatabase.com/SB/SB34NRX75-6)
- [SB34NRXL75-8 (loudspeakerdatabase)](https://loudspeakerdatabase.com/SB/SB34NRXL75-8) · [Willys](https://willys-hifi.com/products/sb-acoustics-sb34nrxl75-8-norex-woofer) · [Soundimports](https://www.soundimports.eu/en/sb-acoustics-sb34nrxl75-8.html) · [SB34SWNRX-S75-6 (loudspeakerdatabase)](https://loudspeakerdatabase.com/SB/SB34SWNRX-S75-6)
- [Scan-Speak 30W/4558T00](https://www.scan-speak.dk/product/30w-4558t00/) · [Soundimports](https://www.soundimports.eu/en/scan-speak-30w-4558t00.html) · [Masori](https://masori.de/en/products/discovery-30w-4558t00-en) · [32W/4878T00 datasheet](https://www.falconacoustics.co.uk/downloads/Scanspeak/32w-4878t00.pdf) · [Soundimports 32W](https://www.soundimports.eu/scan-speak-32w-4878t00.html)
- [Purifi PTT10.0X04](https://loudspeakerdatabase.com/PURIFI/PTT10.0X04-NAB-01) · [Purifi PTT10.0X08 shop](https://purifi-audio.com/shop/ptt10-0x08-nab-01-ptt10-0x08-nab-01-2566) · [Seas L26RO4Y](https://loudspeakerdatabase.com/SEAS/XM004-04_L26RO4Y) · [Faital 12PR320](https://www.parts-express.com/FaitalPRO-12PR320-12-Professional-Neodymium-Woofer-8-Ohm-294-1326)

**Midranges**
- [MR16P-8 (SB)](https://sbacoustics.com/product/6%C2%BDin-satori-mr16p-8/) · [Willys](https://willys-hifi.com/collections/midrange-speakers/products/sb-acoustics-satori-mr16p-8-midrange-speaker) · [TLHP](https://en.toutlehautparleur.com/speaker-sb-acoustics-satori-mr16p-8-impedance-8-ohm-6-5-inch.html) · [Soundimports](https://www.soundimports.eu/de/sb-acoustics-mr16p-8.html) · [Madisound](https://www.madisoundspeakerstore.com/approx-6-midrange/satori-mr16p-8-6-egyptian-papyrus-cone-midrange-8-ohm/)
- [SB17NRX2C35-8 (loudspeakerdatabase)](https://loudspeakerdatabase.com/SB/SB17NRX2C35-8) · [Willys](https://willys-hifi.com/products/sb-acoustics-sb17nrx2c35-8-norex-midwoofer) · [TLHP (NRXC35-8)](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb17nrxc35-8-impedance-8-ohm-6-inch.html)
- [18W/8531G00 datasheet](https://www.falconacoustics.co.uk/downloads/Scanspeak/18w-8531g00.pdf) · [speakerboxlite](https://speakerboxlite.com/es/subwoofers/scan-speak-18w-8531g00/specifications) · [Willys](https://willys-hifi.com/products/scanspeak-18w-8531g00-bass-midrange)
- [Purifi PTT6.5W04](https://loudspeakerdatabase.com/PURIFI/PTT6.5W04-NFA-01) · [Audiohum](https://www.audiohum.com/de/diy-hum-komponenten/lautsprecher/mittel-schwer/purifi-ptt65w04-nfa-01) · [PTT6.5M08 test](https://audioxpress.com/article/test-bench-the-ptt6-5m08-nfa-01-6-5-midrange-from-purifi-audio)
- [18WU/8741T00](https://www.lautsprechershop.de/hifi/scanspeak_woofer_en.htm) · [Seas U18RNX/P](https://www.falconacoustics.co.uk/seas-u18rnx-p-h1571-prestige-series.html) · [Seas MCA15RCY](https://www.falconacoustics.co.uk/drive-units-1/seas-mca15rcy-h1262-prestige-series.html) · [SB17NAC35-8](https://loudspeakerdatabase.com/SB/SB17NAC35-8)

**Tweeters and waveguides**
- [SB WG29-187 mounting sheet](https://sbacoustics.com/wp-content/uploads/2026/03/SATORI-WG29-187.pdf) · [audioXpress TW29DN-B-8](https://audioxpress.com/article/test-bench-the-sb-acoustics-satori-tw29dn-b-8-tweeter) · [Willys TW29DN-B](https://willys-hifi.com/products/sb-acoustics-satori-tw29dn-b-tweeter) · [Masori TW29DN-B](https://masori.de/en/collections/sb-acoustics/products/satori-tw29dn-b) · [TLHP WG29-187](https://en.toutlehautparleur.com/sb-acoustics-satori-wg29-187-diameter-187-mm-for-all-satori-tw29.html) · [TW29R-B](https://willys-hifi.com/products/sb-acoustics-satori-tw29r-b-tweeter) · [TW29BNWG](https://falconacoustics.co.uk/tw29bnwg-4-satori-tweeter-by-sb-acoustics.html)
- [D3004/602200 (Willys)](https://willys-hifi.com/products/scanspeak-d3004-602200-illuminator-range) · [Falcon](https://www.falconacoustics.co.uk/scanspeak-d3004-602200-tweeter-illuminator-range.html) · [Scan-Speak news](https://scan-speak.dk/?p=1954) · [Soundimports](https://www.soundimports.eu/nl/scan-speak-d3004602200.html) · [R3004/602200](https://scan-speak.dk/?p=2019) · [Erin, D3004/602000](https://www.erinsaudiocorner.com/driveunits/scanspeak-d3004-602000-tweeter/)
- [BlieSMa T25A-6 (Falcon)](https://www.falconacoustics.co.uk/drive-units-1/bliesma-t25a-6.html) · [Lautsprechershop](https://lautsprechershop.de/hifi/bliesma_en.htm) · [T25A waveguide profile](https://www.diyaudio.com/community/threads/t25a-simple-waveguide-profile.423131/) · [OLA-WG build](https://www.htguide.com/forum/mission-possible-diy/build-stories/42972-build-therad-ola-wg-2-5-a-2-5way-with-sb-midwoofers-and-a-bliesma-tweeter)
- [XT25SC90-04 datasheet](https://www.falconacoustics.co.uk/downloads/Vifa/XT25SC90-04.pdf) · [Parts Express](https://parts-express.com/Peerless-XT25SC90-04-1-Dual-Ring-Radiator-Tweeter-264-1014) · [XT25 waveguide thread](https://www.diyaudio.com/community/threads/waveguide-for-xt25.242093/) · [Midwest Audio XT25](https://diy.midwestaudio.club/discussion/1643/beating-a-dead-horse-the-xt25-on-a-waveguide)
- [Seas 27TFFNC/G (TLHP)](https://en.toutlehautparleur.com/dome-tweeter-seas-27tffnc-g-4-ohm-voice-coil-27-mm.html) · [Falcon](https://www.falconacoustics.co.uk/seas-27tffncg-h1396-04-tweeter-prestige-series.html)
- [OC25SC65-04 datasheet](https://www.Lautsprechershop.de/pdf/peerless/peerless_oc25sc65_04.pdf) · [Parts Express](https://parts-express.com/Peerless-OC25SC65-04-1-Textile-Dome-Tweeter-264-1018) · [Dayton ND25FN-4](https://www.daytonaudio.com/product/1194/nd25fn-4-1-neo-silk-dome-tweeter-element-4-ohm)
- [SB26ADC datasheet](https://cdn.shopify.com/s/files/1/0809/2387/files/SB26ADC-C000-4.pdf) · [SB26STAC faceplate thread](https://www.diyaudio.com/community/threads/help-needed-does-sb26stac-have-a-removable-faceplate.366880/) · [SB26STWGC-4](https://willys-hifi.com/products/sb-acoustics-sb26stwgc-4-tweeter) · [Open-source waveguides thread](https://www.diyaudio.com/community/threads/open-source-waveguides-for-cnc-3d-printing.318190/) · [Somasonus waveguides](https://www.somasonus.net/waveguides) · [ATH Tritonia S drawing](https://at-horns.eu/img/tritonia/ATH-Tritonia-S-drawing.png) · [SB26ADC + Tritonia thread](https://www.diyaudio.com/community/threads/high-performance-compact-active-2-way.440526/latest)
- [Seas 27TBFC/G](https://www.falconacoustics.co.uk/seas-27tbfc-g-h1212-tweeter-prestige-series.html) · [H1212 grille thread](https://www.htguide.com/forum/forum/mission-possible-diy/22073-seas-h1212) · [Soundimports waveguide blog](https://www.soundimports.eu/nl/blogs/blog/wave-guiding-your-favourite-tweeter/) · [D2608/913000](https://willys-hifi.com/products/scanspeak-d2608-913000-tweeter) · [D2604/833000](https://www.scan-speak.dk/product/d2604-833000/) · [DX25BG60-04](https://www.parts-express.com/Peerless-DX25BG60-04-1-Silk-Dome-Tweeter-4-Ohm-264-1478)
- [Purifi PTT1.3T04 WG104](https://ptt.purifi-audio.com/shop/ptt1-3t04-hag-01-wg104-2969) · [datasheet](https://ptt.purifi-audio.com/shop/ptt1-3t04-hag-01-ptt1-3t04-hag-01-wg104-2088/document/1051) · [audioXpress test](https://audioxpress.com/article/test-bench-purifi-audio-s-ptt1-3t04-hag-01-wg104-1-3-aluminum-dome-home-audio-tweeter)
- [Dayton ND25FW-4](https://www.daytonaudio.com/product/1280/nd25fw-4-1-soft-dome-neodymium-tweeter-with-waveguide-4-ohm) · [ND20FB-4](https://www.daytonaudio.com/product/61/nd20fb-4-rear-mount-3-4-neodymium-dome-tweeter-4-ohm) · [Wavecor TW022WA01](https://wavecor.com/html/tw022wa01.html) · [SB21RDCN](https://en.toutlehautparleur.com/dome-tweeter-sb-acoustics-sb21rdcn-c000-4-impedance-4-ohm-voice-coil-21-mm.html) · [SB29RDC on a waveguide](https://johnr.hifizine.com/2014/04/sb29rdc-on-pellegrene-waveguide/)
- [Ath4 thread](https://diyaudio.com/community/threads/acoustic-horn-design-the-easy-way-ath4.338806/page-363) · [at-horns.eu](https://at-horns.eu)

**Hardware**
- [Precision Port 4 in kit](https://www.parts-express.com/Precision-Port-4-Flared-Port-Tube-Kit-268-352) · [Soundimports 4 in flared](https://www.soundimports.eu/en/precision-sound-4-flared.html) · [Jet Set 100](https://lautsprechershop.de/hifi/rohre_en.htm) · [Monacor MBR-100](https://www.simplysoundandlighting.co.uk/monacor-mbr-100-100mm-bass-reflex-port-tube/)
- [Hypex FA253](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa253) · [Parts Express FA253](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA253-Mono-3-Way-Plate-Amplifier-500W-100W-221-010) · [Soundimports FA253](https://www.soundimports.eu/en/hypex-fa253.html) · [Hypex FA503](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa503)
- [Dayton BPP-G](https://parts-express.com/Dayton-Audio-BPP-G-Premium-Binding-Post-Pair-Gold-091-620) · [WBT at Audiohum](https://www.audiohum.com/gb/marcas/wbt/30-connectors-wbt) · [Mundorf TPCU67OC](https://partsconnexion.com/products/mundorf-connector-tpcu67oc-mconnect-binding-post-6mm)
- [Gasket tape 260-542](https://parts-express.com/Speaker-Gasketing-Tape-1-8-x-1-2-x-50-ft.-Roll-260-542) · [Nuts / T-nuts](https://www.parts-express.com/speaker-components/cabinet-hardware-speaker-grill-cloth/nuts-t-nuts) · [10-32 hurricane nuts](https://parts-express.com/10-32-Hurricane-Nuts-50-Pcs.-081-1082) · [Threaded inserts thread](https://www.htguide.com/forum/mission-possible-diy/woodworking-tools-techniques/35414-threaded-insert-best-practice)
- [Acousta-Stuf 1 lb](https://parts-express.com/Acousta-Stuf-Polyfill-1-lb.-Bag-260-317) · [Acousta-Blue denim 30 mm](https://www.parts-express.com/Sonic-Barrier-Acousta-Blue-Speaker-Cabinet-Sound-Absorbing-Denim-30mm-x-40-x-55-15.2-Sq.-ft.-260-566) · [Sonic Barrier 1 in foam](https://parts-express.com/Sonic-Barrier-1-Acoustic-Foam-w-PSA-18-x-24-260-525)

**Earlier pass (2026-10-04):** `/home/user/earmilk/fab/drivers.json` and `/home/user/earmilk/fab/research/drivers.md`. The MR16P-8, PTT6.5M08, D3004/602000 review, DC300-8, FW305, OC25SC65-04 and ND25FN-4 figures marked "earlier pass" come from there.

## Datasheet check, 2026-10-09

`datasheets-2026-10-09.json` holds each number with its source and how sure it is. The PDFs themselves could not be
downloaded from this session, so the numbers are the text of the makers' drawings or the shops' listings, and a drawing's
labels were not seen. What changed or was learned:

- **RSS315HF-4**: Dayton gives the outside diameter 314, the cut-out 282, 8 holes and 146 overall depth; the bolt circle
  only Audiophonics gives, 295. `params.py` now drills on 295 (it was an estimated 298), and the woofer's T-nuts must be
  12 across or less (a CAD check: a 15 flange on 295 overhangs the cut-out).
- **TW29DN-B**: the faceplate is 103.8 x 5.0, four ø4.2 holes counterbored ø8.2 on what is probably a 92 circle, 21.7
  behind the baffle, 29.3 overall. An unlabelled ø70.0 sits behind the faceplate, probably the motor: over 69 the
  sleeve's wall drops under 1.5, so measure the bare unit before printing (sheet 7, M4). Nothing of the bare unit with
  its faceplate off was found; SB's WG29-187 sheet probably has it.
- **Hypex FusionAmp (manual R4)**: FA253 360 x 135 x 55, cut-out 336 x 111; 8 or 10 screws (Hypex suggests 4.3 x 25.4);
  it may be mounted vertical or horizontal and tilted up to 45 degrees; it is not airtight, so it goes in its own
  compartment. The corner radius, plate thickness and hole positions are in Hypex's 2D CAD files, not reached.
