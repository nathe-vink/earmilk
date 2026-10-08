# earmilk: built-in DSP amplifier research

Compiled 2026-10-08. The machine-readable companion is `amps.json` (26 products, fit checks and recommendations).

**How this was researched:** every figure comes from web-search snippets, cross-checked between the maker and retailers (Soundimports, Audiophonics, Audiohum, Parts Express, Madisound, Masori). An asterisk (*) or "unconfirmed" marks a figure with only one source, or with sources that conflict. No pages could be fetched, so the Hypex 2D drawings and datasheets were not opened. Get the screw-hole pattern from hypex.nl before any CNC work.

"HyperX amps" almost certainly means **Hypex** (hypex.nl). Hypex's DSP plate amps are the **FusionAmp (FA)** family. There are eight models, and no newer ones turned up: the 2026 Hypex OEM brochure lists the same eight. Newer Hypex products (the DSA254 OEM module and the NCOREx NCx-MP modules) are not DSP plates.

## TL;DR

| Size | Primary | Budget | What blocks or constrains the fit |
|---|---|---|---|
| Floorstander, 3-way | **Hypex FA253**, mounted rotated 90° (horizontal), centred 175 mm up | **Hypex FA123** (same 360 mm plate length) | No 360 mm FusionAmp fits vertically below the port. Horizontal mounting leaves only 9 mm per side to the inner walls. FA502 and FA503 do not fit at all. The sealed amp compartment takes about 6-7 L. |
| Bookshelf, 2-way | **Hypex FA122**, vertical | **Dayton KABD-250**, one per speaker, on a small sealed DIY plate | The FA122 needs a back panel at least ~340 mm tall. It leaves no room for the label on the back, and its compartment takes ~3.5-4 L. |
| Desk, 100 mm carton | **Dayton KABD-430**, one board drives both speakers | **Wondom JAB4** + ICP5 programmer | No plate amp fits: every FusionAmp is at least 120 mm wide. Use a bare board with an external 24 V power brick. |

## 1. Hypex FusionAmp family

| Model | Ch | W/ch @ 4 Ω | W/ch @ 8 Ω | Plate H×W×D (mm) | Cutout H×W (mm) | Weight (g) | EUR (incl. VAT) | USD (Parts Express) |
|---|---|---|---|---|---|---|---|---|
| FA122 | 2 | 125 + 125 | 75 + 75 | 315×120×55 | 291×96 ¹ | 815* | 429–430 | 422.40* |
| FA123 | 3 | 125 + 125 + 100 | 75 + 75 + 100 ² | 360×120×55 | 336×96 | 955* | 497–500 | 501.60* |
| FA251 | 1 | 250 | 130* | 280×120×55 | 256×96* | 725* | 349–353 | 355.80* |
| FA252 | 2 | 250 + 250 | 150 + 150 ³ | 315×135×55 | 291×111 | 1000* | 562–570 | 567.00* |
| FA253 | 3 | 250 + 250 + 100 | 150 + 150 + 100 ³ | 360×135×55 | 336×111 | 1145* | 649–650 | 646.80* |
| FA501 | 1 | 500 | 270* | 280×135×55 (60?) | 256×111 | n/a | 499.95* | 501.60* |
| FA502 | 2 | 500 + 500 | 350 + 350 | 380×150×90 | 356×126 | 2150 or 2880 (conflict) | 699–708 | 714.00* |
| FA503 | 3 | 500 + 500 + 100 | 350 + 350 + 100 | 420×150×90 | 396×126 | 2275 | 789–790 | 792.00* |

\* unconfirmed.
¹ An Audiophonics drawing shows 293.
² Hypex Direct and KJF list the tweeter channel at 75 W @ 8 Ω.
³ Hypex's own pages say 150 W @ 8 Ω; Soundimports, Audiohum and Madisound say 200 W.

Bridging ch1+ch2 gives: FA122 200 W @ 4 Ω / 250 W @ 8 Ω; FA252/FA253 400 W / 500 W; FA502/FA503 1000 W. The third channel on 3-channel models is always the 100 W tweeter channel, with a 4 Ω minimum load.

**Common to every FA model** (two or more sources unless noted):

- **Amplifier and DSP:**
  - NCore class D, 92 % efficient at full power.
  - Analog Devices SigmaDSP (ADAU1450 per most retailer titles, ADAU1452 per one) with an AK4454 DAC.
  - 15 biquads per amp channel, 3 presets, delay, volume and a soft-clip limiter.
  - FIR needs firmware 5.x and HFD 5.1+, and depends on hardware revision. Some older used units cannot run FIR.
