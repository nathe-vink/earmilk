# Getting the earmilk speaker parts made (US, one-off build)

Research date: 2026-10-04. Scope: who can make each part from your CAD files, whether they really offer the material and thickness, what file they want, limits, price and lead time. Two speakers.

## Read this first: how the research was done

- **I could not open any web page directly.** The network proxy blocked page fetching, so every fact here comes from search-engine extracts of each service's own pages (or the third-party page named). Treat specs as "listed as of Oct 2026" and confirm them in each service's instant quote before you order.
- **Price labels.** "listed" means the price appeared in the extract of that service's own page. Everything else is marked **(estimate)**. I ran no instant quotes, because that needs your files uploaded.
- **The web-search budget ran out near the end**, so a few small details are inferred from a service's general rules. These are flagged as "verify".
- **Thickness reality check.** US services stock inch sizes. 0.125 in = 3.18 mm, the closest stock size to your 3 mm metal parts. Metric 3.0 mm brass is not a standard US stock size. "3/4 in" Baltic birch is really 18 mm (actual 17.5 to 18.0 mm, about 0.687 to 0.727 in), not 19.05 mm. Tell every wood shop "18 mm Baltic birch" and give them a measured thickness.

## Quick answer: who to use

| Part | Recommended | Backup |
|---|---|---|
| 1. Cabinet panels (18 mm Baltic birch) | Local CNC cabinet or sign shop, or cut it yourself on a makerspace ShopBot | SpeakerHardware Custom Shop (3/4 in Baltic birch flat-packs, 8 to 12 weeks) |
| 2. Gable (3D bowl) | If it will be painted: 3D-print in pieces. If bare wood: local CNC sign/millwork/pattern shop, milled in two halves | JMP Wood (Brooklyn NY / Carteret NJ, 3/4/5-axis) |
| 3. Test slice + port tube | Library/makerspace printer, or Craftcloud (US vendors) | JLC3DP (cheapest, but 40% US tariff on plastics) |
| 4. "earmilk" letters | SendCutSend brass 0.125 in (3.18 mm), hand-polish | OSHCut or Xometry (Xometry also has bronze); Sign Letter Source if you want them pre-polished |
| 5. Nutrition Facts plate | Etched-plaque maker: Woodland Manufacturing, Impact Signs or Saifee Signs | Brass blank from SendCutSend/OSHCut, fiber-laser engraved at a local trophy shop; Front Panel Express |
| 6. Terminal plate | Add it to the SendCutSend letters order (5052 aluminium 0.125 in) | OSHCut / Fabworks (no minimum) / Front Panel Express |
| 7. Paint stencils | Local sign shop, or CraftCuts (adhesive vinyl) | Cut Oramask 813 yourself on a library Cricut |
| 8. Finish | DIY with 2K aerosols if you are patient | Auto-body shop for a true show finish |

---

## 1. Cabinet panels: 18 mm Baltic birch from DXF (about 20 panels, largest about 390 x 860 mm)

**Key finding: none of the big instant-quote sites cut 18 mm plywood.** SendCutSend tops out at 12 mm, Ponoko at about 6 mm, and Fabworks and OSHCut are metal-only. Xometry takes it only as a manual quote. This is a job for a local CNC router shop, a makerspace, or a speaker flat-pack specialist.

| Service | Does it? | Material / thickness | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| SendCutSend | **NO** (no 18 mm) | Baltic birch only 0.125, 0.250, 0.354 (9 mm), 0.472 in (12 mm); MDF up to 0.5 in | DXF, DWG, AI, STEP | Max part 30 x 44 in; routed with a 1/8 in bit (1.6 mm inside-corner radius, 3.2 mm minimum hole) | n/a | n/a | https://sendcutsend.com/materials/baltic-birch-plywood/ |
| Ponoko | **NO** | Birch ply 3.2 and 6.2 mm; max wood 6.7 mm | SVG/DXF | Max sheet 795 x 395 mm | n/a | n/a | https://www.ponoko.com/materials/birch-plywood |
| Fabworks / OSHCut | **NO** (metal only) | Steel, aluminium, stainless (Fabworks); metals only (OSHCut) | n/a | n/a | n/a | n/a | https://www.fabworks.com/services/laser-cutting |
| Xometry | **Partly: manual quote only** | Instant-quote birch ply only 0.125, 0.230, 0.375, 0.500 in; 3/4 in "may be available on request"; CNC-routing page lists Baltic birch | STEP, DXF | Routed parts up to 80 x 48 x 24 in | Manual quote, no public price | CNC routing 3 to 7 business days (listed); manual review adds time | https://www.xometry.com/capabilities/cnc-machining-service/cnc-routing/ |
| SpeakerHardware Custom Shop | **Yes** (speaker specialist) | Only 15-ply 3/4 in (18 mm) and 12-ply 1/2 in Baltic birch | Send your plans; they redraw for their CNC | Flat-pack only (no assembly) | Their stock flat-packs listed at $249.95 to $449.95; custom pair about $300 to $700 **(estimate)** | Custom flat-packs by email: 8 to 12 weeks (listed) | https://www.speakerhardware.com/custom-shop/ |
| SpeakerParts.co | Yes (custom flat-packs) | 0.75 in / 20 mm MDF or Baltic birch | SketchUp .skp or SVG (convert your DXF) | Location not confirmed | Stock packs from $90 (listed); custom work "contact for price" | Not listed | https://speakerparts.co/collections/flat-packs-for-diy-speaker-cabinets-mdf-plywood-speakerparts-co |
| Local CNC cabinet or sign shop | **Yes (best fit)** | Their stock or your sheets; ask for 18 mm Baltic birch | DXF, one layer per operation/depth (through-cut, pocket depth X) | 4 x 8 ft routers are common; holes, pockets and rebates are routine | Forum-reported rates: pro cabinet shops $100 to $150/h, small shops $75 to $100/h with $40 to $50 minimums, hobbyists about $50 to $60/h; a 3-hole baffle about $75 to $100. Whole job about $300 to $900 for cutting plus plywood **(estimate)** | 1 to 3 weeks **(estimate)** | https://techtalk.parts-express.com/forum/tech-talk-forum/1381923-anyone-still-need-cnc-cutting |
| Makerspace with a ShopBot 4 x 8 router | Yes (you cut) | Bring your own sheets | DXF; you do the toolpaths (VCarve, Fusion) | Needs a training class first | Examples (listed): Maker Works, Ann Arbor: $99 3-hour ShopBot class plus $110/month membership; Yakima Maker Space: $30/h; Ace Makerspace: $6 per hour or $50 per day | Your schedule | https://www.maker-works.com/class-wood-shopbot |

