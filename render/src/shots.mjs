// One entry per shot in prompts/. Plain data: it is sent into the page as JSON. Positions in metres; lifts and offsets in mm.
export const SIZE = [1800, 1200];

const C2 = { position: [0.98, 0.95, 2.95], lookAt: [0.3, 0.6, 0], focal: 50 };   // v15: lower, the speaker left of the centre line;
// v19: more frontal again (about 18 degrees off the axis), so the tweeter sits inside the scoop's opening (round 2 on the bright room)
// v16: a little more frontal (about 25 degrees off the axis, was 32), so the tweeter sits further into the bowl's opening
const C7 = { position: [2.0, 1.05, 3.1], lookAt: [0.15, 0.9, 0], focal: 36 };
const FLAVORS = ['whole', 'two-percent', 'skim', 'chocolate', 'oat'];
const LID_ON_FLOOR = [560, -860, 0]; // clear of the speaker's footprint and of the tube's where it stands in frame c
const OLD_SLEEVE = { flavor: 'whole', position: [0, 0, 0], state: { cabinet: false, tubeOffset: [1000, 0, -550], tubeRotY: 0.5, lidOffset: LID_ON_FLOOR, lidRotY: 0.6 } };

export const shots = [
  { id: 'shot-01', frames: [
    // v11: the pair toed in toward the listening spot, the camera lower on a longer lens so the two read as a pair.
    { suffix: '', room: 'hero', speakers: [{ flavor: 'whole', position: [-1, 0, 0], rotationY: 0.2 }, { flavor: 'whole', position: [1, 0, 0], rotationY: -0.2 }], camera: { position: [2.3, 1.0, 4.4], lookAt: [0.1, 0.55, 0], focal: 57 } },   // v19: the right cabinet off the edge
  ] },
  { id: 'shot-02', frames: [
    { suffix: 'a', room: 'apartmentBright', speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: C2 },
    // 2026-10-02: no sleeve, so no skin change. The same Whole in both rooms until the shot is rebriefed (its point was the swap).
    { suffix: 'b', room: 'oldRoom', speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: C2 },
  ] },
  { id: 'shot-03', frames: [
    // v15 (refinement round 1): key 'bowl' from the front-left into the throat, less ambient, the camera back with the corner in frame
    // v16 (refinement round 2): a soft top light (0.9 m) up and to the left, where the red slope mirrors it, so a highlight band
    // crosses the slope and light reaches the bowl's floor (the concavity read as a void, darker than the faceplate); the crop
    // up and tighter, so the mid driver's rim leaves the bottom edge and the fin stands whole at the top
    // v17 (refinement round 3: tight on the bowl alone it read as a basin; a milky sheen across the red): wide enough for the
    // gable's outline and the fin; the top light a strip box (0.25 x 1.4) further up, so the slope mirrors it as one band above the
    // bowl; a low card in front lighting the bowl's back wall; the key further and smaller. New in the model: the scoop's polished
    // lip and the ring the tweeter seats in
    // v18 (round 1 of the v17 batch: neither hero nor detail, an accidental crop; the driver a lens or an eye; a haze across the
    // slope): back to the brief, gable height (0.97 m) and close, 25 degrees off the axis, so the mouth fills much of the frame and
    // the camera looks along the throat at the tweeter, face on inside the lip, the fin across the top; the mouth on a third; the
    // top strip narrower and further, so the slope mirrors it as a line, not a haze
    // v19 (round 2 of the v17 batch: a wash bleaching the red to salmon; the white body the sweep's value; the bowl's left a murk):
    // a mid-grey set, so the white body stands off it and bounces less into the sides; half the environment, so the slope holds its
    // red beside the strip's band; the card into the bowl brighter and aimed at its far side; the tweeter's seat ring satin metal
    { suffix: '', room: 'studio', roomOptions: { key: 'bowl', env: 0.12, ground: 0xb7b3ac, fill: 0.7, fillPos: [-2.2, 5.2, 0.13], fillSoftbox: [0.12, 1.4], card: { color: 0xffffff, intensity: 9, w: 0.45, h: 0.22, position: [0.06, 0.84, 0.95], lookAt: [-0.05, 0.92, 0.04] } }, ao: { radius: 0.05, scale: 1.4 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { bowlShadow: false } }], camera: { position: [0.36, 0.985, 0.80], lookAt: [0.035, 0.94, 0.07], focal: 62 } },
  ] },
  { id: 'shot-04', frames: [
    // v20 (the owner, 2026-10-07): no bronze plate; the Nutrition Facts printed on the body's finish under the clear, like a carton's
    // panel (spec: back.panel 'print'). The reflector still lights the letters, the posts and the port's flange.
    // v15 (refinement round 1): the key from the camera's right; the dome at half (env, bounce) and the fill down; a reflector card behind the camera that lights
    // only the bronze and the posts, so the plate reads bright against its dark engraving; no edge strips (they filled the shadow and show nothing from straight on)
    { suffix: 'a', room: 'studio', roomOptions: { key: 'back', env: 0.15, fill: 0.2, bounce: 0.06, strips: 0, groundRoughness: 0.8, reflector: { w: 2.0, h: 1.2, radiance: 1.5, behind: 1.0, receivers: ['bronze', 'badgeside', 'post', 'screw', 'portflange'] } }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [0, 0.62, -4.2], lookAt: [0, 0.5, 0], focal: 70 } },
    // v17 (the owner, 2026-10-06): a three-quarter frame beside the straight one, which every critic round asked for: 33 degrees
    // off the back face toward its left side and 10 up, the cabinet on the left third with its shadow running out to the right;
    // the key across from the camera ('back3q'), the fill from the camera's side, the edge strips at a little over half; the
    // reflector card where the plate mirrors it from this camera (low, out to the right), lighting only the metal
    // v18 (round 1 of the v17 batch: the sweep's curve read as a hard horizon behind the carton; a bright patch on the empty floor):
    // the sweep turned to face this camera; the key further onto the back and gridded (see 'back3q')
    // v19 (round 2): the key a stop down, larger and higher (see 'back3q'); the fill from the camera's side up, a bounce for the side;
    // the strips up a little for a rim; the reflector brighter, so the plate reads as metal, not an ochre block
    { suffix: 'b', room: 'studio', roomOptions: { key: 'back3q', env: 0.15, fill: 0.5, fillPos: [-4, 2.5, -3], bounce: 0.06, strips: 0.8, groundRoughness: 0.8, turnSweep: true, reflector: { w: 1.4, h: 0.9, radiance: 2.6, position: [1.57, 0.2, -2.48], aim: [0, 0.64, -0.2], receivers: ['bronze', 'badgeside', 'post', 'screw', 'portflange'] } }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [-2.40, 1.31, -3.69], lookAt: [-0.32, 0.52, 0.21], focal: 70 } },
  ] },
  { id: 'shot-05', frames: [
    // v15 (refinement round 1): the 'lineup' key, a softbox high at the front-left and close enough that the sweep falls a stop
    // below the white fronts; dome, fill and strips down so the sides keep their shade; all five turned the same 7 degrees, the
    // very slight three-quarter the brief allows, so each shows a sliver of its shaded side
    // v16 (refinement round 2): square again (the 7 degree turn plus the lens's spread showed a full side on the left carton and
    // none on the right, a row that twists); a grid on the key and exposure up a little, so the white fronts stand above the
    // floor and the sweep (higher washed the colourways off their hex); the strips up for edges, the fill up as a bounce
    // v17 (refinement round 3: no edge took a line; the letters ghosts on the light plinths): the key further round; the strips
    // brought round to the sides (75 degrees off the camera's line), where a vertical corner mirrors them as a line. In the model,
    // dark bronze letters on Chocolate's and Skim's plinths (the owner, 2026-10-06), and Chocolate's throat dark
    // v18 (round 1 of the v17 batch: cutouts against the grey, a grey halo round every driver): the strips back behind the row's
    // sides (125 degrees off the camera's line) and up, a rim on every silhouette; a smaller key (see 'lineup'); in the model each
    // driver's flange now covers its hole's cut edge, whose eased rim was the halo
    { suffix: '', room: 'studio', roomOptions: { key: 'lineup', env: 0.3, fill: 0.35, strips: 1.1, stripAngle: 125, exposure: 1.1 }, speakers: FLAVORS.map((f, i) => ({ flavor: f, position: [(i - 2) * 0.52, 0, 0] })), camera: { position: [0, 1.3, 11.5], lookAt: [0, 0.5, 0], focal: 140 } },
  ] },
  { id: 'shot-06', frames: [
    // v15 (refinement round 1): the camera down to just above the gable tops (desk + 0.38 m), a shallower three-quarter (14 degrees)
    // on an 85 mm lens, the crate a little left of centre with its shadow in frame, so each woofer sits whole in its window; the
    // wall a warm grey so the white crate and bodies separate from it
    // v16 (refinement round 2): a walnut desk, its planks varying more, so the cream crate and the white pints stand off it
    // (crate, desk and wall sat in one band of warm mid-tones and the crate melted into the desk)
    // v17 (refinement round 3: the shadow sides sat a shade below the fronts while the floor's shadow fell to half): the cool fill,
    // the dome and the environment down; the camera a little higher, so the back row's gables read over the front row
    // v18 (round 1 of the v17 batch: three faces and three rooftops): higher again (about 20 degrees down), so all six read
    // v19 (round 2: the woofers cropped unevenly by their windows; the crate's shaded side as pale as its front): a little lower
    // (about 18 degrees), the pints closer to the crate's walls (see buildCrate), the fill and the dome down
    // v20 (round 3: the pints read inflated, their fins rolled bolsters): the eased edges at the pint's scale, 1.5 mm, not the
    // floorstander's 6 mm, which on a 100 mm carton with a 2 mm fin rounded the corners and the whole fin (no critic round)
    { suffix: '', bevelScale: 100 / 390, room: 'desk', roomOptions: { wall: 0xa49e92, desk: { base: '#6e4f36', dark: '#56402c', light: '#86634a' }, env: 0.22, fill: 0.8, bounce: 0.08 }, ao: { radius: 0.04, scale: 1.4 }, speakers: [], crate: { position: [0, 0.72, 0], flavors: ['whole', 'two-percent', 'skim', 'chocolate', 'oat', 'whole'] }, camera: { position: [0.40, 1.29, 1.42], lookAt: [0.06, 0.845, 0.02], focal: 85 } },
  ] },
];

