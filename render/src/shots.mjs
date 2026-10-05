// One entry per shot in prompts/. Plain data: it is sent into the page as JSON. Positions in metres; lifts and offsets in mm.
export const SIZE = [1800, 1200];

const C2 = { position: [1.45, 0.95, 2.9], lookAt: [0.4, 0.6, 0], focal: 50 };   // v15: lower, the speaker left of the centre line;
// v16: a little more frontal (about 25 degrees off the axis, was 32), so the tweeter sits further into the bowl's opening
const C7 = { position: [2.0, 1.05, 3.1], lookAt: [0.15, 0.9, 0], focal: 36 };
const FLAVORS = ['whole', 'two-percent', 'skim', 'chocolate', 'oat'];
const LID_ON_FLOOR = [560, -860, 0]; // clear of the speaker's footprint and of the tube's where it stands in frame c
const OLD_SLEEVE = { flavor: 'whole', position: [0, 0, 0], state: { cabinet: false, tubeOffset: [1000, 0, -550], tubeRotY: 0.5, lidOffset: LID_ON_FLOOR, lidRotY: 0.6 } };

export const shots = [
  { id: 'shot-01', frames: [
    // v11: the pair toed in toward the listening spot, the camera lower on a longer lens so the two read as a pair.
    { suffix: '', room: 'hero', speakers: [{ flavor: 'whole', position: [-1, 0, 0], rotationY: 0.2 }, { flavor: 'whole', position: [1, 0, 0], rotationY: -0.2 }], camera: { position: [2.3, 1.0, 4.4], lookAt: [0.0, 0.55, 0], focal: 60 } },
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
    { suffix: '', room: 'studio', roomOptions: { key: 'bowl', env: 0.28, fill: 0.9, fillPos: [-1.5, 3.2, 0.6], fillSoftbox: 0.9 }, ao: { radius: 0.05, scale: 1.4 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { bowlShadow: false } }], camera: { position: [0.5, 1.08, 1.03], lookAt: [-0.06, 0.93, 0.1], focal: 100 } },
  ] },
  { id: 'shot-04', frames: [
    // v15 (refinement round 1): the key from the camera's right; the dome at half (env, bounce) and the fill down; a reflector card behind the camera that lights
    // only the bronze and the posts, so the plate reads bright against its dark engraving; no edge strips (they filled the shadow and show nothing from straight on)
    { suffix: '', room: 'studio', roomOptions: { key: 'back', env: 0.15, fill: 0.2, bounce: 0.06, strips: 0, groundRoughness: 0.8, reflector: { w: 2.0, h: 1.2, radiance: 1.5, behind: 1.0, receivers: ['bronze', 'badgeside', 'post', 'screw', 'portflange'] } }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [0, 0.62, -4.2], lookAt: [0, 0.5, 0], focal: 70 } },
  ] },
  { id: 'shot-05', frames: [
    // v15 (refinement round 1): the 'lineup' key, a softbox high at the front-left and close enough that the sweep falls a stop
    // below the white fronts; dome, fill and strips down so the sides keep their shade; all five turned the same 7 degrees, the
    // very slight three-quarter the brief allows, so each shows a sliver of its shaded side
    // v16 (refinement round 2): square again (the 7 degree turn plus the lens's spread showed a full side on the left carton and
    // none on the right, a row that twists); a grid on the key and exposure up a little, so the white fronts stand above the
    // floor and the sweep (higher washed the colourways off their hex); the strips up for edges, the fill up as a bounce
    { suffix: '', room: 'studio', roomOptions: { key: 'lineup', env: 0.3, fill: 0.35, strips: 0.8, exposure: 1.1 }, speakers: FLAVORS.map((f, i) => ({ flavor: f, position: [(i - 2) * 0.52, 0, 0] })), camera: { position: [0, 1.3, 11.5], lookAt: [0, 0.5, 0], focal: 140 } },
  ] },
  { id: 'shot-06', frames: [
    // v15 (refinement round 1): the camera down to just above the gable tops (desk + 0.38 m), a shallower three-quarter (14 degrees)
    // on an 85 mm lens, the crate a little left of centre with its shadow in frame, so each woofer sits whole in its window; the
    // wall a warm grey so the white crate and bodies separate from it
    // v16 (refinement round 2): a walnut desk, its planks varying more, so the cream crate and the white pints stand off it
    // (crate, desk and wall sat in one band of warm mid-tones and the crate melted into the desk)
    { suffix: '', room: 'desk', roomOptions: { wall: 0xa49e92, desk: { base: '#6e4f36', dark: '#56402c', light: '#86634a' } }, ao: { radius: 0.04, scale: 1.4 }, speakers: [], crate: { position: [0, 0.72, 0], flavors: ['whole', 'two-percent', 'skim', 'chocolate', 'oat', 'whole'] }, camera: { position: [0.413, 1.10, 1.437], lookAt: [0.06, 0.865, 0.02], focal: 85 } },
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