Ruled out: Chop Shop CNC is in the UK and Woodsat is in China. Both came up in searches but neither is practical for a US one-off.

**Recommended path.** Email your DXFs to two or three local CNC cabinet or sign shops (search "CNC routing" plus your city, or ask a makerspace who they use). Ask for a price that includes the plywood. In the email:

- Say it is 18 mm metric Baltic birch and give a measured thickness, so rebates and grooves fit.
- Put each operation on its own DXF layer (through-cut, or pocket at a stated depth).
- Ask how they handle square inside corners on the rectangular cutouts, since router bits leave a small radius.

If you'd rather do it yourself, take a makerspace ShopBot class (about $100) and cut the panels there. If you can wait two to three months and want a speaker specialist, use SpeakerHardware's custom shop.

---

## 2. The gable: laminated birch block with a concave bowl (STEP, 3D milling) or a 3D-printed alternative

**Key finding: most online machining services do not mill wood.** Protolabs doesn't stock wood. Fictiv lists no wood among its standard certified materials. Xometry accepts it only as "Other" material through engineering review. Real options are a local CNC shop with 3D carving software, a millwork shop, or 3D printing.

| Service | Does it? | Material | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| Protolabs | **NO** | Stocks 30+ plastics and metals; wood not offered | STEP | n/a | n/a | n/a | https://www.protolabs.com/materials/ |
| Fictiv | **Not standard** (custom quote at best) | Wood not among standard certified CNC materials | STEP | n/a | Quote | n/a | https://www.fictiv.com/capabilities/cnc-machining-services |
| Xometry | **Partly** (choose "Other" material, engineering review) | Plywood via routing partners | STEP | 3-axis up to 60 in | Manual quote; likely several hundred dollars or more per gable **(estimate)** | Routing 3 to 7 days (listed) plus review time | https://www.xometry.com/capabilities/cnc-machining-service/ |
| JMP Wood (Brooklyn NY / Carteret NJ) | **Yes** (3-, 4- and 5-axis CNC millwork) | Wood; you can supply a glued-up Baltic birch blank | STEP or STL (ask) | Custom quotes via team@jmpwood.com | Quote; about $400 to $1,200 per gable **(estimate)** | Quote | https://www.jmpwood.com/pages/custom-cnc-millwork-machining-5-axis |
| Made To Spec / Brown Wood Inc (IL, OH, ME) | **NO for one-offs** | 5-axis, 5 x 10 ft beds | n/a | Minimum 25 to 50 pieces | n/a | 2 to 8 weeks | https://brownwoodinc.com/mts/products_category/cnc-and-shaping/ |
| Local CNC sign, millwork or foundry-pattern shop | **Yes (usual route)** | Glue-up of 18 mm Baltic birch (supply it yourself to save cost) | STEP or STL | 3-axis in two halves needs a long-reach ball-nose bit; 5-axis is rare in small shops | $75 to $150/h; about 4 to 8 h including programming, so about $400 to $1,200 per gable **(estimate)** | 1 to 4 weeks **(estimate)** | (rates: Parts Express TechTalk threads, see Sources) |
| JLC3DP (3D print) | Yes | FDM up to 550 x 480 x 480 mm (fits in one piece), but PLA-P only up to 250 x 250 x 300 mm; SLA up to 780 x 780 x 530; MJF max 370 x 276 x 360 (too small) | STL, STEP | Ships from China; 40% US tariff on plastic prints (DDP, since Mar 2026); SLA or MJF of a solid ~9 L block is expensive | FDM gable is about 2.5 to 3 kg of plastic: about $150 to $400 plus shipping and tariff **(estimate)** | FDM build about 3 days, plus shipping | https://jlc3dp.com/help/article/3d-printing-design-guideline |
| Craftcloud (3D print marketplace, 180+ vendors) | Yes | FDM PLA/PETG and others | STL, OBJ, STEP (35+ formats) | Max size depends on vendor | US FDM "large" parts run $150 to $500+ (third-party range) **(estimate)** | Vendor-dependent | https://craftcloud3d.com/ |
| Xometry FDM (3D print) | Yes | Stratasys FDM up to 24 x 36 x 36 in | STL, STEP | n/a | Instant quote | Small parts from 1 day; large about 1 week | https://www.xometry.com/capabilities/3d-printing-service/fused-deposition-modeling/ |
| DIY print at a makerspace | Yes | PLA/PETG | STL | Common 256 mm printers mean 4+ pieces to glue | About $60 to $80 of filament per gable **(estimate)** | 2 to 4 days of printing | (none) |

**Recommended path.**

1. Print the test slice (part 3) first to prove the bowl shape.
2. **If the gables will be painted** like the rest of the cabinet, 3D-print them. Glue the pieces, fill, prime with 2K high-build primer and paint. This is the cheapest and most predictable route.
3. **If you want real plywood,** glue up blanks from 18 mm Baltic birch and ask a local CNC sign, millwork or foundry-pattern shop (or JMP Wood) to mill each gable in two halves on a 3-axis router with a long ball-nose bit. Send the STEP file and say the cavity depth per half.

Cost-saving tip for the CNC route: the shop can 2D-cut each 18 mm layer with an oversize bowl opening before glue-up. Then only a 3D finishing pass is needed, which saves machine time. This changes how the block is made, not the design.

---

## 3. Small 3D prints: test slice (about 250 x 250 x 150 mm) and flared port tube (100 mm bore, 160 mm long)