// Third exploration, 2026-10-02: common milk-carton marks on the finished cabinet, none about the owner. Proposals, not spec.
const MARK_CAM = { position: [2.2, 1.15, 2.0], lookAt: [0.05, 0.5, 0], focal: 50 };
const BACK_CAM = { position: [-1.7, 1.9, -2.1], lookAt: [0.05, 0.58, 0], focal: 50 };
const marked = (marks, camera = MARK_CAM, room = { key: 'even', env: 0.5 }) => ({ room: 'studio', roomOptions: room, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { look: { marks } } }], camera });
export const explore3 = [
  { id: 'r3-open-other-side', ...marked(['open-other-side'], BACK_CAM, { key: 'back', env: 0.6 }) },
  { id: 'r3-best-before', ...marked(['best-before']) },
  { id: 'r3-grade-a', ...marked(['grade-a']) },
  { id: 'r3-shake-well', ...marked(['shake-well']) },
  { id: 'r3-volume', ...marked(['volume'], { position: [1.3, 0.55, 1.2], lookAt: [0.02, 0.12, 0], focal: 70 }) },
  { id: 'r3-all', ...marked(['open-other-side', 'best-before', 'grade-a', 'volume'], { position: [2.1, 1.5, 1.6], lookAt: [0.05, 0.6, 0], focal: 50 }) },
];