- **Software:**
  - Hypex Filter Design (HFD) is free but **Windows only**.
  - Setup is over USB mini-B, which carries no audio. The cable is not included.
  - **Units ship with no filter, so they make no sound until you upload one.**
  - One retailer reviewer and several forum posts call HFD less polished than miniDSP's software. The HFD manual assumes you already know filter design.
- **Inputs:**
  - Balanced XLR in plus an XLR loop-through out, RCA in, AES/EBU, S/PDIF coax (with loop-through) and Toslink.
  - Each FA drives one speaker. You set it to L or R in HFD and daisy-chain the second speaker over XLR or AES.
- **Mains:**
  - IEC C14 inlet on the plate.
  - Hypex's spec block says 100–120 or 200–240 VAC ±10 %. Some EU retailers list 200–240 V only, and whether the range switches automatically is unconfirmed.
  - The safety class (I or II) was not found.
- **Standby:**
  - Signal-detect auto-on and auto-standby ("wake on line") are set in HFD. An optional Fusion IR remote kit is available.
  - Standby and idle wattage are not published. One owner reports a pop on wake or standby.
- **Cooling and airtightness:**
  - Passive cooling with no fan. Heat leaves through the aluminium plate, and there is thermal protection and regulation.
  - **Not airtight.** Soundimports states this on the FA123, FA251, FA252, FA253 and FA503 pages ("due to thermal regulation").
  - Hypex's FAQ recommends a closed-off, sealed compartment. The Soundimports blog says the same and lists sealing tape.
- **Mounting:**
  - The flange is about 12 mm all round. This is derived: overall size minus cutout is 24 mm on every model.
  - Fixing is 8 or 10 screws. Hypex's "Fusion Mounting Screws" kit is 10 × 4.3 × 25 mm self-tapping.
  - The hole pattern and corner radii are in the 2D drawing and 3D model on each product page's download tab. **These were not obtained.**
- **Speaker harness:** "Cable set loudspeaker FA 3-way", 125 cm long, supplied with new units.

**Modular Hypex alternative:**

- Parts:
  - NCx252MP: 2 × 250 W @ 4 Ω / 150 W @ 8 Ω, 170×105×42 mm. The NC252MP version costs about €260.
  - NCx102EXT: 100 W extension channel, 85×78×27 mm, no retail price found.
  - DSP3-224: ADAU1452, 4 outputs, FIR up to 2048 taps, €315.
- The total costs at least as much as an FA253, before you add a connector plate, IEC inlet, cooling and mains wiring. It is only worth it if no plate fits.

## 2. Alternatives

| Product | Type | Ch | Power | DSP / software | Size (mm) | Cutout (mm) | Price | Verdict for earmilk |
|---|---|---|---|---|---|---|---|---|
| miniDSP PWR-ICE125 | DSP plate (ICEpower 125ASX2 inside) | 2 | 2×125 W @ 4 Ω (450 W bridged) | ADAU1445, FIR + IIR, Win/Mac, Ethernet | 216×153×75 | 202×139 | $399 / €449 | Bookshelf alternative if its back is short. Airtightness unknown. |
| miniDSP PWR-ICE250 | DSP plate (250ASX2 inside) | 2 | 2×250 W @ 4 Ω | as above | 267×153×75 | 253×139* | $499 / €630–679 | 2-way only. May be discontinued. |
| ICEpower 125ASX2 | module with built-in SMPS, no DSP | 2 | 125 W @ 4 Ω (120 W per datasheet), 450 W bridged | none | 160×80×35 | – | $230 / €229–240 | Only usable with an external DSP |
| ICEpower 300A2 | module, no DSP, no power supply | 2 | 300 W @ 4 Ω; 600 W bridged @ 8 Ω | none | 100×60×35* | – | – | No |
| miniDSP 2x4 HD | DSP box only | 2 in / 4 out | – | SHARC, FIR + IIR, Win/Mac | 27×119×107 | – | $225 | DIY 3-way with two amp modules: about FA253 cost, more work |
| Dayton PPA800DSP | 2-way DSP plate | 2 | 600 + 200 W @ 4 Ω | PEQ / crossover / delay, Windows GUI, Bluetooth | 381×160×70 | 355.6×139.7* | $349.98 | Doesn't fit: only 2 channels, and its cutout is wider than the 354 mm cavity |
| Dayton SPA250DSP | subwoofer plate | 1 | 250 W @ 4 Ω | sub-only filters | 260×184×60 | 235×159 | €349–369 | Unsuitable: cannot cross over at 350 Hz |
| Dayton KABD-4100 | board with DSP and Bluetooth | 4 | "4×100 W", load not stated (my estimate: 60–80 W @ 8 Ω at 36 V) | ADAU1701, SigmaStudio + ICP1/KPX | not found | – | $96 | Lowest-cost floorstander proof of concept |
| Dayton KABD-250 | board with DSP and Bluetooth | 2 | 2×50 W @ 4 Ω, 2×30 W @ 8 Ω | ADAU1701 | 91×69×23 | – | $64 | Bookshelf budget pick |
| Dayton KABD-430 | board with DSP and Bluetooth | 4 | 4×30 W (TPA3118) | ADAU1701 | ≈91×69* | – | $70–90 / €110 | Desk primary pick |
| Wondom JAB5 | board with DSP and Bluetooth | 4 | 4×100 W @ 6 Ω (36 V) | ADAU1701 + ICP5 programmer | 122×91×40* | – | €69.90 | EU equivalent of the KABD-4100. Hiss reported. |
| Wondom JAB4 | board with DSP and Bluetooth | 4 | 4×30 W @ 8 Ω | ADAU1701 + ICP5 programmer | – | – | €54.90 | Desk budget pick (EU) |
| Monacor AKB-400DSP | DSP plate | 2 | 400 W @ 4 Ω (total?), 180 W @ 8 Ω | 4 presets, USB, Windows | 330×142×55 | – | – | No advantage over the FA122 |
| Purifi 1ET6525SA | module, no DSP | 1 | 450 W @ 4 Ω | none | 82×63×33 | – | – | No Purifi DSP plate exists |
| Orchard Audio Starkrimson DSP plate | 4-channel DSP plate (Hypex DSP3-224 inside) | 2–4 | ~1200 W total | HFD | not published | – | not published | The only other 3-channel DSP plate found. Announced Sept 2025; availability unconfirmed. |