| Service | Does it? | Material / size | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| Library or makerspace printer | Yes | PLA/PETG | STL | The slice needs a bed of 256 mm or more (e.g., Bambu X1/P1 is a 256 mm cube; Prusa XL and Creality K1 Max are larger) | Filament only, about $15 to $40 for everything **(estimate)** | Days | (none) |
| Craftcloud | Yes | Many US/EU vendors; FDM, SLA, MJF | STL, OBJ, STEP | Size depends on vendor | Slice about $50 to $200; port tube about $25 to $60 each **(estimate)** | Vendor-dependent | https://craftcloud3d.com/ |
| JLC3DP | Yes | PLA-P to 250 x 250 x 300 (slice just fits); MJF nylon to 370 x 276 x 360; SLA resin to 780 x 780 x 530 | STL, STEP | 40% US tariff on plastics; international shipping | "From $0.30" (listed, tiny parts only); slice about $40 to $150, port about $15 to $50 **(estimate)** | About 3-day FDM build, plus shipping | https://jlc3dp.com/help/article/us-tariff-policy-faq |
| Xometry | Yes | FDM, SLA, MJF | STL, STEP | n/a | Small prototypes "$5 to $50" (listed generic range); the slice will cost more **(estimate)** | 1 to 3 business days for small parts | https://www.xometry.com/capabilities/3d-printing-service/ |
| PCBWay | Yes | FDM to 600 x 500 x 500 mm; SLA to 2100 x 800 x 700 mm | STL, STEP | Ships from China | Quote | Resin 5 to 10 business days | https://www.pcbway.com/rapid-prototyping/3d-printing/ |

US FDM service-bureau rule of thumb (third-party guide): about $0.05 to $0.15 per gram plus $3 to $10 setup per part.

**Recommended path.** Print both at a library or makerspace if one has a large enough printer. Otherwise upload the STLs to Craftcloud and pick a US vendor (no tariff, faster). Use PETG or ASA rather than PLA for the port tube, since PLA softens around 55 to 60 C, for example in a hot car (general knowledge).

---

## 4. Metal letters: "earmilk" in 2.5 to 3 mm brass or bronze, polished, stud-mounted (4 sets = 28 letters plus 4 i-dots)

| Service | Does it? | Material / thickness | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| SendCutSend | **Yes for brass; NO bronze** | Brass 260 H02: 0.040, 0.063, **0.125 in (3.18 mm)**, 0.187, 0.250; also 5052 aluminium 0.125 | DXF, DWG, AI, STEP | Minimum part 0.25 x 0.375 in, so **the i-dot may be too small: check its size**; minimum hole about 50% of thickness (about 1.6 mm); bridges at least 0.030 in; **no polishing** (ships mill finish, may have scratches); tumbling is for deburring and gives brass an "antiqued" look; $39 order minimum | Instant quote; about $4 to $10 per letter **(estimate)** | Ships in 2 to 4 business days; free shipping over $39 | https://sendcutsend.com/materials/brass/ |
| OSHCut | **Yes** | Brass 260: 0.016 to 0.25 in, including 0.093 (2.36 mm) and 0.125 (3.18 mm); Brass 353 at 0.125; **Bronze 220 only up to 0.09 in (2.3 mm)**; silicon bronze 655 only 0.0625 | DXF or STEP | No minimum order; smaller minimum part sizes than SendCutSend (partial data, verify) | Instant quote, similar to SendCutSend **(estimate)** | 2 business days standard | https://www.oshcut.com/materials |
| Xometry | **Yes (brass and bronze)** | Brass 260/353/464 at 0.032 to 0.250 in, including 0.125; Bronze 220/510/932/655 at 0.020 to 0.125 in | DXF, STEP | No minimum; free US shipping | Instant quote | From 3 days | https://www.xometry.com/capabilities/sheet-cutting/ |
| Sign Letter Source | Yes (sign-letter maker) | Waterjet-cut C280 brass 1/8 to 3/4 in; polished, brushed or patina, with protective clear coat | Your vector art | Letters from 1 in tall | From $29.70 per letter (listed base) | Not listed | https://www.signlettersource.com/sign-letters/metal-letters/cut-metal/brass.php |
| Gemini (via Gemini Letters Direct or a sign shop) | **Partly** | Brass C280 1/8 to 3/4 in; bronze C220 1/8 to 1/2 in | Vector art | **1/8 in letters can't be drilled and tapped.** Welded studs only on letters 3 in or taller with a 1/2 in or wider stroke; **smaller 1/8 in letters are "plain mount" (adhesive) only.** Includes a paper pattern | From $34.90 per letter (listed) | Not listed | https://hub.geminimade.com/knowledge/flat-cut-metal-product-specifications |
| Impact Signs | **NO at 3 mm** | Brass letters only 1/4 to 1/2 in thick; polished costs +50% | Upload via quote form | n/a | Quote | n/a | https://www.impactsigns.com/sign-letters/cut-brass/ |
| Ponoko | **NO** | Brass max 1.6 mm | n/a | n/a | n/a | n/a | https://www.ponoko.com/laser-cutting/metal/brass |
| Fabworks | **NO brass** | Aluminium, steel and stainless only | n/a | n/a | n/a | n/a | https://www.fabworks.com/resources/materials/sheet/aluminum |

**Recommended path.**

1. Order from SendCutSend in brass 0.125 in (3.18 mm, the nearest stock size to 3 mm). Use one closed outline per part, with the i-dot as its own part. Order quantity 4 of each letter.
2. If the i-dot fails SendCutSend's 0.25 x 0.375 in minimum, cut the dots at OSHCut or Xometry.
3. For **bronze**, use Xometry (bronze up to 0.125 in). OSHCut's bronze 220 stops at 0.09 in (2.3 mm).
4. Polish by hand with a buffing wheel and compound (SendCutSend suggests Mothers Mag & Aluminum Polish), then seal against tarnish with Everbrite ProtectaClear.
5. If you'd rather receive them polished and clear-coated, Sign Letter Source cuts 1/8 in brass from your vector file, at a much higher price.

See "Mounting the letters" below.

---

## 5. Brass or bronze "Nutrition Facts" plate: 318 x 312 x 3 mm, 3 mm corner radius, fine engraving or etch with dark fill (2 plates)

The text goes down to about 2 mm tall, so you need chemical etching, a fiber laser, or fine milled engraving. Ordinary laser-cutting services can't do this.