// Fourth exploration, 2026-10-02: the shape of the bare birch field on the back. 'label' holds the Facts panel with a 26 mm margin and leaves
// the port, the posts and the engraved wordmark on the finish; 'full' runs from above the plinth to 30 below the top, same margins at the sides.
const BACK_STRAIGHT = { position: [0, 0.62, -4.2], lookAt: [0, 0.5, 0], focal: 70 };
const BACK_QUARTER = { position: [-2.2, 1.3, -2.6], lookAt: [0.05, 0.5, 0], focal: 55 };
const backOpt = (backPanel, camera) => ({ room: 'studio', roomOptions: { key: 'back', env: 0.6, groundRoughness: 0.8 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { backPanel } }], camera });
export const explore4 = [
  { id: 'r4-back-label-straight', ...backOpt('label', BACK_STRAIGHT) },
  { id: 'r4-back-full-straight', ...backOpt('full', BACK_STRAIGHT) },
  { id: 'r4-back-label-quarter', ...backOpt('label', BACK_QUARTER) },
  { id: 'r4-back-full-quarter', ...backOpt('full', BACK_QUARTER) },
];

// Fifth exploration, 2026-10-02: the back with the bronze plate, the cast letters and the two spec marks, and three more mark proposals.
const SIDE_CAM = { position: [2.7, 1.3, 1.5], lookAt: [0.05, 0.5, 0], focal: 50 };
export const explore5 = [
  { id: 'r5-back-quarter', room: 'studio', roomOptions: { key: 'back', env: 0.6, groundRoughness: 0.8 }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: BACK_QUARTER },
  { id: 'r5-back-close', room: 'studio', roomOptions: { key: 'back', env: 0.6, groundRoughness: 0.8 }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [-0.9, 0.95, -1.5], lookAt: [0, 0.66, 0], focal: 70 } },
  { id: 'r5-keep-room-temperature', ...marked(['open-other-side', 'shake-well', 'keep-room-temperature'], SIDE_CAM) },
  { id: 'r5-return-for-deposit', ...marked(['open-other-side', 'shake-well', 'return-for-deposit'], SIDE_CAM) },
  { id: 'r5-barcode', ...marked(['open-other-side', 'shake-well', 'barcode'], SIDE_CAM) },
  { id: 'r5-all-new', ...marked(['open-other-side', 'shake-well', 'keep-room-temperature', 'return-for-deposit', 'barcode'], SIDE_CAM) },
];

