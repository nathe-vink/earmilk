// One entry per shot in prompts/. Plain data: it is sent into the page as JSON. Positions in metres; lifts and offsets in mm.
export const SIZE = [1800, 1200];

const C2 = { position: [1.7, 1.2, 2.7], lookAt: [0.05, 0.55, 0], focal: 50 };
const C7 = { position: [2.0, 1.3, 3.1], lookAt: [0.15, 0.9, 0], focal: 36 };
const FLAVORS = ['whole', 'two-percent', 'skim', 'chocolate', 'oat'];
const OLD_SLEEVE = { flavor: 'whole', position: [0, 0, 0], state: { cabinet: false, tubeOffset: [1000, 0, -550], tubeRotY: 0.5, lidOffset: [780, -860, -350], lidRotY: 0.6 } };

export const shots = [
  { id: 'shot-01', frames: [
    { suffix: '', room: 'hero', speakers: [{ flavor: 'whole', position: [-1, 0, 0] }, { flavor: 'whole', position: [1, 0, 0] }], camera: { position: [2.4, 1.2, 3.9], lookAt: [0.25, 0.55, 0], focal: 50 } },
  ] },
  { id: 'shot-02', frames: [
    { suffix: 'a', room: 'apartmentBright', speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: C2 },
    { suffix: 'b', room: 'oldRoom', speakers: [{ flavor: 'oat', position: [0, 0, 0] }], camera: C2 },
  ] },
  { id: 'shot-03', frames: [
    { suffix: '', room: 'studio', roomOptions: { key: 'rake', env: 0.45, fill: 0.25 }, ao: { radius: 0.05, scale: 1.4 }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [0.3, 1.0, 0.9], lookAt: [-0.03, 0.885, 0.09], focal: 85 } },
  ] },
  { id: 'shot-04', frames: [
    { suffix: '', room: 'studio', roomOptions: { key: 'back', env: 0.6, groundRoughness: 0.8 }, speakers: [{ flavor: 'whole', position: [0, 0, 0] }], camera: { position: [0, 0.62, -4.2], lookAt: [0, 0.5, 0], focal: 70 } },
  ] },
  { id: 'shot-05', frames: [
    { suffix: '', room: 'studio', roomOptions: { key: 'even', env: 0.5 }, speakers: FLAVORS.map((f, i) => ({ flavor: f, position: [(i - 2) * 0.52, 0, 0] })), camera: { position: [0, 1.5, 8.2], lookAt: [0, 0.5, 0], focal: 100 } },
  ] },
  { id: 'shot-06', frames: [
    { suffix: '', room: 'desk', ao: { radius: 0.04, scale: 1.4 }, speakers: [], crate: { position: [0, 0.72, 0], flavors: ['whole', 'two-percent', 'skim', 'chocolate', 'oat', 'whole'] }, camera: { position: [0.95, 1.32, 1.45], lookAt: [0, 0.82, 0], focal: 70 } },
  ] },
  { id: 'shot-07', frames: [
    { suffix: 'a', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { lidLift: 320 } }], camera: C7 },
    { suffix: 'b', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'whole', position: [0, 0, 0], state: { tubeLift: 1000, lidOffset: [780, -860, -350], lidRotY: 0.6 } }], camera: C7 },
    { suffix: 'c', room: 'studio', roomOptions: { key: 'swap', env: 0.5 }, speakers: [{ flavor: 'oat', position: [0, 0, 0] }, OLD_SLEEVE], camera: C7 },
  ] },
];
