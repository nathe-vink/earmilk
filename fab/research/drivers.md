# Driver research: passive three-way floorstander (12" woofer, 6.5" mid, 1" dome in a 66 mm-throat bowl)

Researched 2026-10-04. Prices change often, so check them again before ordering.

## Read this first: method and caveats

- **How the numbers were gathered.** Every attempt to open a page directly (WebFetch) was blocked by this environment's network proxy. That included parts-express.com, daytonaudio.com, madisoundspeakerstore.com, sbacoustics.com, minidsp.com and loudspeakerdatabase.com. So every figure below comes from search-engine extracts of the cited manufacturer datasheets and retailer product pages. The URL for each one is in the tables and in the Sources list. Search extracts sometimes garble a number, so **open the datasheet link and confirm the figures before you buy.**
- **"(unverified)"** marks a number that did not appear in a datasheet or retailer extract. That covers numbers taken only from aggregator sites (loudspeakerdatabase.com, speakerboxlite), numbers that conflict between sources, my own estimates or calculations, and prices recalled from memory. **n/f** means not found in the sources I could reach. The web-search quota ran out before the crossover-gear prices could be looked up, so every gear price in section 4 is (unverified).
- **Box simulations are my own calculation.** They use the standard vented-box transfer function with leakage losses QL = 7, a net volume of 88 L and tuning at 32 Hz, with no allowance for crossover-inductor resistance (DCR) or room gain. f3 is measured relative to the passband.

### Reality check on the marketing targets (important)

1. **The 32 Hz target is achievable.** The Dayton DSA315-8 simulates to f3 = 32.0 Hz in 88 L tuned to 32 Hz. In a room the response will reach lower still.
2. **91 dB at 2.83 V is not realistic together with 32 Hz in 88 L.** Hoffman's iron law caps it. An ideal driver in a lossless B4 alignment at f3 = 32 Hz in 88 L reaches only about 92 dB/1 W in half-space (my calculation). The real 12-inch hi-fi woofers here are rated 88 to 91 dB at 2.83 V in half-space. A 390 mm-wide baffle has its baffle-step corner near 115/0.39 m ≈ 295 Hz, which is right at the 350 Hz woofer crossover. So the woofer works almost entirely in the step region and needs about 3 to 6 dB of baffle-step compensation. Expect **about 85 to 88 dB at 2.83 V / 1 m** for a flat system, depending on how much compensation you use. The one high-sensitivity woofer that fits the frame (Fostex FW305, 93 dB) only gets f3 = 43 to 54 Hz in this box.
3. **8 ohm nominal.** Every tweeter that fits the 62 mm limit is 4 ohm. That works, because the tweeter is attenuated with an L-pad. The usual convention is that the impedance minimum should not fall below 80 % of the label (6.4 ohm for "8 ohm"). If the finished crossover dips lower, label the speaker 6 ohm.
4. **40 to 250 W.** The woofers are rated 80 to 120 W RMS. Read 250 W as the largest amplifier you can safely use, not as continuous power handling.

---

## 1. Woofers (12-inch, 8 ohm, frame no larger than about 315 mm)

### 1a. Parameters