| Service | Does it? | Material / thickness | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| Woodland Manufacturing | **Yes** | Chemically etched brass (bronze also offered); recessed areas filled with automotive-grade paint, whole plaque clear-coated | Vector art; digital proof emailed | Custom size by quote | From $194 (listed); a 12.5 in square plate about $250 to $450 **(estimate)** | Proof in 2 to 3 business days; about 3 to 4 weeks total (listed) | https://www.woodlandmanufacturing.com/engraved-brass-plaque.html |
| Impact Signs | **Yes** | Etched brass, bronze or stainless; paint-filled in solid or multi-colour; described as suited to small text | Upload via quote form | n/a | Custom metal plaques from $169 (listed); brass memorial plaques from $217 (listed) | Not listed | https://www.impactsigns.com/plaques/custom-metal-plaques/ |
| Saifee Signs (Houston, ships nationwide) | **Yes** | Etched brass 1/16, 1/8, 3/16 or 1/4 in; any custom shape; Pantone paint match | Vector or line art | Up to 36 x 72 in | From $212 (listed) | Not listed | https://saifeesigns.net/ss-off-the-shelf-sign-shop-houston/p/etched-brass-plaques |
| Front Panel Express (Seattle) | **Yes** (milled engraving with paint infill) | Aluminium 2, 2.5, 3 or 4 mm (anodized or powder-coated); brass, copper and bronze up to 6 mm | Free Front Panel Designer software (.fpd); imports DXF and HPGL artwork (per their manuals) | Engraving cutters down to 0.2 mm; max panel 1100 x 800 mm | The software shows the exact price. Gallery examples (listed): 370 x 320 x 2.5 mm anodized panel $173.06; 73 x 97 x 2 mm brass panel $64.27. Your plate about $200 to $500 each **(estimate)** | US standard shipping about 5 business days | https://www.frontpanelexpress.com/products |
| Local trophy or engraving shop (fiber laser), with a blank from SendCutSend or OSHCut | **Yes** | Brass 0.125 in blank (12.52 x 12.28 in fits SendCutSend's 30 x 44 in max) | SVG, PDF or DXF to the shop | Needs a **fiber** laser (a CO2 laser can't engrave bare brass; general knowledge). Ask whether the laser covers about 300 mm or tiles the job. Darken with Birchwood Casey Brass Black, or paint-fill and wipe | Blank about $50 to $100 plus engraving about $75 to $250 each **(estimate)** | 1 to 2 weeks **(estimate)** | https://sendcutsend.com/faq/do-you-offer-laser-etching-or-laser-engraving/ |
| SendCutSend | **NO engraving** | Only a faint single-line etch on aluminium and steel (not brass), "not cosmetic"; they refer customers to trophy and engraving shops | n/a | n/a | n/a | n/a | https://sendcutsend.com/faq/do-you-offer-laser-etching-or-laser-engraving/ |
| OSHCut | **Partly** | Laser "engrave lines" along contours | DXF with engrave lines | Line engraving works for rules and boxes, but text would come out as outlines only, so it is not suited to 2 mm text (verify) | Instant quote | 2 days | https://www.oshcut.com/design-guide/dxf-for-laser-cutting |

**Recommended path.**

- **Easiest and most reliable:** send the SVG to an etched-plaque maker (Woodland Manufacturing, Impact Signs or Saifee Signs). Specify brass (or bronze), 1/8 in thick, 318 x 312 mm, 3 mm corner radius, black paint fill and clear coat. Chemical etching handles 2 mm text and hairlines easily.
- **Cheaper:** order two 318 x 312 mm brass blanks (0.125 in, with the corner radius cut in) from SendCutSend or OSHCut. Have a local trophy shop with a fiber laser engrave them, then darken with Brass Black or a black paint wash and clear-coat.
- **If aluminium is acceptable:** Front Panel Express gives an exact price in its free software before you order.

---

## 6. Terminal plate: 128 x 64 mm, 3 mm aluminium or brass, two binding-post holes (2 plates)

| Service | Does it? | Material / thickness | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| SendCutSend | **Yes** | 5052 aluminium 0.125 in (3.18 mm), or brass 0.125 | DXF, DWG, AI, STEP | $39 order minimum, so combine with the letters order; anodizing and powder coat available | Their 5052 page lists a generic pricing example of $9.41 per part; about $8 to $15 each **(estimate)** | 2 to 4 business days | https://sendcutsend.com/materials/5052-aluminum/ |
| OSHCut | **Yes** | 5052 aluminium 0.125 in: minimum hole 0.0625 in (0.125 recommended); max part 119 x 59 in | DXF, STEP | No minimum order | Instant quote | 2 business days | https://www.oshcut.com/materialdetails/aluminum-5052-h32 |
| Fabworks | **Yes (aluminium only)** | 5052 aluminium 0.032 to 0.250 in | DXF, STEP | No minimum; powder coat adds 5 to 7 days | Instant quote | Ships in 1 to 2 business days | https://www.fabworks.com/resources/general/faq |
| Front Panel Express | **Yes** | True 3 mm aluminium, anodized or powder-coated; can engrave and paint-fill +/- labels | .fpd (free software) | n/a | About $25 to $50 each **(estimate)** | About 5 business days shipping | https://www.frontpanelexpress.com/products |

**Recommended path.** Add the two plates to the SendCutSend letters order, in aluminium or brass. If you want engraved, colour-filled "+" and "-" markings and an anodized colour, use Front Panel Express.

---

## 7. Paint stencils: two short lines of capitals, 27 mm and 26 mm tall, sprayed onto a lacquered panel

Adhesive vinyl stencils are the right tool. The centres of letters like A, O and R stay in place without bridges, and low-tack film (Oramask 813, a 3 mil translucent blue film made for smooth, flat, rigid surfaces) peels off cleanly.

| Service | Does it? | Material | File format | Limits that matter | Price | Lead time | URL |
|---|---|---|---|---|---|---|---|
| Local sign shop | **Yes** | Oramask 813 or similar | SVG, EPS or PDF with text converted to outlines | n/a | About $15 to $40 **(estimate)** | Same day to a few days **(estimate)** | (none) |
| CraftCuts | **Yes** | Adhesive vinyl stencil, no bridges needed | Stencil-ready vector file (otherwise artwork prep from $15) | n/a | Priced by letter height: about $1.03 (1.5 in) up to $20.59 (28 in) (listed) | Not listed | https://www.craftcuts.com/adhesive-stencil.html |
| Stencil Planet | Yes | One-time-use adhesive vinyl | Choose from 100 fonts (own artwork not confirmed) | n/a | Base $10 (listed) | Not listed | https://stencilplanet.com/products/custom-lettering-stencil-vinyl |
| Create N Sip | Yes | Oramask 813, cut, weeded and transfer-taped | Choose design and size; proof emailed | Sizes from 10 in, max width 22 in | From $3 (listed) | Up to 48 h processing (listed) | https://creatensip.com/shop/single-use-adhesive-vinyl-stencil-or-decal/ |
| DIY: library or makerspace Cricut | Yes | Oramask 813 film from USCutter, Amazon and others | SVG | n/a | A roll about $10 to $25 **(estimate)** | Your time | https://uscutter.com/ORAMASK-813-Paint-Mask-Stencil/ |

