# 12 in woofers without a metal cone, for the floorstander (2026-10-10)

The owner asked on 2026-10-10 for a non-aluminium woofer that is performant and in keeping with the carton. The
spec already draws black paper cones (spec/geometry.md); the RSS315HF-4's aluminium cone was the exception.

**Method.** Search-result excerpts only. WebFetch could not reach any of the pages, so every figure comes from snippets
quoting makers' datasheets and retailers: toutlehautparleur, Soundimports, Falcon, Willys and loudspeakerdatabase.
Where sources disagree, both figures are noted.

**Box figures.** These come from a lumped vented-box model at 1 m in half space, with QL 7 and no room gain. The maximum
SPL is on the FA253's 250 W channel: about 31.6 V into 4 ohm, or about 40 V into 8 ohm. It also respects each driver's
Xmax and power rating.

**Baseline.** In 81 L at 32 Hz the RSS315HF-4 gives f3 28 Hz with a +2.9 dB hump at 39 Hz, and about 30 Hz with the
hump EQ'd flat.

## The candidates

| | model | cone | Z (Re) | Fs | Qts | Vas | Xmax | Sd | sensitivity | power | cut-out / frame / depth | price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SB Acoustics SB34NRXL75-8 | Norex paper, black | 8 (6.2) | 22 | 0.28 | 205 L | ±10 | 508 cm² | 91 dB/2.83 V | 200 W | 305.2 / 346 / 146, behind a 13 mm flange | EUR 281-310 (TLHP, Soundimports); Madisound $337.70 |
| 2 | Scan-Speak Revelator 32W/4878T00 | paper sandwich, foam core, black | 4 (3.1) | 18 | 0.32 | 207.5 L | ±14 | 531 cm² | 90 dB/2.83 V | 350 W | about 290.5 / 320 / about 161 overall (from the T01) | GBP 519.95 (Falcon); EUR 699.95 |
| 3 | Visaton TIW 300-8 | black cellulose (paper) | 8 (5.4) | 25 | 0.28 | 160 L | ±7.5 | 510 cm² | 90 dB/1 W | 300 W | 288 / 329 / 143 (149 overall) | GBP 364 (Bax); EUR 327-370 (TLHP, SOS) |
| 4 | SB Acoustics SB34SWNRX-S75-6 | Norex paper | 6 (4.5) | 19 | 0.32 | 164 L | ±11 | 508 cm² | 88 dB/2.83 V | 200 W | about 305 / 346.2 / 156 | EUR 190-230 |
| 5 | ETON 12-612/C8/62 RP | ribbed paper | 8 (6.2) | 28-30 | 0.32 | 134 L | ±9 | 515 cm² | about 91.4 dB/1 W | 150 W | 282 / 331 / not found | EUR 249.95 |
| 6 | SB Acoustics Satori WO24P-4 (9.5 in) | papyrus, the mid's finish | 4 (3.3) | 28 | 0.40 | 71 L | ±8.5 | 255 cm² | 91 dB/2.83 V | 90 W | 209.3 / 242 / 116.4 | about EUR 218-223 |

## In the floorstander's 81 L

| | in 81 L at 32 Hz | best tuning | DSP | max SPL at 25 / 30 / 40 Hz (RSS 104.6 / 110.5 / 114.3) |
|---|---|---|---|---|
| 1 SB34NRXL75-8 | f3 33 Hz, flat | 30-32 Hz, as built | +5-6 dB shelf at 35 Hz: f3 about 29-30 Hz | 104.4 / 109.4 / 114.1 (the amplifier runs out first) |
| 2 32W/4878T00 | f3 30, +2.8 dB hump at 43 Hz | 26-27 Hz (the port about 1.4-1.5 times longer) | at 32 Hz, -3 dB PEQ at 43 Hz: f3 about 31.6 | 104.9 / 110.2 / 115.6 |
| 3 TIW 300-8 | f3 33.5, flat | 31-32 Hz, as built | +5-6 dB shelf: f3 about 29-30 | 102.7 (Xmax) / 110.3 / 114.4 |
| 4 SB34SWNRX-S75-6 | f3 29, +2.9 dB hump at 41 Hz | 25 Hz: f3 about 26, flat | its Le 3.0 mH droops 3-5 dB by 300-400 Hz | 104.0 / 109.6 / 114.4 |
| 5 ETON 12-612 | f3 about 36-37, overdamped | 33-34 Hz | needs +6-8 dB | 103.5 / 108.0 / 112.3 |
| 6 WO24P-4 | f3 28.6 | 26 Hz | | 97.8 / 106.5 / 109.7 |

## What it means for the face

The face comparison is in `renders/2026-10-10/woofer-faces.png`. It is built with `EARMILK_WOOFER=<key>`
(params.WOOFER_OPTIONS).