// Sixth exploration, 2026-10-07: the scoop's trim. The owner is unsure of the metal ("it looks like a diner"). Four options, each in
// the close-up's frame and nearer in the bright room: the spec's polished lip with the tweeter's bright ring; the lip as spec with the
// tweeter's ring and seat black; the lip in the gable's own lacquer, the ring black; no lip, the ring black. Proposals, not spec.
const TRIM_NEAR = { position: [0.75, 1.35, 1.55], lookAt: [0.02, 0.86, 0.05], focal: 50 };
const BOWL_CLOSE = shots.find(s => s.id === 'shot-03').frames[0];
const trimClose = (scoopTrim) => ({ ...BOWL_CLOSE, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { bowlShadow: false, scoopTrim } }] });
const trimNear = (scoopTrim) => ({ room: 'apartmentBright', speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { scoopTrim } }], camera: TRIM_NEAR });
export const explore6 = ['polished', 'black', 'tone', 'none'].flatMap(t => [{ id: `r6-trim-${t}-close`, ...trimClose(t) }, { id: `r6-trim-${t}-near`, ...trimNear(t) }]);

// Retired 2026-10-02 with the sleeve: the three-frame swap. Kept so `--list retired` can still render it in the sleeve look.
const SLEEVE = { look: { mode: 'sleeve' } };
export const retired = [
  { id: 'shot-07', frames: [
    { suffix: 'a', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { lidLift: 320, ...SLEEVE } }], camera: C7 },
    { suffix: 'b', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { tubeLift: 1000, lidOffset: LID_ON_FLOOR, lidRotY: 0.6, ...SLEEVE } }], camera: C7 },
    { suffix: 'c', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'oat', position: [0, 0, 0], state: SLEEVE }, { ...OLD_SLEEVE, state: { ...OLD_SLEEVE.state, ...SLEEVE } }], camera: C7 },
  ] },
];