**Recommended path.** Send the SVG (text converted to outlines) to a local sign shop or CraftCuts, or cut it yourself on a library Cricut.

- Apply the stencil only after the lacquer is fully cured, and burnish the edges.
- A light first mist of clear seals the stencil edge, so any bleed is clear. This is a common sign-painting technique.
- Spray light coats, then lift the stencil while the paint is still soft.
- Clear-coat over the lettering if you want it protected.

---

## 8. Finishing: glass-smooth solid colours (white body, red #C62828 base)

### Options

| Option | What you get | Cost | Notes | URL |
|---|---|---|---|---|
| Auto-body shop | 2K primer, basecoat, 2K clear, then cut and buff: the best gloss and durability | One forum report: $300 to $400 just to paint speaker tops, brought in disassembled. Full pair plus gables about $800 to $2,500 **(estimate)** | Bring bare, sanded parts. Ask for 2K primer over the wood. Masking two colours costs extra | https://audiokarma.org/forums/threads/what-to-use-to-paint-speakers-glossy-piano-black-tops.502093/ |
| Furniture-finishing shop | Sprayed pre-catalyzed or catalyzed lacquer | Furniture refinishing averages $637 per piece (range $341 to $939, HomeAdvisor); the pair about $500 to $1,500 **(estimate)** | Usually less glossy and less durable than automotive 2K | https://www.homeadvisor.com/cost/home-design-and-decor/refinish-furniture/ |
| DIY with 2K aerosols | Near-automotive finish if you wet-sand and polish | About $500 to $1,200 for both cabinets: roughly 16 to 26 cans plus a respirator and abrasives **(estimate)** | Isocyanates: a NIOSH-approved respirator with organic-vapour cartridges is mandatory | See product rows below |

### DIY products (listed prices)

| Product | Use | Price | Notes | URL |
|---|---|---|---|---|
| SprayMax 2K Clear Glamour (high gloss) | Clear coat | $24.22 to $38.99 depending on seller ($18.95 at one seller) | Pot life about 48 h after activation; about 0.5 to 0.75 m² per can at 2 to 3 coats | https://www.66autocolor.com/products/spray-max-2k-high-gloss-glamour-clear-coat-aerosol |
| Eastwood 2K AeroSpray High Gloss Clear | Clear coat | $39.99 | Can be wet-sanded and polished like gun-sprayed 2K | https://www.eastwood.com/ew-2k-aerosol-high-gloss-clear.html |
| Eastwood 2K AeroSpray High Build Urethane Primer | Filling plywood grain, block sanding | From $39.99 | Gray or black | https://www.eastwood.com/2k-aerospraytm-high-build-urethane-primer-gray-black.html |
| Custom-colour 1K basecoat aerosol (66autocolor) | Colour coat under 2K clear | $35.77 per can (listed for Pantone matching; ask about RAL) | Basecoat must be clear-coated | https://www.66autocolor.com/products/pantone-custom-color-aerosol-1k-basecoat |
| SprayMax 2K single-stage, custom-mixed | Colour and gloss in one product, no clear needed | Quote | Mixed to your colour code | https://www.66autocolor.com/products/spray-max-2k-single-stage-aerosol-spray-paint |

**Warning:** don't put 2K clear over generic hardware-store enamel. It can lift or wrinkle. Use an automotive basecoat designed to be clear-coated, applied within its recoat window. Sources: https://www.porphis-online.com/blogs/technical-guides/can-you-spray-2k-clear-coat-over-1k-base-coat and https://www.nonpaints.com/en/blog/post/can-2-component-automotive-paint-be-sprayed-over-1-component-car-spray-paint

DIY sequence:

1. Fill the plywood grain and edges.
2. Spray 2K high-build primer and block-sand at 320 to 400 grit. Repeat until flat.
3. Spray the colour basecoat. Mask for the two colours.
4. Spray 2 to 3 coats of 2K clear.
5. Let it cure, wet-sand from 1500 up to 3000 grit, then polish.

### Colour matching a hex code

- **A hex code is a screen colour, not a paint formula.** Paint stores match physical samples. Pick from a physical RAL chip or fan deck, and approve a sprayed test card before painting the cabinets.
- **Red #C62828:** the nearest RAL is **RAL 3028 Pure red**. Published screen values for RAL 3028 vary (RGB about 204, 44, 36, or #CC2C24). Source: https://www.schemecolor.com/hex/c62828
- **"Pure white" body:** RAL 9010 is named "Pure white" but is actually warm and slightly creamy. For a crisp white use **RAL 9016 Traffic white** (cool, bright) or **RAL 9003 Signal white** (neutral).
- **Where to get RAL colours mixed:**
  - Automotive paint suppliers, for basecoat in aerosols: O'Reilly custom mixing at 500+ locations; LVP Paints, custom-matched aerosols in 0 to 3 working days; Johnson Supply.
  - MyPerfectColor lists RAL 3028 aerosol from $9.99. That is probably the smallest size, and it is a 1K acrylic enamel, so it is not ideal under 2K clear.

**Recommended path.** If you want truly glass-smooth with little risk, get quotes from two auto-body shops. Bring the cabinets bare and sanded, and specify 2K primer, RAL 9016 or 9003 and RAL 3028 basecoat, 2K clear, then cut and buff. If you DIY, use the sequence above, outdoors or in a ventilated space, wearing the respirator.

---

## Mounting the letters on studs

**What the sign trade does.** Letters are normally drilled and tapped on the back for threaded studs. The installer tapes a paper pattern to the wall, punches and drills the stud holes slightly oversize, dry-fits the letters, then fills the holes with epoxy or silicone and presses the letters in, taping them in place until cured.

Gemini says 1/8 in letters cannot be drilled and tapped. They weld studs only on letters 3 in or taller with a 1/2 in or wider stroke, and **mount smaller 1/8 in letters with adhesive only.** Your letters are 3 mm thick and under 2 in tall, so pins are a DIY method. Keep them decorative and indoor.

**DIY pin method (what to buy and do):**