## 3. Floorstander back-panel fit (390 mm wide, 354 mm between the inner walls)

Coordinates are viewed from behind: x = 0 is the centre line, y is the height above the floor, both in mm.

| Element | y range | x range |
|---|---|---|
| Port bore, Ø100 (a flared Ø~140 flange would occupy y ≈ 335–475) | 355–455 | −50 … +50 |
| Nutrition Facts label, 266×260 | 510–770 | −133 … +133 |
| Free band under the port for a cutout (inner floor is at 18) | 18–355 (about 335 with a flared port) | −177 … +177 |
| Free band between the port and the label | 455–510 (35–55 mm) | too small to use |
| **FA253 plate, rotated 90°, centred at y = 175** | **107.5–242.5** | **−180 … +180** |
| FA253 cutout | 119.5–230.5 | −168 … +168 |
| FA123 plate / cutout at the same position | 115–235 / 127–223 | ±180 / ±168 |

**Verdicts:**

- **FA253 or FA123 mounted vertically: blocked.**
  - A 360 mm plate needs y ≈ 10–370, but only about 335–355 is free under the port. It is 15–35 mm short.
  - There is no room above the port either, because the label starts at 510.
- **FA253 or FA123 mounted horizontally: fits.**
  - The 360 mm flange on the 390 mm back leaves 15 mm per side.
  - The 336 mm cutout in the 354 mm cavity leaves **9 mm per side to the side-wall faces**, so use a CNC or template cut.
  - The plate clears the port bore by 112 mm and the label by 268 mm.
  - If the screw holes sit mid-flange (not confirmed), the end screws land in the 18 mm back panel about 3 mm inside the side-wall faces. Check this against the Hypex drawing.
- An FA123 mounted vertically and offset beside the port would only work with a flush, flangeless port (cutout x 67–163). Not recommended.
- **FA502 is blocked:** its 356 mm cutout is wider than the 354 mm cavity.
- **FA503 is blocked:** its 420 mm plate is wider than the 390 mm back.
- **Dayton PPA800DSP is blocked.**
- Any of these three would need the port moved to the front or a side.
- **Amp compartment:**
  - Use the cabinet side walls as its ends. Add a lower shelf with its top face at y ≈ 101.5, an upper shelf with its underside at y ≈ 248.5, and a front wall about 90 mm in from the back panel's inner face.
  - That encloses about 4.7 L of air and displaces about 6.2 L gross with 12 mm panels or 7.0 L with 18 mm panels. That is 7–8 % of the 88 L box.
  - If the port is left unchanged, the tuning rises to about 33 Hz. Either lengthen the 100 mm port by about 2 cm (roughly 18.8 to 20.9 cm, from the simple vent formula) or add about 6.5 L gross.
  - Check the 12 in woofer's magnet clearance to the compartment's front wall.

## 4. Recommendations