| Parameter | Dayton DC300-8 (budget) | Dayton DSA315-8 (best box fit) | Dayton DS315-8 | Dayton RSS315HFA-8 | Fostex FW305 | Morel TiCW 1258Ft (premium) |
|---|---|---|---|---|---|---|
| Cone | paper (unverified) | aluminum | non-aluminum Designer cone, material n/f | aluminum (unverified) | paper | "Titanium Series" subwoofer |
| Nominal impedance | 8 ohm | 8 ohm | 8 ohm | 8 ohm | 8 ohm | 8 ohm |
| Fs (Hz) | 22.9 | 24.2 | 24.2 | 22.2 | 25 | 18 |
| Qts | 0.33 | 0.33 | 0.31 | 0.45 | 0.31 listed (0.25 from the listed Qes/Qms, so the listing is inconsistent) (unverified) | 0.27 |
| Qes | 0.37 | 0.40 | 0.37 | 0.54 | 0.28 | n/f |
| Qms | 3.21 | 1.89 | 1.79 | 2.5 | 2.73 | n/f |
| Vas (L) | 181.5 (6.41 ft³) | 147 | 159 | 97.2 | 254 | 191 |
| Sd (cm²) | n/f | 506.7 | 506.7 | 506.7 | 527 | n/f |
| Xmax (mm, one-way) | 4.3 | 5.5 | 5.5 | 14.3 | 4.8 | 10.5 |
| Re (ohm) | 6.8 | 6.0 | 6.1 | 6.5 | 6.6 | n/f |
| Le (mH) | 2.93 | 1.11 @ 1 kHz | 1.43 @ 1 kHz | 1.56 @ 1 kHz | n/f | n/f |
| Sensitivity | 90.3 dB @ 2.83 V/1 m | 90.3 dB @ 2.83 V/1 m | 91 dB @ 2.83 V/1 m | 85.7 dB @ 2.83 V/1 m | 93 dB @ 1 W/1 m | 88 dB (basis n/f) |
| Power, RMS / max (W) | 80 / 160 | 120 / 240 | 120 / 240 | n/f | 125 | 600 (nominal) |
| Frame outer diameter (mm) | n/f (confirm it is under 315) | 314 | 314 | 314 | 312 | 305 |
| Cutout (mm) | n/f | 272 | 272 | 282 | 280 | n/f |
| Mounting depth (mm) | n/f | 130 | 130 | 146 | 121 | n/f |
| Typical US price | n/f (budget class) | $139.98 at Parts Express, MSRP $167.99 (unverified: the extract mixed up part numbers) | MSRP $149.99 (check stock) | n/f | $266.30 (Madisound) | n/f (one Hong Kong listing at HKD 7,910, about US$1,000) (unverified) |
| Datasheet / retailer | [Dayton](https://www.daytonaudio.com/product/34/dc300-8-12-classic-woofer-8-ohm) | [Dayton](https://www.daytonaudio.com/product/1317/dsa315-8-12-designer-series-aluminum-cone-woofer-8-ohm) | [Dayton](https://www.daytonaudio.com/product/1059/ds315-8-12-designer-series-woofer-speaker-8-ohm), [PE](https://www.parts-express.com/Dayton-Audio-DS315-8-12-Designer-Series-Woofer-295-434) | [Dayton](https://www.daytonaudio.com/product/123/rss315hfa-8-12-reference-hf-subwoofer-8-ohm) | [Madisound](https://www.madisoundspeakerstore.com/approx-12-woofers/fostex-fw305-12-woofer/), [PDF](http://madisound.com/pdf/fostexdrivers/fw305.pdf) | [Morel](https://www.morelhifi.com/product/ticw-1258ft/) |

The deepest woofer here is 146 mm, so mounting depth is not a problem in the 354 mm internal depth.

### 1b. How each one fits this box (88 L net, rear port tuned to 32 Hz)

| Woofer | Simulated f3 (88 L, 32 Hz) | Response shape | Likely system sensitivity after 3 to 6 dB baffle-step compensation (unverified estimate) | Verdict |
|---|---|---|---|---|
| **DSA315-8** | **32.0 Hz** (32.6 Hz at 85 L, 31.7 Hz at 90 L) | flat, no peak | 84 to 87 dB | **Best match.** With a 0.5 ohm inductor DCR in series, f3 is 31.5 Hz with a +0.2 dB bump, which is harmless. The aluminum cone has breakup up top (Dayton rates it 24 to 2,000 Hz), so check for a breakup peak in the measurements and add a notch if needed. |
| DS315-8 | 34.1 Hz | flat | 85 to 88 dB | Good. 0.7 dB more sensitive, with a non-metal cone (Dayton rates it to 2,500 Hz against 2,000 Hz for the DSA). Slightly higher f3. Dayton's own suggestion is 2 ft³ vented with f3 37 Hz. |
| DC300-8 | 33.7 Hz | flat (+0.1 dB) | 84 to 87 dB | Good budget option. Limited Xmax (4.3 mm) and high Le (2.93 mH, harmless with a 350 Hz crossover). |
| RSS315HFA-8 | 24.9 Hz | +2.2 dB hump at 44 Hz | 80 to 83 dB | **Struggles with 91 dB.** It is a subwoofer driver: very deep and huge excursion, but about 5 dB less sensitive than the others. |
| Fostex FW305 | 43 to 54 Hz (depends on which Qts is right) | over-damped | 87 to 90 dB | **Struggles with 32 Hz.** It is the only way to approach 91 dB, but its very low Qts and large Vas need a much bigger box. |
| TiCW 1258Ft | about 30 to 33 Hz (Qes assumed 0.28 to 0.32) (unverified) | flat | 82 to 85 dB | Deep, but a subwoofer-oriented driver at 88 dB. Expensive. Several parameters not found. |

**Considered and rejected:**
- **SB Acoustics SB34NRXL75-8** (91 dB, Fs 22 Hz, Qts 0.28, Vas 205 L (unverified), $337.70 at Madisound): its 346 mm outer diameter is too big for the frame limit.
- **Scan-Speak Revelator 32W/4878T00**: 4 ohm, 320 mm frame and 87.1 dB/1 W.
- **Scan-Speak 30W/4558T00**: 4 ohm (Fs 17 Hz, Qts 0.32, Vas 197 L, Xmax 12.5 mm).
- **Peerless SLS-P830669**: Parts Express lists Fs 31 Hz, Qts 0.54, Vas 132 L and 89.8 dB; the loudspeakerdatabase listing says Fs 34 Hz, Qts 0.64 (unverified). Its Qts is too high for this box: it simulates a +2.5 to +3.5 dB hump near 60 Hz.

Peerless SLS sources: [PE](https://www.parts-express.com/Peerless-830669-12-Paper-Cone-SLS-Subwoofer-264-1118), [LDB](https://loudspeakerdatabase.com/Peerless/SLS-P830669).

---

## 2. Midranges (6.5-inch class, frame no larger than about 175 mm, used from about 350 Hz to 2.2 kHz in a sealed chamber)

| Parameter | SB Acoustics SB17MFC35-8 (budget) | Dayton DSA175-8 (budget) | SB Acoustics Satori MR16P-8 (premium) | Purifi PTT6.5M08-NFA-01 (premium, borderline fit) | Seas Prestige MCA15RCY H1262-08 (5.5" alternative) |
|---|---|---|---|---|---|
| Cone | polypropylene | aluminum | paper and papyrus (dedicated midrange) | fibre (dedicated midrange) | coated paper (dedicated midrange) |
| Nominal impedance | 8 ohm | 8 ohm | 8 ohm | 8 ohm | 8 ohm |
| Fs (Hz) | 33 | 38.4 | 32 | 52 | 51 |
| Qts | 0.37 | 0.29 | 0.30 | 0.34 | n/f |
| Qes | 0.40 | 0.35 | 0.32 | n/f | n/f |
| Qms | 4.9 | 1.66 | 5.11 | n/f | n/f |
| Vas (L) | 39 | 18.7 (0.66 ft³) | 44.3 | 12 | 12 |
| Sd (cm²) | 118 | 128.7 | 119 | n/f | n/f |
| Xmax (mm, one-way) | 5.5 | 5.3 | 4.77 | 3.9 (linear) | n/f |
| Re (ohm) | 5.7 | 5.8 | 6.2 | 6.5 | n/f |
| Le (mH) | 0.15 | 0.85 | 0.11 | 0.39 | n/f |
| Sensitivity | 88 dB @ 2.83 V (SB rating; 87.3 calculated) | 88.1 dB @ 2.83 V | 88 dB @ 2.83 V | 90.9 dB @ 2.83 V | 89.5 dB (basis n/f) |
| Frame outer diameter (mm) | 171 | **175.6 (right at the limit)** | 165 | **176 (1 mm over the limit)** | 146 (smaller rebate needed) |
| Cutout (mm) | 146 | 144 (5.67") | 140.3 | n/f | n/f |
| Mounting depth (mm) | 75 (86 overall) | 80.5 (3.17") | 75.6 | 85.2 | n/f |
| Rated or usable range | Range n/f. A poly cone like this is normally smooth through 3 kHz (unverified) | 38 to 7,500 Hz (Dayton). The aluminum breakup peak lies above that and must be pushed well down by the low-pass | 32 to 8,000 Hz (SB) | 56 to 3,500 Hz (Purifi) | 100 to 4,000 Hz |
| Typical US price | $75.90 (Madisound; out of stock when checked) | $54.98 to $67.99 (MSRP) | $206.60 (Madisound) | n/f (made to order) | $120.60 (Madisound) |
| Datasheet / retailer | [SB PDF](https://sbacoustics.com/wp-content/uploads/2020/02/6in-SB17MFC35-8.pdf), [Madisound](https://www.madisoundspeakerstore.com/sb-acoustics-woofers-6-7/sb-acoustics-sb17mfc35-8-6-poly-cone-woofer/) | [Dayton](https://www.daytonaudio.com/product/1314/dsa175-8-6-1-2-designer-series-aluminum-cone-woofer-8-ohm), [PE](https://www.parts-express.com/Dayton-Audio-DSA175-8-6-1-2-Designer-Series-Aluminum-Cone-Woofer-295-528) | [SB](https://sbacoustics.com/product/6%C2%BDin-satori-mr16p-8/), [Madisound](https://www.madisoundspeakerstore.com/approx-6-midrange/satori-mr16p-8-6-egyptian-papyrus-cone-midrange-8-ohm/) | [Purifi](https://purifi-audio.com/shop/ptt6-5m08-nfa-01-ptt6-5m08-nfa-01-271), [Madisound](https://www.madisoundspeakerstore.com/approx-6-midrange/ptt6.5m08-nfa-01-6.5-ultra-low-distortion-midrange-8-ohm/), [audioXpress test](https://audioxpress.com/article/test-bench-the-ptt6-5m08-nfa-01-6-5-midrange-from-purifi-audio) | [Madisound](https://www.madisoundspeakerstore.com/approx-5-midrange/seas-prestige-mca15rcy-h1262-5.5-coated-paper-midrange/), [Seas](https://www.seas.no/index.php?option=com_content&view=article&id=77%3Ah1262-08-mca15rcy&catid=46&Itemid=240) |

**Mid chamber sizing (my calculation).** At 6 L the sealed resonance is 78 to 93 Hz for all of these drivers, far below the 350 Hz crossover, so any chamber of 4 to 10 L works. The high-Vas drivers (SB17MFC35-8 and MR16P-8) reach a Qtc of about 0.9 to 1.2 at 4 to 6 L. That is harmless behind a 350 Hz high-pass, but give them about 8 L and fill the chamber loosely with damping material. The DSA175-8 and Purifi are fine at 4 to 6 L.

**Budget alternates:**
- Dayton DS175-8: 175.6 mm, 87.7 dB, Fs 37 Hz, Qts 0.27, Vas 17 L, Le 1.06 mH ([Dayton](https://www.daytonaudio.com/product/1056/ds175-8-6-1-2-designer-series-woofer-speaker-8-ohm)).
- Dayton DC160-8: 165 mm, 86.1 dB, Le 2.26 mH, Xmax 3.15 mm, MSRP $41.99 ([Dayton](https://www.daytonaudio.com/product/22/dc160-8-6-1-2-classic-woofer-8-ohm)).
- SB Acoustics SB17NRX2C35-8: 171 mm, 86.4 dB, Fs 36.5 Hz, Qts 0.42, Vas 27 L, Le 0.15 mH; price n/f; data from loudspeakerdatabase only, so treat as (unverified) ([LDB](https://loudspeakerdatabase.com/SB/SB17NRX2C35-8)).

**Too large for the 175 mm limit:**
- Dayton RS180-8: 180.6 mm.
- Scan-Speak Revelator 18M/8631T00: 182 mm. A pity, because it is an excellent midrange.
- Faital Pro 6FE100: 181.2 mm across the mounting ears.
- Peerless SDS-P830657: 182 mm.

---

## 3. Tweeters (1-inch dome; faceplate no larger than 62 mm because the bowl throat is 66 mm)

This is the hard part. Most "compact" 1-inch domes have faceplates of 65 to 72 mm. Only two kinds of product actually fit:

1. **Scan-Speak's small-flange Illuminator family**, with 62 mm round aluminum faceplates.
2. **Faceplate-less tweeter elements** designed to be mounted into a custom faceplate or waveguide.

A faceplate-less element has an extra advantage here. You make the mounting ring yourself, so its inner contour can continue the bowl's profile right down to the dome.

### 3a. Tweeters that fit as sold

| Parameter | Scan-Speak Illuminator R3004/602200 | Scan-Speak Illuminator D3004/602200 | Scan-Speak Silver D3004/602006 (same tweeter as the discontinued D3004/602000) | Peerless (Tymphany) OC25SC65-04 | Dayton ND25FN-4 |
|---|---|---|---|---|---|
| Type | 26 mm ring dome, neodymium | 26 mm dome, neodymium (Solen's listing calls it a "ring dome"; check) | 1" textile dome, neodymium | 1" textile dome, neodymium, no faceplate | 1" silk dome, neodymium, no faceplate |
| Impedance / Re | 4 ohm / 3.0 ohm | 4 ohm / 3.0 ohm | 4 ohm / 3.0 ohm | 4 ohm / 3.0 ohm | 4 ohm / n/f (the sibling ND25FA-4 is 3.2 ohm) (unverified) |
| Le (mH) | 0.02 | n/f | 0.02 | 0.02 | n/f (ND25FA-4 is 0.03) (unverified) |
| Fs (Hz) | **420** | **440** | 700 | 1,382 | 1,350 |
| Sensitivity | 89.5 dB @ 2.83 V | 90.5 dB @ 2.83 V | 89 dB @ 2.83 V (89.2 on the datasheet) | 93.1 dB @ 2.83 V on the datasheet; Parts Express lists 96.2 (unverified) | 90 dB @ 2.83 V |
| Recommended crossover or range | used 2.5 to 40 kHz | used 2.5 to 30 kHz | 2.5 kHz, 12 dB/oct (datasheet). Erin's Audio Corner measured very low distortion above 1.3 kHz | 2.5 kHz, 12 dB/oct (one listing); another source says 3 kHz or higher | used 2.5 to 20 kHz; users of its sibling, the ND25FA-4, typically cross at about 3 to 3.5 kHz |
| Faceplate | **62 mm round, aluminum** | **62 mm round, black anodized aluminum** | **61.9 mm round, aluminum** | **None.** Body is 41.3 mm across, with a twist-lock to mate with a custom faceplate | **None.** Element is 41 mm (1.61") across |
| Cutout (mm) | 43 (3 mounting holes) | n/f (the D3004/602000 needed 50) (unverified) | 50 | 38.6 (1.52") | n/f (fits your own ring) |
| Mounting depth (mm) | n/f | n/f (the D3004/602000 is 21.5) (unverified) | 21.5 | 25.5 | 21 (0.83") |
| Power (W) | n/f | 50 RMS / 130 max | 50 RMS / 130 max | 25 RMS | 20 RMS |
| Typical US price | $197.20 at Madisound (one other listing showed $141) | US price n/f; Solen lists CA$222.71 | $185.40 (Madisound) | $35.20 (Madisound) | MSRP $14.99 |
| Datasheet / retailer | [Scan-Speak](https://www.scan-speak.dk/product/r3004-602200/), [Madisound](https://www.madisoundspeakerstore.com/ring-radiator-tweeters/scan-speak-r3004/602200-illuminator-ring-radiator-tweeter/) | [Scan-Speak](https://www.scan-speak.dk/product/d3004-602200/), [Solen](https://solen.ca/en/products/scan-speak-illuminator-d3004-602200-26mm-ring-dome-tweeter) | [Madisound (602006)](https://www.madisoundspeakerstore.com/auto-tweeters/scanspeak-silver-series-d3004-602006-1-textile-dome-tweeter-each/), [Madisound (602000, discontinued)](https://www.madisoundspeakerstore.com/scanspeak-soft-dome-tweeters/scanspeak-illuminator-d3004/6020-00-tweeter-textile-dome/), [Erin's review](https://www.erinsaudiocorner.com/driveunits/scanspeak-d3004-602000-tweeter/) | [Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-vifa/peerless-oc25sc65-04-1-textile-dome-tweeter-4-ohm/), [Tymphany PDF](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6167/OC25SC65-04.pdf) | [Dayton](https://www.daytonaudio.com/product/1194/nd25fn-4-1-neo-silk-dome-tweeter-element-4-ohm), [PE](https://www.parts-express.com/Dayton-Audio-ND25FN-4-1-Silk-Dome-Neodymium-Tweeter-Element-4-Ohm-275-053) |
| Fit for a 2.2 kHz crossover | **Best.** The very low Fs leaves margin, and the waveguide's loading helps further. | **Very good.** | Workable at about 2.5 kHz, which is where users settle with it. Erin found a dip from 2 to 5 kHz and a rise above 5 kHz, so EQ it in the crossover. | Cross at about 2.8 to 3 kHz, not 2.2. | Cross at about 3 kHz, not 2.2. Its 20 W rating is the lowest here. |

**Mounting notes.**
- A 62 mm faceplate in a 66 mm throat leaves a 2 mm gap all round. Fill it flush (felt, or a thin turned ring) so it does not cause diffraction or a small cavity resonance.
- For the two faceplate-less elements, make a ring (3D-printed, or turned in plywood or MDF) no larger than 62 mm per your spec, and shape its face to continue the bowl. The OC25SC65-04 was designed for exactly this: Tymphany's datasheet describes the twist-lock for mating with custom faceplates, retailers describe it as suited to waveguides, and one builder has written up mounting it in a horn ([link](https://josephcrowe.com/blogs/news/peerless-oc25sc65-04-with-horn-no-1900)).
- Whatever you choose, the tweeter must be measured in the finished bowl. The waveguide changes both its level (usually several dB of gain at the low end of its range (unverified)) and its directivity.

### 3b. Tweeters that need cutting down, and other options

| Model | Faceplate | Cutout | Fs | Sensitivity | Recommended crossover | Price | What it would take |
|---|---|---|---|---|---|---|---|
| Dayton ND25FA-4 | 66 mm round (material n/f) | 45 mm (1.77") | 1,350 Hz | 90 dB @ 2.83 V | 2.5 to 20 kHz range | $11.49 (Parts Express), MSRP $14.99 | Not worth trimming. Buy its faceplate-less version, the ND25FN-4, instead ([Dayton](https://www.daytonaudio.com/product/1196/nd25fa-4-1-soft-dome-neodymium-tweeter-4-ohm)) |
| Peerless NE25VTS-04 | 66.3 mm aluminum | n/f | 733 Hz | 88.1 dB @ 2.83 V | 2.0 kHz, 12 dB/oct | $42 (Parts Express clearance) | Low Fs, but it needs 2.2 mm turned off the radius on a lathe, and it is being cleared out (likely discontinued) ([PE](https://www.parts-express.com/Peerless-NE25VTS-04-1-Silk-Dome-Tweeter-264-1034), [PDF](https://www.falconacoustics.co.uk/downloads/Vifa/NE25VTS-04.pdf)) |
| Peerless BC25SC55-04 | 70 mm round polymer with flats at 54 mm | 43 mm (1.70") | 1,401.5 Hz | 93.3 dB @ 2.83 V | n/f | $14.25 (Parts Express) | Trim the two round sections down to 62 mm; the recessed screw holes may be lost, so glue or clamp it ([PE](https://www.parts-express.com/Peerless-BC25SC55-04-1-Square-Frame-Tweeter-264-1024)) |
| Morel MDT12 (8 ohm, Re 5.2, Le 0.05) | 54 mm **square** (about 76 mm corner to corner, my calculation) | 44 mm | 1,000 Hz | 89 dB @ 2.83 V | 3 kHz, 12 dB/oct | $52 (Madisound) | Round the corners off to 62 mm. 15.5 mm deep. The only 8 ohm option ([Madisound](https://www.madisoundspeakerstore.com/morel-soft-dome-tweeters/morel-mdt12-1-textile-dome-tweeter/)) |
| Vifa DQ25SC16-04 (titanium) | 65 mm | 43 mm | n/f | n/f | n/f | n/f | Turn 1.5 mm off the radius ([Madisound](https://www.madisoundspeakerstore.com/hard-dome-tweeter/vifa-dq25sc16-04-1-titanium-dome-tweeter/)) |
| Audiofrog GB10 (car audio) | about 49 mm body | n/a | 1,500 Hz | 90 dB @ 2.83 V | at least 2.5 kHz, 24 dB/oct | $469 per pair | Fits, but it is expensive and its high Fs rules out 2.2 kHz ([Audiofrog](https://www.audiofrog.com/gb10-1-25-mm-audiophile-grade-automotive-tweeter/)) |
| *Smaller than 1":* SB Acoustics SB21RDCN-C000-4 | 58 mm | n/f | 850 Hz | 89.5 dB | n/f | $55.20 (Madisound) | Fits as sold, but it is a 20 mm ring dome ([Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-sb-acoustics/sb-acoustics-sb21rdcn-c000-4-ring-dome-tweeter-neodymium/)) |
| *Smaller than 1":* Scan-Speak R2004/602200 | 55 mm | n/f | 625 Hz | 87.5 dB | used from 3 kHz | $139 to $178.60 | Fits as sold, but it is a 19 mm ring ([Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-scanspeak/scan-speak-r2004/602200-19mm-small-ring-radiator-tweeter/)) |

**Checked and too large:**

| Model | Size | Source |
|---|---|---|
| Peerless DX25BG60-04 | 72 mm cutout | [PE](https://www.parts-express.com/Peerless-DX25BG60-04-1-Silk-Dome-Tweeter-4-Ohm-264-1478) |
| Peerless BC25SC06-04 | 70 mm | [PE](https://www.parts-express.com/Peerless-BC25SC06-04-1-Textile-Dome-Tweeter-264-1028) |
| Vifa NE25VTA-04 | 66 mm | [eBay listing](https://www.ebay.com/itm/135161832446) |
| Morel ET 448 | 72 mm | [Falcon](https://www.falconacoustics.co.uk/morel-et-448-tweeter.html) |
| Morel MDT 29 | 94 mm | [PE](https://www.parts-express.com/Morel-MDT-29-1-1-8-Soft-Dome-Tweeter-277-010) |
| Bliesma T25A-6 | 68 mm | [Falcon](https://www.falconacoustics.co.uk/bliesma-t25a-6.html) |
| Dayton AN25F-4 | 2.9" (74 mm) | [Dayton](https://www.daytonaudio.com/product/1567/an25f-4-1-soft-dome-neodymium-car-audio-tweeter-pair-4-ohm) |
| HiVi SD1.1-A | 4.56" | [PE](https://www.parts-express.com/HiVi-SD1.1-A-1-Textile-Dome-Tweeter-297-416) |
| Seas 22TAF/G | 97.7 mm | [Madisound](https://www.madisoundspeakerstore.com/hard-dome-tweeter/seas-prestige-22taf/g-h1283-alum/magn.-alloy-22-mm-dome-tweeter/) |
| Seas 27TBFC/G | 103.8 mm | [Madisound](https://www.madisoundspeakerstore.com/hard-dome-tweeter/seas-prestige-27tbfc/g-h1212-aluminum/magnesium-dome-tweeter/) |
| Scan-Speak D2010/8513 | 98 mm | [Falcon PDF](https://www.falconacoustics.co.uk/downloads/Scanspeak/d2010-851300.pdf) |

---

## 4. Getting a good crossover with no electronics experience

No published crossover will match this speaker, because the tweeter's response is set by your own bowl and the mid sits in a custom chamber. The crossover has to be designed from measurements of the finished cabinet. There are three realistic routes, and they combine well: measure first, optionally audition with DSP, then design the passive network yourself with a forum mentor, or pay someone.

### (a) Measure, and audition with DSP

- **Measurement kit (needed on every route):**
  - Calibrated USB microphone: miniDSP UMIK-1, about $80 to $110 (unverified).
  - REW (Room EQ Wizard), free, for Windows, macOS and Linux.
  - Impedance tester: Dayton Audio DATS V3, about $130 to $150 (unverified). It produces the impedance (.zma) files the crossover programs need, and it also measures Thiele-Small parameters.
- **What to measure:**
  1. Impedance of each driver mounted in the cabinet (DATS).
  2. Mid and tweeter frequency response at 1 m on your chosen listening axis, gated to remove room reflections.
  3. Woofer and port close-miked, then merged with the far-field data and given the baffle-diffraction correction. VituixCAD's Merger and Diffraction tools do both steps.
  4. Off-axis curves every 10 to 15 degrees if you want a power-response design.
  5. Keep the timing reference consistent between drivers (REW's timing reference, or a fixed mic position) so the relative phase is real.
- **DSP audition stage (optional but very instructive):**
  - Use a miniDSP 2x4 HD, about $225 to $250 (unverified). It has 2 inputs and 4 outputs, which is enough to run one speaker as an active three-way. One speaker is all you need for design measurements; for stereo listening you need two units, or a 4-in/8-out box such as the Dayton DSP-408, about $130 to $150 (unverified).
  - Add 3 amplifier channels per speaker: a pair of inexpensive class-D stereo amps (about $50 to $100 each) or a multichannel amp such as the Dayton MA1240a (about $350 to $450). All amp prices are (unverified).
  - Set Linkwitz-Riley 24 dB/oct filters at about 350 Hz and 2.2 to 2.5 kHz, level-match the drivers, EQ toward flat, and listen. The response you end up liking becomes the target for the passive design.
- **Staying active permanently** gives the best result, but the speaker stops being passive. Hypex FusionAmp FA253 three-way DSP plate amp, about $1,000 or more (model details and price unverified). Cheap ADAU1701 DSP amp boards (Wondom/Sure) exist but need SigmaStudio, which is not beginner-friendly.

### (b) Design the passive crossover yourself from those measurements

- **VituixCAD** (free, Windows) is the most capable. It covers off-axis and power response, driver merging, baffle diffraction and an optimizer. It is the better tool, with a steeper learning curve.
- **XSim** (free, Windows) is simpler: it works on-axis and with impedance curves, and it is easier for a first design.
- Import each driver's .frd and .zma files, draw the network, and let the program optimize part values toward your target. Then build on a board with screw terminals and measure again. Expect one or two rounds of changes, usually to the tweeter L-pad, the baffle-step level or a notch.
- **Parts budget:** about $100 to $250 per speaker (unverified).
  - Use a **low-DCR woofer inductor** (about 0.3 to 0.5 ohm or less). 0.5 ohm costs about 0.5 dB of sensitivity and moves the DSA315-8's f3 from 32.0 to 31.5 Hz.
  - Use film capacitors in the tweeter and mid circuits and air-core inductors for the mid and tweeter.
  - Keep the impedance minimum at 6.4 ohm or higher if the speaker is to be labelled 8 ohm.

### (c) Get help, or pay someone

- **Free help.** I could not check these against current listings. Experienced members of the DIY forums routinely review or design crossovers if you post your .frd and .zma files: the Parts Express Tech Talk forum, diyAudio's Multi-Way forum, HTGuide's DIY section, the Midwest Audio Club DIY forum and the AVS Forum DIY speaker forum. Members of local DIY clubs often own measurement rigs.
- **Paid design.** Not verified in this session; the search quota ran out.
  - **Madisound** designs crossovers in-house; its online reference library publishes them, for example "SB13PFC2508 + MDT12 Passive Crossover Design". Ask whether they will quote a custom job.
  - Independent designers known from the forums, and **GR-Research** (Danny Richie), are known to do custom crossover work (unverified).
  - Expect to send in-box .frd and .zma files, or sometimes the speaker itself, and to pay a few hundred dollars (unverified).

**Recommended route for a beginner.** Buy the UMIK-1 and DATS V3 (about $210 to $260 in total, unverified) and learn REW on the finished cabinet. Design in VituixCAD, or in XSim if VituixCAD feels like too much, and post your files on Parts Express Tech Talk or diyAudio for review before ordering parts. If the budget allows, add a miniDSP 2x4 HD with a cheap amp to audition the crossover points first. If designing still feels out of reach once you have measurements, those same files are exactly what a paid designer will ask for.

---

## 5. Shortlist (one speaker; double for a pair)

| Tier | Woofer | Midrange | Tweeter | Driver cost per speaker | Why they suit each other |
|---|---|---|---|---|---|
| **Budget** | Dayton DSA315-8 ($139.98) (unverified) | SB Acoustics SB17MFC35-8 ($75.90) | Peerless OC25SC65-04 ($35.20) in a home-made ring | **about $251** (plus the ring) | The woofer gives the best 32 Hz fit in 88 L at 90.3 dB. The mid's 88 dB and the tweeter's 93 dB leave room to pad both down to the woofer, and the faceplate-less tweeter is designed for custom waveguide mounting. Cross to the tweeter at about 2.8 to 3 kHz, not 2.2. Swapping in a Dayton DC300-8 woofer is cheaper (price not verified), at f3 33.7 Hz and with less excursion. |
| **Mid** | Dayton DSA315-8 ($139.98) (unverified) | SB Acoustics SB17MFC35-8 ($75.90) | Scan-Speak Illuminator R3004/602200 ($197.20) | **about $413** | The money goes where your design is hardest. The R3004/602200's 420 Hz Fs and 62 mm faceplate make the planned 2.2 kHz crossover realistic, and the low-inductance mid (0.15 mH) is clean up to that point. The Scan-Speak D3004/602200 (Fs 440 Hz, 90.5 dB) is an equal alternative if you can find it in the US. |
| **Premium** | Dayton DSA315-8 ($139.98) (unverified), or DS315-8 (MSRP $149.99) for +0.7 dB and a non-metal cone | SB Acoustics Satori MR16P-8 ($206.60) | Scan-Speak Illuminator R3004/602200 ($197.20) | **about $544** | A dedicated low-distortion midrange (0.11 mH, 165 mm frame, 88 dB) and a very low-Fs small-flange ring dome cover the critical 350 Hz to 20 kHz range. I found no premium 8 ohm 12-inch woofer that fits a 315 mm frame and this box, so the Dayton stays. Upgrade path: the Purifi PTT6.5M08-NFA-01 midrange (90.9 dB), only if your rebate can be opened to about 177 mm. |

All prices are single-unit list prices found during research; shipping is not included. In every set the mid and tweeter are more sensitive than the woofer after baffle-step compensation, so the woofer sets the system sensitivity: expect about 85 to 88 dB at 2.83 V, not 91.

---

## Sources

The URLs below were found and used through web search. Direct page loading was blocked in this environment, so the data are search-engine extracts of these pages.

**Woofers**
- https://www.daytonaudio.com/product/1317/dsa315-8-12-designer-series-aluminum-cone-woofer-8-ohm
- https://loudspeakerdatabase.com/Dayton/DSA315-8
- https://www.daytonaudio.com/product/1059/ds315-8-12-designer-series-woofer-speaker-8-ohm
- https://www.parts-express.com/Dayton-Audio-DS315-8-12-Designer-Series-Woofer-295-434
- https://www.daytonaudio.com/product/34/dc300-8-12-classic-woofer-8-ohm
- https://loudspeakerdatabase.com/Dayton/DC300-8
- https://www.daytonaudio.com/product/123/rss315hfa-8-12-reference-hf-subwoofer-8-ohm
- https://loudspeakerdatabase.com/Dayton/RSS315HFA-8
- https://www.madisoundspeakerstore.com/approx-12-woofers/fostex-fw305-12-woofer/
- http://madisound.com/pdf/fostexdrivers/fw305.pdf
- https://loudspeakerdatabase.com/Fostex/FW305
- https://www.morelhifi.com/product/ticw-1258ft/
- https://loudspeakerdatabase.com/Morel/TiCW_1258Ft
- https://www.parts-express.com/Peerless-830669-12-Paper-Cone-SLS-Subwoofer-264-1118
- https://loudspeakerdatabase.com/Peerless/SLS-P830669
- https://www.madisoundspeakerstore.com/approx-12-woofers/sb-acoustics-sb34nrxl75-8-12-woofer/
- https://sbacoustics.com/product/12-sb34nrxl75-8-norex/
- https://loudspeakerdatabase.com/SB/SB34NRXL75-8
- https://www.scan-speak.dk/product/32w-4878t00/
- https://loudspeakerdatabase.com/ScanSpeak/32W-4878T00
- https://loudspeakerdatabase.com/ScanSpeak/30W-4558T00
- https://www.madisoundspeakerstore.com/approx-12-woofers/

**Midranges**
- https://sbacoustics.com/product/6in-sb17mfc35-8/
- https://sbacoustics.com/wp-content/uploads/2020/02/6in-SB17MFC35-8.pdf
- https://www.madisoundspeakerstore.com/sb-acoustics-woofers-6-7/sb-acoustics-sb17mfc35-8-6-poly-cone-woofer/
- https://loudspeakerdatabase.com/SB/SB17MFC35-8
- https://www.daytonaudio.com/product/1314/dsa175-8-6-1-2-designer-series-aluminum-cone-woofer-8-ohm
- https://www.parts-express.com/Dayton-Audio-DSA175-8-6-1-2-Designer-Series-Aluminum-Cone-Woofer-295-528
- https://sbacoustics.com/product/6%C2%BDin-satori-mr16p-8/
- https://www.madisoundspeakerstore.com/approx-6-midrange/satori-mr16p-8-6-egyptian-papyrus-cone-midrange-8-ohm/
- https://purifi-audio.com/shop/ptt6-5m08-nfa-01-ptt6-5m08-nfa-01-271
- https://www.madisoundspeakerstore.com/approx-6-midrange/ptt6.5m08-nfa-01-6.5-ultra-low-distortion-midrange-8-ohm/
- https://audioxpress.com/article/test-bench-the-ptt6-5m08-nfa-01-6-5-midrange-from-purifi-audio
- https://www.erinsaudiocorner.com/driveunits/purifi_ptt6.5m-08-nfa-01a/
- https://www.madisoundspeakerstore.com/approx-5-midrange/seas-prestige-mca15rcy-h1262-5.5-coated-paper-midrange/
- https://www.seas.no/index.php?option=com_content&view=article&id=77%3Ah1262-08-mca15rcy&catid=46&Itemid=240
- https://www.daytonaudio.com/product/1056/ds175-8-6-1-2-designer-series-woofer-speaker-8-ohm
- https://www.daytonaudio.com/product/22/dc160-8-6-1-2-classic-woofer-8-ohm
- https://loudspeakerdatabase.com/SB/SB17NRX2C35-8
- https://www.daytonaudio.com/product/101/rs180-8-7-reference-woofer-8-ohm
- https://www.scan-speak.dk/product/18m-8631t00/
- https://loudspeakerdatabase.com/ScanSpeak/18M-8631T00
- https://faitalpro.com/en/products/LF_Loudspeakers/product_details/datasheet.php?id=401020100
- https://willys-hifi.com/products/peerless-sds-p830657-6-midwoofer

**Tweeters**
- https://www.scan-speak.dk/product/r3004-602200/
- https://www.madisoundspeakerstore.com/ring-radiator-tweeters/scan-speak-r3004/602200-illuminator-ring-radiator-tweeter/
- https://audioxpress.com/news/scan-speak-launches-updated-illuminator-r3004-602200-1-ring-radiator-tweeter
- https://www.scan-speak.dk/product/d3004-602200/
- https://solen.ca/en/products/scan-speak-illuminator-d3004-602200-26mm-ring-dome-tweeter
- https://www.madisoundspeakerstore.com/auto-tweeters/scanspeak-silver-series-d3004-602006-1-textile-dome-tweeter-each/
- https://www.madisoundspeakerstore.com/scanspeak-soft-dome-tweeters/scanspeak-illuminator-d3004/6020-00-tweeter-textile-dome/
- https://www.erinsaudiocorner.com/driveunits/scanspeak-d3004-602000-tweeter/
- https://hificompass.com/en/speakers/measurements/scan-speak/scanspeak-d3004/602000
- https://www.madisoundspeakerstore.com/soft-dome-tweeters-vifa/peerless-oc25sc65-04-1-textile-dome-tweeter-4-ohm/
- https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6167/OC25SC65-04.pdf
- https://www.digikey.com/en/products/detail/peerless-by-tymphany/OC25SC65-04/6557474
- https://josephcrowe.com/blogs/news/peerless-oc25sc65-04-with-horn-no-1900
- https://www.daytonaudio.com/product/1194/nd25fn-4-1-neo-silk-dome-tweeter-element-4-ohm
- https://www.parts-express.com/Dayton-Audio-ND25FN-4-1-Silk-Dome-Neodymium-Tweeter-Element-4-Ohm-275-053
- https://www.daytonaudio.com/product/1196/nd25fa-4-1-soft-dome-neodymium-tweeter-4-ohm
- https://www.daytonaudio.com/images/resources/275-059--dayton-audio-ND25FA-4-specifications.pdf
- https://www.parts-express.com/Dayton-Audio-ND25FA-4-1-Soft-Dome-Neodymium-Tweeter-275-059
- https://www.parts-express.com/Peerless-NE25VTS-04-1-Silk-Dome-Tweeter-264-1034
- https://www.falconacoustics.co.uk/downloads/Vifa/NE25VTS-04.pdf
- https://www.parts-express.com/Peerless-BC25SC55-04-1-Square-Frame-Tweeter-264-1024
- https://www.madisoundspeakerstore.com/morel-soft-dome-tweeters/morel-mdt12-1-textile-dome-tweeter/
- https://www.parts-express.com/Morel-MDT-12-1-1-8-Neodymium-Tweeter-277-060
- https://www.madisoundspeakerstore.com/hard-dome-tweeter/vifa-dq25sc16-04-1-titanium-dome-tweeter/
- https://www.audiofrog.com/gb10-1-25-mm-audiophile-grade-automotive-tweeter/
- https://www.crutchfield.com/ISEO-rgbtcspd/p_898GB10/Audiofrog-GB10.html
- https://www.madisoundspeakerstore.com/soft-dome-tweeters-sb-acoustics/sb-acoustics-sb21rdcn-c000-4-ring-dome-tweeter-neodymium/
- https://www.madisoundspeakerstore.com/soft-dome-tweeters-scanspeak/scan-speak-r2004/602200-19mm-small-ring-radiator-tweeter/
- https://www.madisoundspeakerstore.com/ring-radiator-tweeters/
- https://www.parts-express.com/Peerless-DX25BG60-04-1-Silk-Dome-Tweeter-4-Ohm-264-1478
- https://www.parts-express.com/Peerless-BC25SC06-04-1-Textile-Dome-Tweeter-264-1028
- https://www.ebay.com/itm/135161832446 (NE25VTA-04 size, 66 mm)
- https://www.falconacoustics.co.uk/morel-et-448-tweeter.html
- https://www.parts-express.com/Morel-MDT-29-1-1-8-Soft-Dome-Tweeter-277-010
- https://www.falconacoustics.co.uk/bliesma-t25a-6.html
- https://www.daytonaudio.com/product/1567/an25f-4-1-soft-dome-neodymium-car-audio-tweeter-pair-4-ohm
- https://www.parts-express.com/HiVi-SD1.1-A-1-Textile-Dome-Tweeter-297-416
- https://www.madisoundspeakerstore.com/hard-dome-tweeter/seas-prestige-22taf/g-h1283-alum/magn.-alloy-22-mm-dome-tweeter/
- https://www.madisoundspeakerstore.com/hard-dome-tweeter/seas-prestige-27tbfc/g-h1212-aluminum/magnesium-dome-tweeter/
- https://www.falconacoustics.co.uk/downloads/Scanspeak/d2010-851300.pdf
- https://www.diyaudio.com/community/threads/small-faceplate-tweeters.344366/ (found; could not be opened)

**Crossover help and community (found in search results)**
- https://madisound.com/library/sb13pfc2508-mdt12-passive-crossover-design/
- https://techtalk.parts-express.com/forum/tech-talk-forum/19390-peerless-sls-830669
- https://diy.midwestaudio.club/discussion/62/dayton-audio-dsa175-8
- https://www.htguide.com/forum/forum/primetime-a-v/mission-possible-diy/driver-testing-discussion/42109-waveguides-for-3d-printers-and-cnc-s/page5

**Gear and software links from prior knowledge.** These were not opened in this session, and their prices are (unverified).
- miniDSP 2x4 HD: https://www.minidsp.com/products/minidsp-in-a-box/minidsp-2x4-hd
- miniDSP UMIK-1: https://www.minidsp.com/products/acoustic-measurement/umik-1
- REW (Room EQ Wizard): https://www.roomeqwizard.com/
- VituixCAD: https://kimmosaunisto.net/Software/Software.html
- XSim: https://sites.google.com/site/xsimulator/
- Dayton Audio DATS V3, DSP-408 and MA1240a: https://www.daytonaudio.com/ (search by model name)
- Hypex FusionAmp FA253: https://www.hypex.nl/