1. **Pins:** 1/16 in (1.6 mm) solid brass rod, K&S, 3 pieces of 12 in for $4.99 (listed). Or 3/32 in (2.4 mm) at $4.99 for one piece. Cut pins about 10 to 15 mm long. Use 2 per letter, 3 on the "m", and 1 on each i-dot.
2. **Blind holes in the letters:** drill only to about half the thickness, about 1.5 mm, with a drill press and depth stop, so the polished face doesn't distort. Sign makers drill pin holes "at half the depth" (Signs101). Scuff the pins.
3. **Fix the pins.** Use one of:
   - **3M Scotch-Weld DP420** epoxy: about 20 min working time, handling strength in about 2 h, full cure in 24 h. Needs the Duo-Pak dispenser.
   - **Devcon Plastic Steel:** about 4,500 psi shear strength, sets in 1 h, cures in 16 h.
   - **J-B Weld Original.**
   - Or **soft-solder** the pins with 60/40 solder and flux. Clean, roughened surfaces matter, and avoid overheating, which discolours and softens brass.
4. **Polish and seal** the letters (Everbrite ProtectaClear) before mounting.
5. **Drilling template:**
   - Paper option: print the letter DXF at 1:1 with pin centres marked, and check the scale with a ruler.
   - Acrylic option: since you need 4 identical sets, a laser-cut acrylic template with pin holes (makerspace laser or any online laser service) is worth it and reusable.
   - Tape the template on the finished panel, level it, and punch the hole centres.
6. **Drill the cabinet:** holes slightly larger than the pins (e.g., 2 mm for 1.6 mm pins), about 10 mm deep, then blow out the dust. Dry-fit every letter.
7. **Glue in:** fill the holes with epoxy, press the letters home, and tape them until cured. Put low-tack tape around the area first to protect the lacquer.

---

## Buying 18 mm Baltic birch (5 x 5 ft sheets) in small quantities

Rough quantity: about 3 to 4 sheets for the panels of both cabinets, plus about 1 sheet for the two gable glue-ups (each gable is about 9 layers of 18 mm, up to 390 x 390 mm), plus a spare **(estimate; depends on your cut list)**.

| Source | What | Price | Notes | URL |
|---|---|---|---|---|
| Cherokee Wood Products (Southern California) | 3/4 in Baltic birch, full 60 x 60 in sheet cut into packs (e.g., 2 pcs at 24 x 60, 6 pcs at 20 x 30) | $90 on sale, regular $105 (listed) | Own delivery fleet in CA, NV, AZ and UT; oversize shipping by quote | https://www.cherokeewood.com/store/3-4-baltic-birch-plywood-cut-to-size/ |
| The Wood & Shop (woodnshop.net) | 3/4 x 60 x 60 in ("cutting required" to ship) | $154 (listed) | n/a | https://woodnshop.net/products/baltic-birch-plywood-3-4-x-60-x-60-cutting-required.html |
| Rockler (stores nationwide) | 3/4 in Baltic birch 5 x 5 | About $99.99 per a third-party report; sales 20 to 30% off **(estimate)** | Check local store stock | https://toolsradar.com/rockler-baltic-birch-uncovering-ideal-pricing-for-woodworkers/ |
| Woodworkers Source (Arizona, ships) | 3/4 in Baltic birch pre-cut packs, choose size | Not captured | Ships nationwide | https://www.woodworkerssource.com/plywood/34-baltic-birch-plywood-pack-choose-your-size.html |
| MakerStock (PA and UT warehouses) | Baltic birch 3 to 18 mm, stock sizes up to 24 x 48 in, plus cut-to-size | From $1.25 for small pieces; $12 flat shipping per 50 lb box; custom cuts in 2 to 4 business days (listed) | 24 x 48 in blanks cover your largest 390 x 860 mm panel | https://makerstock.com/products/baltic-birch-plywood |
| Local hardwood or plywood dealer | Full 5 x 5 sheets, B/BB grade | Usually cheapest, about $80 to $150 per sheet **(estimate)** | Most will rip sheets to fit your car | (none) |
| Home Depot / Lowe's | Generally not true Baltic birch in 5 x 5 | Their 3/4 in 4 x 8 "PureBond birch" at $82.78 is a different product with fewer plies | Not recommended for this build | https://www.homedepot.com/b/Lumber-Composites-Plywood/3-4/Birch/N-5yc1vZbqm7Z1z0mcq7Z1z11dkr |

Measure each sheet's real thickness before CNC work. 18 mm Baltic birch varies by about ±0.5 mm, so a groove cut for 3/4 in (19.05 mm) will be loose. Source: https://bertastore.com/blogs/hub/baltic-birch-thickness-chart

---

## Rough budget for both speakers' fabricated parts (excluding drivers and electronics)

All figures are **(estimates)**. They exclude binding posts, glue, plywood delivery and tax.

| Part | DIY-heavy | Middle path | Everything outsourced |
|---|---|---|---|
| 1. Panels, including 3 to 4 sheets of plywood | $450 (makerspace) | $1,000 (local CNC shop) | $1,700 |
| 2. Gables x2 | $150 (print yourself) | $600 (print service) | $2,600 (CNC-milled wood, including blanks) |
| 3. Test slice + 2 port tubes | $30 | $150 | $350 |
| 4. Letters x4 sets, plus pins, epoxy, polish, clear | $200 | $350 | $1,600 (sign-letter maker, pre-polished) |
| 5. Nutrition plates x2 | $300 (blank + trophy shop) | $700 (etched-plaque maker) | $1,000 |
| 6. Terminal plates x2 | $20 | $40 | $100 |
| 7. Stencils | $10 | $20 | $40 |
| 8. Finishing | $550 (2K aerosols + respirator) | $800 | $2,500 (auto-body shop) |
| **Total** | **about $1,700** | **about $3,650** | **about $9,900** |

**Bottom line:** about $1,700 to $9,900 for the pair, with a sensible middle path around $3,500 to $4,000 (all estimates). The biggest swings are the gables (printed vs CNC-milled wood) and the paint (DIY vs body shop).

---

## Sources