**Floorstander, primary: Hypex FA253** (€649 / $647 each, two per pair)
- Its three channels map onto woofer, mid and tweeter: 250/250/100 W @ 4 Ω, or 150/150/100 W @ 8 Ω.
- Woofer headroom is +21.8 dB over 1 W into 8 Ω. With a 90 dB/W/m 12 in that is about 112 dB peak at 1 m, before any DSP bass boost.
- The mid and tweeter channels have far more power than their drivers can take. Set HFD's soft-clip limit for each driver. HFD's default soft-clip assumes 4 Ω, so enter each driver's real impedance and maximum power.
- It only fits horizontally (see section 3) and needs a sealed compartment.

**Floorstander, budget: Hypex FA123** (€499 / $502 each)
- Same software and inputs as the FA253, and the same 360 mm length in CAD. It is 15 mm less tall, so cut the panel for the model you actually buy.
- The woofer channel gives 75 W @ 8 Ω, about 3 dB less headroom than the FA253. That is fine at domestic levels, but tight if the DSP adds a large low-shelf or Linkwitz-transform boost.
- **Cheapest proof of concept: Dayton KABD-4100** on a DIY aluminium plate with an external 36 V SELV power brick (about $96 plus a programmer and the brick).
  - It is programmed in SigmaStudio, which is harder to learn than HFD.
  - Power per load impedance is not published.
  - The external brick keeps mains voltage out of the cabinet.

**Bookshelf, primary: Hypex FA122** (€429 / $422 each)
- 2 × 75 W @ 8 Ω gives about 106 dB peak with an 87 dB/W/m driver.
- Same DSP workflow as the floorstander.
- Design constraints:
  - The rectangular back must be at least ~340 mm tall.
  - Add about 3.5–4 L of compartment volume to the gross box volume.
  - The label has to move to a side panel.
  - Put the port on the front, or build the box sealed and EQ it.
- If the back is shorter, use the **miniDSP PWR-ICE125** instead (216×153 mm plate, $399).

**Bookshelf, budget: Dayton KABD-250, one per speaker** ($64 each)
- 2 × 50 W @ 4 Ω or 2 × 30 W @ 8 Ω.
- The 91×69 mm board fits on a small sealed plate of about 120×100 mm. It takes almost no box volume, and it runs cool enough to seal in.
- Powered by a 24 V brick.
- Alternatively, one KABD-4100 can run both speakers.

**Desk, primary: Dayton KABD-430** (about $70–90)
- One 4 × 30 W board makes both 2-way desk speakers active.
- Put it in the base of the master carton or in a small hub, powered by a 24 V brick. Run 4-core cable to the second carton.

**Desk, budget: Wondom JAB4 + ICP5 programmer** (€55 + €25)
- Same approach as the KABD-430.
- Both ADAU1701 boards have some hiss. If it is audible at desk distance, add a resistor L-pad to the tweeter.

## 5. Integration notes

**Sealing a non-airtight plate**
- Box in the back of the plate: two shelves and a front wall, with the cabinet sides and back panel closing the rest.
- Glue and seal every seam with PU glue or a silicone fillet.
- Put 2–3 mm closed-cell EPDM or neoprene foam tape under the plate flange.
- Pass cables through tight holes or PG7/PG9 glands, then fill with silicone or epoxy.
- Keep damping wool away from the electronics.
- For a proof of concept that will come apart often, fit M4 threaded inserts instead of self-tapping screws. Check the hole size on the Hypex drawing first.

**Heat**
- Heat leaves through the plate into room air. The sealed compartment does not ventilate the amp.
- Leave at least 100 mm free behind the speaker. This also gives the IEC and XLR plugs room to bend.
- Never cover the plate with the label, grille cloth or a wall niche.
- Hypex gives no orientation guidance. Rotating the plate 90° keeps it vertical, but confirm with sales@hypex.nl. A general plate-amp forum post warns that heatsinks mounted sideways lose some convection.
- Leave at least 20–25 mm of air behind the deepest component.
- Before closing the cabinet, play at high level for an hour and measure the plate temperature.

**Cable routing**
- Woofer: a short run inside the main box.
- Mid: through a sealed gland into its sub-chamber.
- Tweeter: up a rear corner to the gable, about 0.9–1.1 m from a plate centred 175 mm up. The supplied 125 cm harness is marginal, so plan an extension.
- Clip the runs to the walls so they can't rattle, and keep them away from the port mouth.
- Twist each pair. Use at least 1.5 mm² wire for the woofer and 0.75 mm² for the mid and tweeter. Label polarity.

