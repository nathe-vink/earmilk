"""earwig: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).
Nothing here is SPEC yet: the owner has not seen earwig.

Bud frame: x toward the head (the inner side), y forward, z up; the bud's body is centred near the origin and the
tail leaves its root downward (-z). The right bud is drawn; the left is its mirror. Case frame: standing on the floor
at z = 0. Since 2026-10-06 (the owner) the tail is a flexible exoskeleton of overlapping plates that hangs loose, like
the earworm's cable, ending in the forceps; the case has no wig, and its lid is split like an earwig's wing covers.
"""

# --- bud body and stem: one loft through ellipses (z, half-width x, half-width y, centre x) (PROPOSAL) ---------------
BUD_TOP = (0.55, 10.5)                 # the loft closes to a point here (x, z): a dome, not a flat cap
BUD_BOTTOM = (-2.0, -13.9)             # and here: a short neck at the tail's root (the stiff stem ran to -28.7 until 2026-10-06)
BUD_SECTIONS = [
    (10.38, 1.0, 0.85, 0.55),
    (10.1, 2.6, 2.2, 0.55),
    (9.4, 5.2, 4.4, 0.6),
    (7.5, 8.4, 7.0, 0.6),
    (4.5, 10.0, 8.4, 0.5),
    (1.0, 10.2, 8.6, 0.3),
    (-2.5, 9.4, 8.0, 0.0),
    (-5.5, 7.2, 6.4, -0.6),
    (-8.0, 4.6, 4.2, -1.4),
    (-10.0, 3.5, 3.0, -1.8),
    (-12.0, 3.2, 2.6, -2.0),
    (-13.2, 2.4, 1.9, -2.0),
]

# --- the tail: a flexible exoskeleton (the owner, 2026-10-06): plates that lap over each other toward the forceps, like the
# earworm's cable or a jointed toy snake, round a soft core, so it hangs loose from the ear and drapes on a table (PROPOSAL)
TAIL_ROOT = (-2.0, 0.0, -12.6)        # where it leaves the body, inside the neck collar
COLLAR_R, COLLAR_LEN = 3.0, 1.4       # a satin collar round the root
TAIL_LEN = 46.0                       # root to the forceps' base, along the tail
TAIL_R0, TAIL_R1 = 2.65, 1.9          # radius at the root and at the forceps
TAIL_PITCH = 2.3                      # one plate every 2.3 mm
TAIL_FLARE = 0.21                     # each plate flares toward its rear lip by this fraction of the radius
FORCEPS_KNOB = (2.5, 2.2, 1.8)        # the last plate, which carries the forceps: half-sizes across, deep, long

SPLIT_X = 1.6                        # the head's parting line: outer half gloss, inner half (nozzle side) satin
SENSOR_AT, SENSOR_AB = (0.0, -3.4), (1.1, 1.6)   # 2026-10-06: the wear sensor's window on the inner half (y, z centre; half-sizes)
SPLIT_ZMIN = -8.0                    # below this the stem stays one piece
SEAM = 0.25

# --- nozzle and ear tip (PROPOSAL; the tip is a bought size: PLACEHOLDER) ---------------------------------------------
NOZZLE_AT = (6.5, 0.8, 2.0)          # where the nozzle's axis leaves the body
NOZZLE_DIR = (0.84, 0.46, 0.28)      # into the canal: inward, forward, a little up
NOZZLE_R = 2.8
NOZZLE_LEN = 6.0                     # beyond NOZZLE_AT
TIP_D = 12.4                         # medium silicone tip (PLACEHOLDER: the tips bought)
TIP_LEN = 7.4

# --- pincers (the forceps): two tapering lofts that bow apart and close at the tips (PROPOSAL) ------------------------
# Drawn in their own frame since 2026-10-06: the knob at the origin, the arms running down -z, spread along y.
PINCER_TOP_Z = -0.6                 # inside the knob
PINCER_LEN_Z = 10.5  # shorter and softer since 2026-10-04 (less grotesque); a touch longer on the thicker tail (10-06)
PINCER_BASE_Y = 1.5                  # each pincer's base, off the tail's centre plane
PINCER_BOW = 2.6                     # how far they bow apart
PINCER_TIP_Y = 0.8                   # tip gap is twice this
PINCER_R0, PINCER_R1 = 1.6, 0.68     # radius at the base and at the tip, which is rounded, not pointed

# --- case (PROPOSAL) --------------------------------------------------------------------------------------------------
CASE_W, CASE_D, CASE_H = 62.0, 26.0, 48.0
CASE_R = 10.0                        # every edge rounded
LID_SPLIT = 0.62                     # the lid's split, as a fraction of the height
LID_GAP = 0.4
# the wing-case lid (the owner, 2026-10-06): the lid in the buds' chestnut, split down the middle front to back like an
# earwig's folded wing covers, each half crowned a little; the base cream (PROPOSAL)
WING_SEAM_W, WING_SEAM_D = 0.6, 0.45 # the centre seam: width and depth
WING_CROWN = 0.9                     # each cover's crown above the lid's flat, at its middle
# The wig (2026-10-04 to 10-05) is gone: the owner did not like the hairy case.