Part 1: cabinet panels and plywood
- https://sendcutsend.com/materials/baltic-birch-plywood/
- https://sendcutsend.com/guidelines/cnc-routing/
- https://sendcutsend.com/services/cnc-routing/
- https://sendcutsend.com/materials/mdf/
- https://www.ponoko.com/materials/birch-plywood
- https://www.ponoko.com/laser-cutting/wood
- https://www.fabworks.com/services/laser-cutting
- https://www.oshcut.com/materials
- https://www.xometry.com/capabilities/cnc-machining-service/cnc-routing/
- https://www.xometry.com/sheet-cutting/standard-sheet-sizes/
- https://www.xometry.com/capabilities/sheet-cutting/
- https://www.xometry.com/capabilities/cnc-machining-service/cnc-cutting-service/
- https://www.speakerhardware.com/custom-shop/
- https://speakerhardware.com/simplexx-18-flat-pack-subwoofer.php
- https://www.speakerhardware.com/anthology-ii-tower-flat-pack.php
- https://www.speakerhardware.com/titan-48-sub-flat-pack.php
- https://speakerparts.co/collections/flat-packs-for-diy-speaker-cabinets-mdf-plywood-speakerparts-co
- https://techtalk.parts-express.com/forum/tech-talk-forum/1381923-anyone-still-need-cnc-cutting
- https://techtalk.parts-express.com/forum/tech-talk-forum/62677-advice-on-finding-wood-cnc-shop-or-hobbyist-to-cut-parts
- https://techtalk.parts-express.com/forum/tech-talk-forum/52342-cnc-baffle-cutting-service
- https://techtalk.parts-express.com/forum/tech-talk-forum/41472-cabinet-baffle-cnc-service
- https://www.maker-works.com/class-wood-shopbot
- https://www.maker-works.com/membership-old
- https://www.yakimamakerspace.org/CNC-Router-Table
- https://www.acemakerspace.org/product/cnc-router-use-fees/
- https://www.fablabs.io/labs/fablabtacoma
- https://www.fablabs.io/labs/makersedgemakerspace
- https://fabfoundation.org/
- https://chopshopcnc.com/contact (UK, ruled out)
- https://woodsat.com/about-us/ (China, ruled out)
- https://bertastore.com/blogs/hub/baltic-birch-thickness-chart
- https://sawmillcreek.org/showthread.php?261849-Rabbeting-bits-sized-for-baltic-birch-plywood=
- https://www.cherokeewood.com/store/3-4-baltic-birch-plywood-cut-to-size/
- https://woodnshop.net/products/baltic-birch-plywood-3-4-x-60-x-60-cutting-required.html
- https://toolsradar.com/rockler-baltic-birch-uncovering-ideal-pricing-for-woodworkers/
- https://www.woodworkerssource.com/plywood/34-baltic-birch-plywood-pack-choose-your-size.html
- https://makerstock.com/products/baltic-birch-plywood
- https://www.homedepot.com/b/Lumber-Composites-Plywood/3-4/Birch/N-5yc1vZbqm7Z1z0mcq7Z1z11dkr

Part 2: gable
- https://www.protolabs.com/materials/
- https://www.protolabs.com/services/cnc-machining/
- https://www.fictiv.com/capabilities/cnc-machining-services
- https://www.fictiv.com/articles/cnc-materials-series-common-materials-used-in-cnc-projects
- https://www.xometry.com/capabilities/cnc-machining-service/
- https://www.xometry.com/capabilities/cnc-machining-service/cnc-milling-service/
- https://www.jmpwood.com/pages/custom-cnc-millwork-machining-5-axis
- https://www.jmpwood.com/pages/about/
- https://brownwoodinc.com/mts/products_category/cnc-and-shaping/
- https://brownwoodinc.com/about-us/

Parts 2 and 3: 3D printing
- https://jlc3dp.com/help/article/3d-printing-design-guideline
- https://jlc3dp.com/capabilities
- https://jlc3dp.com/3d-printing/fused-deposition-modeling
- https://jlc3dp.com/3d-printing/stereolithography
- https://jlc3dp.com/help/article/us-tariff-policy-faq
- https://jlc3dp.com/news/materials-finishing-pricing-update-july2026
- https://jlc3dp.com/blog/3d-printing-cost
- https://craftcloud3d.com/
- https://support.craftcloud3d.com/en/articles/24-understanding-prices-on-craftcloud
- https://www.xometry.com/capabilities/3d-printing-service/
- https://www.xometry.com/capabilities/3d-printing-service/fused-deposition-modeling/
- https://www.xometry.com/capabilities/3d-printing-service/large-scale/
- https://www.pcbway.com/rapid-prototyping/3d-printing/
- https://www.pcbway.com/rapid-prototyping/3D-Printing/3D-Printing-FDM.html
- https://www.pcbway.com/rapid-prototyping/3D-Printing/3D-Printing-SLA.html
- https://3dprinting.com/how-much-does-3d-printing-cost/
- https://3dprintbounty.com/blog/3d-printing-filament-cost
- https://3dservicesusa.com/services/fdm