**Mains safety**
- FusionAmp and miniDSP plates have their own IEC C14 inlet. Use an earthed C13 cord and don't modify the plate. The safety class wasn't found, so ask Hypex.
- Two mains-powered speakers plus an RCA source invite ground loops. Use XLR, AES or optical with loop-through instead.
- In the US, confirm the unit works on the 100–120 V band.
- For bare amplifier boards, use an external, certified SELV DC brick (24 or 36 V) so no mains enters the cabinet.
- If mains must go inside the cabinet:
  - use a fused, switched IEC C14 module;
  - bond all touchable metal to protective earth (ring terminal with a star washer);
  - use mains-rated wire and heat-shrink every terminal;
  - keep at least 6 mm creepage between mains and low voltage;
  - fit strain relief;
  - have it PAT or insulation tested.
- A product version will need LVD/EMC (EN 62368-1) or UL certification.

**DSP setup workflow (FusionAmp with HFD)**
1. You need a Windows PC, HFD and a USB mini-B cable. Update the FA firmware following Hypex's tutorial; FIR needs firmware 5.x.
2. Before any sound, upload a **safe measurement filter**: a protective high-pass on the tweeter (e.g. LR4 at 1.5–2 kHz) and low levels and limits on every channel.
3. Measure each driver in the finished box with REW and a calibrated USB mic, keeping the mic position fixed. Use gated far-field measurements for the mid and tweeter, and near-field plus port measurements for the woofer. Export FRD and ZMA files.
4. Design the crossover in VituixCAD, or reuse the passive design's targets:
   - Start from LR4 at about 350 Hz and 2.2 kHz.
   - Add driver EQ and baffle-step or room-gain shelves.
   - Set delays to align the acoustic centres of the waveguide tweeter, mid and woofer.
   - Optionally build a linear-phase FIR in rePhase.
5. In HFD, enter the biquads (or import the FIR). Set per-channel gain, speaker impedance, soft-clip and maximum power, L/R input selection, sensitivity and volume behaviour.
6. Save to preset 1. Use presets 2–3 for variants such as a bass cut for near-wall placement, or a tilt.
7. Turn on signal-detect auto-on and standby.
8. Measure in the room and iterate.

With the ADAU1701 boards the steps are the same, but the filters are built as a SigmaStudio signal flow and written to EEPROM through an ICP1, KPX or ICP5 programmer.

## 6. Open items to confirm before cutting panels or buying
- The Hypex 2D drawings for the FA253, FA123 and FA122: hole pattern, hole diameter and corner radii.
- Whether Hypex accepts a plate rotated 90°.
- The FA safety class and standby/idle wattage.
- The disputed 8 Ω ratings: FA252/FA253 at 150 W or 200 W, and the FA123 tweeter channel at 75 W or 100 W.
- The real driver sensitivity and impedance. The headroom figures above assume 90 dB/W/m (woofer) and 87 dB/W/m (bookshelf driver).
- Dimensions and per-load power ratings for the KABD-4100, KABD-430 and JAB4 boards.

## Sources

