# Explorations

Not shots. Each folder is one design question, rendered with the same model as the shots so proportions stay exact. Nothing here changes the spec until a choice is made; the chosen option then goes to the canvas, `spec/`, `copy/` and the shot briefs together.

    cd render && node render.mjs --list explore --scale 2

## 2026-10-01: more colour on the carton, and the owner's side panel

Question raised after the v3 renders: the cartons read as mostly white, and the side could carry something people choose themselves, in the manner of the old "Have you seen me?" milk-carton panels.

Colour, one lineup each, flavour order left to right:

| File | Look | What it touches in the spec |
|---|---|---|
| `color-wordmark-as-spec.png` | As specified today: wordmark front and side, colour only in the throat. | Nothing. |
| `color-cap.png` | The lid (gable and fin) in the flavour's print colour. | Reopens the Decision "gable and fin are the same colour as the body". |
| `color-band.png` | A 110 mm band of print colour around the base. | The print line in Colorways. |
| `color-rings.png` | Print-colour rings around the woofer and the mid. | The print line in Colorways. |
| `color-side.png` | Both side panels in the print colour, wordmark reversed in the board colour. | The print line in Colorways. |

The side panel, with the lid in colour:

| File | What |
|---|---|
| `decal-side.png` | Whole, from the front-right: "HAVE YOU HEARD ME?", a halftone portrait placeholder, four rows the owner fills in. 300 x 330 mm below the side wordmark. |
| `decal-side-chocolate.png` | The same panel in Chocolate's cream ink. |
| `decal-pair.png` | The hero pair, each with a different panel, to show that the panel is chosen per speaker. |

Panel copy in these renders is placeholder, not approved: the headline is the one proposed; the rows are Name, Heard since, Last heard, If heard call; the footer line is a mock. The portrait is a generated halftone silhouette, not a photo of anyone.

## 2026-10-01, round 2: lids on the white cartons, the band as print or as a stand, wordmark in the band

Direction after round 1: coloured lids, but the darker cartons stay solid; the base band either as a default or as an optional stand; no rings; coloured sides dropped; the wordmark could move into the band; and a question about where physical controls would live.

    cd render && node render.mjs --list explore2 --scale 2

| File | What | What it touches in the spec |
|---|---|---|
| `r2-lineup-lids-white-only.png` | Lid in the print colour on Whole, 2% and Skim; Chocolate and Oat solid as today. | Reopens "gable and fin are the same colour as the body" for the three white flavours only. |
| `r2-lineup-band-logo.png` | Lids as above, a printed 110 mm base band in the print colour, the wordmark reversed in the board colour inside the band on the front and the right side, nothing printed under the gable. | The print line in Colorways, and the as-drawn wordmark placement in `spec/geometry.md`. |
| `r2-lineup-stand-logo.png` | Lids as above, no printed band; instead a separate 110 mm painted stand in the print colour with a 6 mm dark reveal under the carton, the wordmark on the stand. | Adds an object the handoff does not have. Overall height with the stand 1,171 mm; the tweeter axis rises to about 1,020 mm. |
| `r2-band-close.png`, `r2-chocolate-band-close.png` | The printed band close, on Whole and on Chocolate (cream band, brown wordmark). | As above. |
| `r2-stand-close.png` | The stand close: the reveal is what makes it read as a separate block. | As above. |
| `r2-pair-band-panels.png` | The hero pair with lids, printed band and the owner's panel on each. | As above, plus the panel. |
| `r2-whatif-knob-on-stand.png` | A what-if only: one knob on the stand's front. The floorstander is passive by Decision and has no controls; if it ever went active, the stand is where they would live. | Not proposed. |

## 2026-10-02, round 3: milk-carton marks that are not about the owner

Direction: no sleeve, the colour a finish on the birch, the band and the stand one built-in plinth, the wordmark a badge on the front and an engraving on the back, the owner's panel dropped. Asked for: other common milk-themed marks, as long as they are not about the owner. These are proposals, not spec; none of them is on the model by default.

    cd render && node render.mjs --list explore3 --scale 2

| File | What | Where it would live |
|---|---|---|
| `r3-open-other-side.png` | OPEN OTHER SIDE with the arrow, the line every gable-top carries on the slope that is not the spout. Here it points at the bowl. In the gable's other colour (white on Whole's red). | The back slope of the gable. Seen from behind and above, so a room shot would only catch it on the far speaker. |
| `r3-best-before.png` | BEST BEFORE  NEVER as an inkjet date stamp, dot matrix, black. | The front face of the fin, where the date goes on a carton. |
| `r3-grade-a.png` | A stamped roundel: GRADE A over PASTEURIZED · HOMOGENIZED, a big A in the middle, in the accent colour. | The right side, upper third, 130 mm across. The only one of these that puts anything on a side. |
| `r3-shake-well.png` | SHAKE WELL in caps, in the accent colour. | The right side, near the top. |
| `r3-volume.png` | 103 L (27 GAL), the cabinet's gross internal volume from `render/src/check-spec.mjs`, set small under the badge the way the net-contents line sits at the foot of a carton. | The plinth's front, under the badge. |
| `r3-all.png` | OPEN OTHER SIDE, the date stamp, the roundel and the volume line together, from high and to the right, to see how much is too much. | As above. |

Not rendered on purpose: anything with a name, a face, a date the owner fills in, or a phone number.

## 2026-10-02, round 4: the shape of the bare birch field on the back

Asked: must the birch fill the whole back, or only hold the Nutrition Facts, with the port, the posts and the wordmark outside it? Both, straight on and from the rear quarter. The contained field is the default from v9; the full field stays an option with its bottom lifted so the margin above the plinth matches the sides.

    cd render && node render.mjs --list explore4 --scale 2

| File | What |
|---|---|
| `r4-back-label-straight.png`, `r4-back-label-quarter.png` | The field is the Facts panel plus a 26 mm margin; the wordmark engraved on the finish above it, the port and the posts on the finish below. |
| `r4-back-full-straight.png`, `r4-back-full-quarter.png` | The field from 140 above the floor to 30 below the top, 26 in from the sides; everything inside it. |

## 2026-10-02, round 5: the back as decided, and three more marks

OPEN OTHER SIDE (back slope) and SHAKE WELL (by the port) are spec now; the Facts are an engraved bronze plate; the back wordmark is cast letters like the front. The first two frames show that. The rest are new proposals, none about the owner.

    cd render && node render.mjs --list explore5 --scale 2

| File | What | Where it would live |
|---|---|---|
| `r5-back-quarter.png`, `r5-back-close.png` | The back as decided: bronze plate, cast letters, SHAKE WELL under the port, OPEN OTHER SIDE on the slope. | Spec. |
| `r5-keep-room-temperature.png` | KEEP AT ROOM TEMPERATURE, the storage line, true of a speaker. | Right side, under the gable, accent colour. |
| `r5-return-for-deposit.png` | RETURN FOR DEPOSIT, small, reversed in the body colour. | The plinth's right side. |
| `r5-barcode.png` | A barcode whose digits are the spec's own numbers (390, 860, 1055, 103). | Right side, low, where a carton carries it. |
| `r5-all-new.png` | The three together with the two spec marks. | As above. |