// Explorations: not shots. Rendered with `node render.mjs --list explore` into explore/<date>/.
const LINEUP = { position: [0, 1.4, 7.4], lookAt: [0, 0.5, 0], focal: 100 };
const lineup = (style) => ({ room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: FLAVORS.map((f, i) => ({ flavor: f, position: [(i - 2) * 0.52, 0, 0], state: { look: { mode: 'sleeve', style, lid: style === 'cap' ? 'print' : 'board', band: style === 'band' ? 'print' : null, wordmark: 'gable' } } })), camera: LINEUP });
const PANEL_A = { rows: [['Name', '[YOUR NAME]'], ['Heard since', '[DATE]'], ['Last heard', '[YOUR ROOM]'], ['If heard, call', '[YOUR NUMBER]']] };
const PANEL_B = { rows: [['Name', "[A FRIEND'S NAME]"], ['Heard since', '[DATE]'], ['Last heard', 'Side B, loud'], ['If heard, call', '[THEIR NUMBER]']] };
export const explore = [
  { id: 'color-wordmark-as-spec', ...lineup('wordmark') },
  { id: 'color-cap', ...lineup('cap') },
  { id: 'color-band', ...lineup('band') },
  { id: 'color-rings', ...lineup('rings') },
  { id: 'color-side', ...lineup('side') },
  { id: 'decal-side', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { look: { mode: 'sleeve', style: 'cap', lid: 'print', band: null, wordmark: 'gable', panel: PANEL_A } } }], camera: { position: [1.75, 0.95, 1.35], lookAt: [0.05, 0.5, 0], focal: 70 } },
  { id: 'decal-side-chocolate', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'chocolate', position: [0, 0, 0], state: { look: { mode: 'sleeve', style: 'cap', lid: 'print', band: null, wordmark: 'gable', panel: PANEL_B } } }], camera: { position: [1.75, 0.95, 1.35], lookAt: [0.05, 0.5, 0], focal: 70 } },
  { id: 'decal-pair', room: 'hero', speakers: [{ flavor: 'whole', position: [-1, 0, 0], state: { look: { mode: 'sleeve', style: 'cap', lid: 'print', band: null, wordmark: 'gable', panel: PANEL_A } } }, { flavor: 'whole', position: [1, 0, 0], state: { look: { mode: 'sleeve', style: 'cap', lid: 'print', band: null, wordmark: 'gable', panel: PANEL_B } } }], camera: { position: [2.4, 1.2, 3.9], lookAt: [0.25, 0.55, 0], focal: 50 } },
];

// Second round of the colour exploration: lids on the white cartons only, the band as print or as a stand, wordmark in the band.
const WHITE = ['whole', 'two-percent', 'skim'];
const lidFor = f => (WHITE.includes(f) ? 'print' : 'board');
const lineup2 = (lookFor) => ({ room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: FLAVORS.map((f, i) => ({ flavor: f, position: [(i - 2) * 0.52, 0, 0], state: { look: lookFor(f) } })), camera: LINEUP });
const CLOSE = { position: [1.9, 0.8, 1.7], lookAt: [0.05, 0.38, 0], focal: 55 };
const CLOSE_LOW = { position: [1.9, 0.7, 1.7], lookAt: [0.05, 0.33, 0], focal: 55 };
export const explore2 = [
  { id: 'r2-lineup-lids-white-only', ...lineup2(f => ({ lid: lidFor(f) })) },
  { id: 'r2-lineup-band-logo', ...lineup2(f => ({ lid: lidFor(f), band: 'print', wordmark: 'band' })) },
  { id: 'r2-lineup-stand-logo', ...lineup2(f => ({ lid: lidFor(f), band: 'stand', wordmark: 'band' })) },
  { id: 'r2-band-close', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { look: { mode: 'sleeve', lid: 'print', band: 'print', wordmark: 'band' } } }], camera: CLOSE },
  { id: 'r2-stand-close', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { look: { mode: 'sleeve', lid: 'print', band: 'stand', wordmark: 'band' } } }], camera: CLOSE_LOW },
  { id: 'r2-chocolate-band-close', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'chocolate', position: [0, 0, 0], state: { look: { mode: 'sleeve', lid: 'board', band: 'print', wordmark: 'band' } } }], camera: CLOSE },
  { id: 'r2-pair-band-panels', room: 'hero', speakers: [{ flavor: 'whole', position: [-1, 0, 0], state: { look: { mode: 'sleeve', lid: 'print', band: 'print', wordmark: 'band', panel: PANEL_A } } }, { flavor: 'whole', position: [1, 0, 0], state: { look: { mode: 'sleeve', lid: 'print', band: 'print', wordmark: 'band', panel: PANEL_B } } }], camera: { position: [2.4, 1.2, 3.9], lookAt: [0.25, 0.55, 0], focal: 50 } },
  { id: 'r2-whatif-knob-on-stand', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { look: { mode: 'sleeve', lid: 'print', band: 'stand', wordmark: 'band', knob: true } } }], camera: CLOSE_LOW },
];