**Hypex (maker)**
- [FusionAmp family](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/) · [FA122](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa122) · [FA123](https://hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa123) · [FA251](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa251) · [FA252](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa252) · [FA253](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa253) · [FA501](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa501) · [FA502](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa502) · [FA503](https://www.hypex.nl/products/amplifier-families/fusion-amplifier-family/fusionamp-fa503)
- [Hypex Direct FA122](https://www.hypexdirect.com/products/fusion-amplifiers/fusionamp-fa122) · [Hypex Direct FA252](https://www.hypexdirect.com/products/fusion-amplifiers/fusionamp-fa252)
- [Fusion user manual R4 (PDF)](https://www.hypex.nl/media/df/df/c2/1678368740/Fusion%20Manual%20R4.pdf) · [HFD release notes v5.2.4 (PDF)](https://www.hypex.nl/media/4f/b1/93/1759733530/ReleaseNotes%20Hypex%20Filter%20Design%20v5.2.4.pdf) · [HFD release notes v5.2 (PDF)](https://www.hypex.nl/media/77/f4/de/1753101579/ReleaseNotes%20HFD%20v5.2.pdf)
- [FAQ: building a Fusion amp into a cabinet](https://www.hypex.nl/FAQ-Hypex/Fusion-Amp-Family/I-want-to-build-in-one-of-the-Fusion-Amps-in-my-speaker-cabinets-how-to-do) · [FAQ: heatsinks and cooling](https://www.hypex.nl/FAQ-Hypex/Temperature-and-implementation/Do-I-need-to-add-a-heatsink-to-the-Hypex-amplifiers-to-cool-them)
- [Fusion mounting screws](https://hypex.nl/products/accessories/fastening-materials/fusion-mounting-screws) · [Cable set FA 3-way](https://www.hypex.nl/products/accessories/connection-materials/cable-set-loudspeaker-fa-3-way)
- [DSP3-224](https://www.hypex.nl/products/dsp-family/dsp3-224) · [DSP3-224 datasheet (PDF)](https://www.hypex.nl/media/ca/a3/3c/1745821824/Datasheet%20A4-R02%20DSP3-224-0102.pdf) · [Hypex DSP technology](https://www.hypex.nl/technology/dsp)
- [NCOREx family](https://www.hypex.nl/products/amplifier-families/mains-powered-ncorex-family/) · [NCx102EXT](https://www.hypex.nl/products/amplifier-families/mains-powered-ncorex-family/ncx102ext) · [NCx102EXT datasheet (PDF)](https://www.hypex.nl/media/03/55/3e/1750836511/Datasheet%20NCx102EXT_01xx.pdf) · [NC252MP datasheet (PDF)](https://www.hypex.nl/media/7f/85/fa/1786438779/NC252MP_04xx_R16.pdf)
- [Hypex OEM brochure (PDF)](https://www.hypex.nl/assets/oem-brochure/Hypex_OEM-brochure.pdf) · [DSA254 OEM](https://hypex.nl/products/amplifier-families/dsa-family/dsa254-oem)

**Retailers (Hypex)**
- Soundimports: [FA122](https://www.soundimports.eu/nl/hypex-fa122.html) · [FA123](https://www.soundimports.eu/en/hypex-fa123.html) · [FA251](https://www.soundimports.eu/nl/hypex-fa251.html) · [FA252](https://www.soundimports.eu/de/hypex-fa252.html) · [FA253](https://www.soundimports.eu/en/hypex-fa253.html) · [FA501](https://www.soundimports.eu/nl/hypex-fa501.html) · [FA502](https://www.soundimports.eu/nl/hypex-fa502.html) · [FA503](https://www.soundimports.eu/en/hypex-fa503.html) · [NC252MP](https://www.soundimports.eu/de/nc252mp-2x250w-amp-board.html) · [DSP3-224](https://www.soundimports.eu/nl/hypex-dsp3-224.html) · [Hypex Fusion design guide (blog, NL)](https://www.soundimports.eu/nl/blogs/blog/hypex-fusion-introduction-guide/) · [same guide (IT)](https://www.soundimports.eu/it/blogs/blog/active-design-dei-diffusori-con-amplificatori-hype/)
- Audiophonics: [FA122](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa122-plate-ncore-amplifier-2x125w-dsp-adau1450-dac-ak4454-192khz-p-13530.html) · [FA123](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa123-plate-ncore-amplifier-2x125w-1x100w-dsp-adau1450-dac-ak4454-192khz-p-13531.html) · [FA251](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa251-plate-ncore-amplifier-1x250w-dsp-adau1450-dac-ak4454-p-14542.html) · [FA252](https://audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa252-plate-ncore-amplifier-2x250w-dsp-adau1450-dac-ak4454-192khz-p-16206.html) · [FA253](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa253-p-13532.html) · [FA501](https://audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa501-plate-ncore-amplifier-1x500w-dsp-adau1450-dac-ak4454-192khz-p-13529.html) · [FA502](https://www.audiophonics.fr/fr/modules-amplificateurs/hypex-fusionamp-fa502-module-amplificateur-ncore-btl-2x500w-4-ohm-p-15824.html) · [FA503](https://www.audiophonics.fr/en/amplifier-boards/hypex-fusionamp-fa503-ncore-amplifier-module-btl-2x500w-100w-4-ohm-p-14857.html)
- Audiohum: [FA122](https://www.audiohum.com/fr/composants-diy-hum/kits/kits-electroniques/hypex-fa122) · [FA123](https://www.audiohum.com/fr/composants-diy-hum/kits/kits-electroniques/hypex-fa123) · [FA251](https://www.audiohum.com/fr/composants-diy-hum/kits/kits-electroniques/hypex-fa251) · [FA252](https://www.audiohum.com/gb/diy-components/kits/electronics-kits/hypex-fa252) · [FA253](https://www.audiohum.com/fr/composants-diy-hum/kits/kits-electroniques/hypex-fa253) · [FA501](https://www.audiohum.com/fr/composants-diy-hum/kits/kits-electroniques/hypex-fa501) · [FA502](https://www.audiohum.com/gb/diy-components/kits/electronics-kits/copy-of-hypex-fa502-fusionamp-plate-amplifier) · [FA503](https://www.audiohum.com/es/componentes-diy-hum/kits/kits-de-electronica/hypex-fa503)
- Parts Express: [FA122](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA122-Mono-2-Way-Plate-Amplifier-250W-221-006) · [FA123](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA123-Mono-3-Way-Plate-Amplifier-2-x-250W-75W-221-007) · [FA251](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA251-Mono-Plate-Amplifier-250W-221-008) · [FA252](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA252-Mono-2-Way-Plate-Amplifier-500W-221-009) · [FA253](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA253-Mono-3-Way-Plate-Amplifier-500W-100W-221-010) · [FA501](https://www.parts-express.com/Hypex-Direct-FusionAmp-FA501-Mono-Plate-Amplifier-500W-221-011) · [Hypex Direct brand page (FA502/FA503)](https://www.parts-express.com/brand/Hypex-Direct)
- Madisound: [FA123](https://www.madisoundspeakerstore.com/speaker-amps/hypex-fusionamp-fa123/) · [FA253](https://www.madisoundspeakerstore.com/speaker-amps/hypex-fusionamp-fa253-250w-250w-100w/)
- Other: [Masori FA253](https://masori.de/en/products/fa253) · [Masori FA503](https://masori.de/en/products/fa503) · [Lautsprechershop Fusion](https://lautsprechershop.de/hifi/hypex_fusion_amp_en.htm) · [Hifishark FA123](https://www.hifishark.com/model/hypex-fusion-amp-fa-123) · [Hifishark FA502](https://www.hifishark.com/model/hypex-fusion-amp-fa-502) · [Hifishark FA503](https://www.hifishark.com/model/hypex-fusion-amp-fa-503) · [KJF FA123](https://kjfaudio.com/product/hypex-fusionamp-fa123/) · [StereoNET FA253 listing](https://radar.stereonet.com/listing/25261-hypex-fusion-fa253-3-channel-plate-amplifier) · [StereoNET FA501 owner](https://www.stereonet.com/forums/topic/314032-custom-cabinetry/)

**ICEpower / miniDSP**
- [ICEpower 125ASX2](https://shop.icepoweraudio.com/product/125asx2/) · [125ASX2 release note](https://icepoweraudio.com/icepower125asx2-is-now-released-for-sale-december-6-2007-2/) · [Parts Express 125ASX2](https://parts-express.com/ICEpower-125ASX2-Class-D-Amplifier-Module-with-Built-In-Power-Supply-2-x-125W-326-268) · [Audiophonics 125ASX2](https://audiophonics.fr/en/amplifier-boards/icepower-125asx2-class-d-stereo-mono-amplifier-module-2x215w-1x450w-4-p-17318.html) · [ICEpower module update (audioXpress)](https://audioxpress.com/news/icepower-updates-existing-amplifier-modules-with-new-technology)
- [ICEpower 300A2](https://shop.icepoweraudio.com/product/300a2/) · [300A2 datasheet (PDF)](https://shop.icepoweraudio.com/wp-content/uploads/2023/02/ICEpower-300A2-Datasheet-1.6.pdf)
- [miniDSP PWR-ICE125](https://www.minidsp.com/products/plate-amplifiers/pwr-ice125) · [Soundimports PWR-ICE125](https://www.soundimports.eu/en/minidsp-pwr-ice125.html) · [Audiophonics PWR-ICE125](https://www.audiophonics.fr/en/amplifier-boards/minidsp-pwr-ice125-asx2-amplifier-module-450w-4-ohms-dsp-p-9530.html) · [PWR-ICE125 review notes](https://audioreview.frieve.com/products/en/minidsp-pwr-ice125/)
- [miniDSP PWR-ICE250](https://www.minidsp.com/products/plate-amplifiers/pwr-ice250) · [Masori PWR-ICE250](https://masori.de/en/collections/minidsp/products/pwr-ice250)
- [miniDSP 2x4 HD](https://www.minidsp.com/products/minidsp-in-a-box/minidsp-2x4-hd) · [miniDSP forum: no 3-way plate amp](https://www.minidsp.com/community/threads/3-way-plate-amplifier.10996/)

**Dayton Audio**
- [PPA800DSP](https://www.daytonaudio.com/product/1608/ppa800dsp-2-way-plate-amplifier-800w-2-channel-with-dsp-and-bluetooth) · [Parts Express PPA800DSP](https://parts-express.com/Dayton-Audio-PPA800DSP-2-Way-Plate-Amplifier-800W-2-Channel-with-DSP-and-Bluetooth-300-798) · [Audiophonics PPA800DSP](https://www.audiophonics.fr/en/subwoofer-modules/dayton-audio-ppa800dsp-2-way-amplifier-module-800w-dsp-bluetooth-50-tws-p-13325.html)
- [SPA250DSP](https://daytonaudio.com/product/1526/spa250dsp-250w-subwoofer-plate-amplifier-with-dsp) · [Parts Express SPA250DSP](https://www.parts-express.com/Dayton-Audio-SPA250DSP-250W-Subwoofer-Plate-Amplifier-with-DSP-300-8010) · [Decibel HiFi SPA250DSP](https://www.decibelhifi.com.au/250w-dsp-subwoofer-plate-amplifier)
- [KABD-4100](https://daytonaudio.com/product/1870/kabd-4100-4-x-100w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd) · [Parts Express KABD-4100](https://www.parts-express.com/Dayton-Audio-KABD-4100-4-x-100W-Bluetooth-Amp-Board-with-DSP-325-434) · [KABD-4100 manual (PDF)](https://www.audioclub.ro/cs-content/cs-docs/Manual%20de%20utilizare%20Dayton%20Audio%20KABD-4100-20186-.pdf) · [ST TDA7498E](https://www.st.com/ja/audio-ics/tda7498e.html)
- [KABD-430](https://daytonaudio.com/product/1869/kabd-430-4-x-30w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd) · [KABD-430 manual (PDF)](https://www.daytonaudio.com/images/resources/325-430--dayton-audio-kabd-430-manual.pdf) · [KABD-430 wiring guide (PDF)](https://www.daytonaudio.com/images/resources/325-430--dayton-audio-kabd-430-quick-start-wiring-guide.pdf) · [Parts Express KABD-430](https://www.parts-express.com/Dayton-Audio-KABD-430-4-x-30W-Bluetooth-Amp-Board-with-DSP-325-430)
- [KABD-250](https://daytonaudio.com/product/1863/kabd-250-2-x-50w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd) · [Parts Express KABD-250](https://www.parts-express.com/Dayton-Audio-KABD-250-2-x-50W-DSP-Amplifier-Board-aptX-HD-Bluetooth-5.0-325-107) · [Audiophonics KABD-250](https://www.audiophonics.fr/fr/modules-amplificateurs/dayton-audio-kabd-250-p-21222.html) · [KABD-230 (dimensions)](https://www.daytonaudio.com/product/1862/kabd-230-2-x-30w-all-in-one-amplifier-board-with-dsp-and-bluetooth-5-0-aptx-hd)

**Wondom / Sure Electronics**
- [JAB5 (Audiophonics)](https://www.audiophonics.fr/en/amplifier-boards/wondom-jab5-aa-ja33286-amplifier-module-class-d-bluetooth-50-dsp-adau1701-4x100w-6-ohm-p-15064.html) · [JAB5 (Soundimports)](https://www.soundimports.eu/nl/sure-electronics-aa-ja33286.html) · [JAB4 (Audiophonics)](https://www.audiophonics.fr/en/amplifier-boards/wondom-jab4-aa-ja33285-amplifier-board-4-ways-tpa3118-bluetooth-50-dsp-adau1701-4x30w-8-ohm-p-15454.html) · [ICP5 programmer](https://www.audiophonics.fr/fr/modules-dsp/wondom-icp5-programmateur-pour-jab-interface-usb-uart-application-bluetooth-p-15703.html)

**Others**
- [Monacor AKB-400DSP (Conrad)](https://www.conrad.com/en/p/monacor-akb-400dsp-built-in-amplifier-400-w-1331334.html)
- [Purifi 1ET6525SA](https://purifi-audio.com/shop/1et6525sa-1et6525sa-amplifier-module-2032) · [Audiophonics 1ET6525SA blog](https://audiophonics.fr/en/blog-diy-audio/85-discover-the-new-purifi-1et6525sa-amplifier-module.html)
- [Orchard Audio Starkrimson plate amps (audioXpress)](https://audioxpress.com/news/orchard-audio-previews-upcoming-range-of-starkrimson-plate-amplifiers) · [Positive Feedback](https://positive-feedback.com/?p=104203)
- Forums: [diyAudio: Hypex plate amps with 4 or 8 Ω drivers](https://www.diyaudio.com/community/threads/hypex-plate-amps-and-4-or-8-ohm-drivers.397141/) · [diyAudio: FusionAmp users](https://www.diyaudio.com/community/threads/hypex-fusionamp-users.403031/) · [diyAudio: Fusion troubleshooting](https://www.diyaudio.com/community/threads/hypex-fusion-troubleshooting.423937/) · [Home Theater Forum: plate amp orientation](https://www.hometheaterforum.com/community/threads/plate-amp-location.180649/)
