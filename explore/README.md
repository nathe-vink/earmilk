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