Each driver sits flush, its frame in a rebate and a printed ring over the frame, so the ring's outside equals the
frame:

- RSS315HF-4: 314, the ring about 12 mm wide.
- 32W/4878T00: 320 (17 mm).
- TIW 300-8: 329 (24 mm).
- SB34NRXL75-8: 346 (33 mm), with 22 mm of the 390 face left each side.

The SB34's 13 mm flange, if the snippet is right, needs a 17 mm rebate in the 18 mm baffle. That leaves 1 mm under it.
Its flush detail would have to change: a doubled baffle locally, or the frame on the face with a deeper ring.

## Recommendation (the owner decides: the frame is a SPEC figure, drawn at about 310)

- **The research agent's pick: SB34NRXL75-8.**
  - Its Qts 0.28 and Vas 205 L call for almost exactly this box: flat at 32 Hz with no change to the port.
  - Its maximum output is within about 1 dB of the RSS.
  - Its midbass is cleaner: a 93 g cone against 188 g, and no metal breakup.
  - It shares the Norex paper cone of the bookshelf's woofer.
  - Against it: its 346 frame is the largest change to the face, and its thick flange may not fit the flush detail.
- **Mine: Visaton TIW 300-8.**
  - It is flat in the box as built.
  - It is within 2 dB of the RSS at 25 Hz and level with it above 30 Hz.
  - Its 6 mm flange suits today's flush detail.
  - Its 329 frame changes the face less than the SB34's.
  - It costs about half the Scan-Speak.
- **If the face must not move: Scan-Speak 32W/4878T00.** Its 320 frame is nearest the drawing and it has the deepest
  bass, at about EUR 700 each.
- **Every candidate is black.** No performant white or cream 12 in was found: SB's natural-colour Satori stops at
  7.5 in. The milk stays in the cabinet's finish.

## Rejected

- **Metal cones:** RSS315HO-4, 30W/4558T00, Purifi PTT10.0, Seas L26ROY and L26RFX/P.
- **Too boomy in 81 L:** Peerless SLS-P830669 and XXLS-P830845.
- **Wants an open baffle or a very large box:** SB34NRX75-6.
- **Pure subwoofer:** SB34SWPL76-4.
- **Poor value:** 32W/8878T11 and Volt RV3143.
- **Pro 12s that want small, high-tuned boxes:** B&C 12NW76, Faital 12RS1066 and 12FH520.

## Sources

- **SB34NRXL75-8**
  - [sbacoustics.com](https://sbacoustics.com/?p=2986)
  - [datasheet PDF](https://www.audioclub.ro/cs-content/cs-docs/9069-1583243220.pdf)
  - [toutlehautparleur](https://en.toutlehautparleur.com/speaker-sb-acoustics-sb34nrxl75-8-impedance-8-ohm-12-inch.html)
  - [loudspeakerdatabase](https://loudspeakerdatabase.com/SB/SB34NRXL75-8)
  - [Soundimports](https://www.soundimports.eu/en/sb-acoustics-sb34nrxl75-8.html)
  - [Madisound](https://www.madisoundspeakerstore.com/approx-12-woofers/sb-acoustics-sb34nrxl75-8-12-woofer/)
- **32W/4878T00**
  - [Falcon datasheet](https://www.falconacoustics.co.uk/downloads/Scanspeak/32w-4878t00.pdf)
  - [Falcon](https://falconacoustics.co.uk/scanspeak-32w-4878t00-subwoofer-revelator-range.html)
  - [Soundimports](https://www.soundimports.eu/scan-speak-32w-4878t00.html)
  - [the T01's dimensions](https://www.soundimports.eu/scan-speak-32w4878t01.html)
- **TIW 300-8**
  - [datasheet (Mouser)](https://mouser.com/datasheet/2/700/TIW_300_1364-3461249.pdf)
  - [loudspeakerdatabase](https://loudspeakerdatabase.com/VISATON/TIW300-8)
  - [toutlehautparleur](https://en.toutlehautparleur.com/haut-parleur-visaton-tiw-300-8-ohm-12-95-inch.html)
  - [Bax](https://www.bax-shop.co.uk/12-inch-speakers/visaton-tiw-300-8-ohm)
- **The others**
  - [SB34SWNRX-S75-6](https://sbacoustics.com/?p=1175)
  - [ETON 12-612](https://loudspeakerdatabase.com/ETON/12-612C8-62RP)
  - [WO24P-4](https://sbacoustics.com/?p=1170)
  - [RSS315HF-4](https://daytonaudio.com/product/121/rss315hf-4-12-reference-hf-subwoofer-4-ohm)
  - [FA253](https://masori.de/en/products/fa253)