Part 4: letters and mounting
- https://sendcutsend.com/materials/brass/
- https://sendcutsend.com/blog/brass-vs-bronze/
- https://sendcutsend.com/laser-cutting-guidelines
- https://sendcutsend.com/faq/what-are-best-practices-for-minimum-geometry/
- https://sendcutsend.com/faq/what-are-your-material-size-limits/
- https://sendcutsend.com/materials/processing-min-max/
- https://sendcutsend.com/faq/do-you-offer-polishing-and-mirror-finishes/
- https://sendcutsend.com/faq/will-there-be-scratches-on-my-parts/
- https://sendcutsend.com/services/tumbling/
- https://sendcutsend.com/shipping/
- https://sendcutsend.com/pricing/
- https://sendcutsend.com/sendcutsend-processing-times/
- https://www.oshcut.com/minimum-maximum-material-sizes
- https://www.oshcut.com/materialdetails/brass-353
- https://www.oshcut.com/materialdetails/bronze-510-h08-spring
- https://www.oshcut.com/materialdetails/silicon-bronze-655
- https://www.oshcut.com/faq
- https://oshcut.com/laser-metal-cutting
- https://www.oshcut.com/osh-cut-vs-send-cut-send
- https://jiga.io/articles/oshcut-vs-sendcutsend-differences/
- https://www.xometry.com/capabilities/sheet-cutting/metal-laser-cutting/
- https://www.ponoko.com/laser-cutting/metal/brass
- https://www.ponoko.com/materials/yellow-brass
- https://www.fabworks.com/resources/materials/sheet/aluminum
- https://www.signlettersource.com/sign-letters/metal-letters/cut-metal/brass.php
- https://www.signlettersource.com/blog/install-instructions-stud-flatcut-metal.pdf
- https://www.signlettersource.com/blog/cut-metal-install-stud-mount-letters.php
- https://hub.geminimade.com/knowledge/flat-cut-metal-product-specifications
- https://geminimade.com/wp-content/uploads/FLAT-CUT-METAL-WELDED-STUDBOSS-MOUNT_3_23_22.pdf
- https://geminimade.com/wp-content/uploads/FLAT-CUT-METAL-STUD-MOUNT_3_23_22.pdf
- https://www.geminilettersdirect.com/gemini-flat-cut-brass-letters
- https://www.geminilettersdirect.com/gemini-flat-cut-bronze-letters
- https://www.impactsigns.com/sign-letters/cut-brass/
- https://www.alphabetsigns.com/signs/brass-letters.html
- https://www.woodlandmanufacturing.com/articles/guides/how-to-stud-mount-metal-letters/
- https://www.officesigncompany.com/dimensional-signs-stud-mount-installation/
- https://www.signs101.com/threads/pin-letters-how-you-tap-holes.152930/
- https://ksmetals.com/collections/brass-rod
- https://www.3m.com/3M/en_US/p/d/b5005321028/
- https://www.gluegun.com/blogs/adhesive-reviews/11722121-the-ultimate-guide-to-3m-epoxy-selection
- https://metalfusionpro.com/what-product-is-better-than-jb-weld/
- https://orchid.ganoksin.com/t/soldering-broach-pins-without-annealing/45058
- https://davidneat.wordpress.com/2015/05/03/a-quick-guide-to-soldering-brass/
- https://www.everbritecoatings.com/brass

Part 5: plate
- https://www.woodlandmanufacturing.com/engraved-brass-plaque.html
- https://www.woodlandmanufacturing.com/engraved-bronze-plaque.html
- https://www.impactsigns.com/plaques/custom-metal-plaques/
- https://www.impactsigns.com/plaques/brass-memorial/
- https://www.impactsigns.com/etched-bronze-brass-plaques/
- https://saifeesigns.net/ss-off-the-shelf-sign-shop-houston/p/etched-brass-plaques
- https://saifeesigns.net/ss-off-the-shelf-sign-shop-houston/p/etched-bronze-plaques
- https://www.frontpanelexpress.com/products
- https://www.frontpanelexpress.com/inspiration
- https://www.frontpanelexpress.com/faq
- https://www.frontpanelexpress.com/fpd-doc/en/fpd_elements_engraving.htm
- https://docs.frontpanelexpress.com/new_file/main_plate.html
- https://docs.frontpanelexpress.com/design_tips/manufacturing_constraints.html
- https://www.frontpanelexpress.com/downloads/manuals/FPE/HPGL-Engravings.pdf
- https://sendcutsend.com/faq/do-you-offer-laser-etching-or-laser-engraving/
- https://www.oshcut.com/design-guide/dxf-for-laser-cutting
- https://www.oshcut.com/tutorials/working-through-design-warnings
- https://www.rextrophies.com/product/laser-engraved-brass-plates/
- https://www.birchwoodcasey.com/products/brass-black-touch-up.html
- https://engraverscafe.com/threads/blackening-engravings.1697/

Part 6: terminal plate
- https://sendcutsend.com/materials/5052-aluminum/
- https://www.oshcut.com/materialdetails/aluminum-5052-h32
- https://www.fabworks.com/resources/general/faq
- https://www.fabworks.com/services/powder-coating

Part 7: stencils
- https://www.craftcuts.com/adhesive-stencil.html
- https://www.craftcuts.com/custom-stencil.html
- https://stencilplanet.com/products/custom-lettering-stencil-vinyl
- https://creatensip.com/shop/single-use-adhesive-vinyl-stencil-or-decal/
- https://www.etsy.com/market/custom_vinyl_stencil
- https://www.stencilease.com/products/custom-stencils
- https://uscutter.com/ORAMASK-813-Paint-Mask-Stencil/
- https://signwarehouse.com/blogs/content/basic-guide-to-stencil-mask-use
- https://makerspace.aapld.org/equipment/technology/cricut/
- https://guides.lib.unc.edu/library-makerspace/cricut

Part 8: finishing and colour
- https://www.66autocolor.com/products/spray-max-2k-high-gloss-glamour-clear-coat-aerosol
- https://www.tptools.com/SprayMax-2K-Clear-Glamour-118-oz,9682.html
- https://download.kwasny.com/datasheets/TMB-3680061_(US)EN.pdf
- https://carxplorer.com/spraymax-2k-clear-coat-review/
- https://www.eastwood.com/ew-2k-aerosol-high-gloss-clear.html
- https://www.eastwood.com/2k-aerospraytm-high-build-urethane-primer-gray-black.html
- https://www.66autocolor.com/products/pantone-custom-color-aerosol-1k-basecoat
- https://www.66autocolor.com/products/spray-max-2k-single-stage-aerosol-spray-paint
- https://www.porphis-online.com/blogs/technical-guides/can-you-spray-2k-clear-coat-over-1k-base-coat
- https://www.nonpaints.com/en/blog/post/can-2-component-automotive-paint-be-sprayed-over-1-component-car-spray-paint
- https://audiokarma.org/forums/threads/what-to-use-to-paint-speakers-glossy-piano-black-tops.502093/
- https://techtalk.parts-express.com/forum/tech-talk-forum/66331-best-black-finish
- https://www.homeadvisor.com/cost/home-design-and-decor/refinish-furniture/
- https://woodweb.com/knowledge_base/Pricing_for_Cabinet_Finishing.html
- https://www.schemecolor.com/hex/c62828
- https://encycolorpedia.com/e72512
- https://www.myperfectcolor.com/paint/384159-ral-3028-pure-red-paint
- https://www.myperfectcolor.com/RAL-Color-Matches-in-Spray-Paint/3547.htm
- https://lakgruppen.com/blog/ral-9010-and-other-shades-of-white
- https://tintrio.nl/en/blog/White-and-bright-which-shade-of-white-to-pick
- https://www.oreillyauto.com/store-services/custom-paint-mixing
- https://www.lvppaints.com/custom-matched-12-oz-aerosol-spray-paint.html
- https://www.johnsonautobodysupply.com/custom-paint.html
