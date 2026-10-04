"""earwig: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).
Nothing here is SPEC yet: the owner has not seen earwig.

Bud frame: x toward the head (the inner side), y forward, z up; the bud's body is centred near the origin and the
stem hangs down -z. The right bud is drawn; the left is its mirror. Case frame: standing on the floor at z = 0.
"""

# --- bud body and stem: one loft through ellipses (z, half-width x, half-width y, centre x) (PROPOSAL) ---------------
BUD_TOP = (0.55, 10.5)                 # the loft closes to a point here (x, z): a dome, not a flat cap
BUD_BOTTOM = (-2.0, -28.7)             # and here: the stem's end is rounded between the forceps
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
    (-13.0, 3.2, 2.5, -2.0),
    (-20.0, 3.1, 2.4, -2.0),
    (-26.0, 3.0, 2.3, -2.0),
    (-27.5, 2.6, 1.95, -2.0),
    (-28.4, 1.5, 1.1, -2.0),
]
STEM_GROOVES = (-12.6, -16.0, -19.4, -22.8)   # the abdomen's segments: shallow grooves round the stem
GROOVE_W, GROOVE_D = 0.6, 0.11

SPLIT_X = 1.6                        # the head's parting line: outer half gloss, inner half (nozzle side) satin
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
PINCER_TOP_Z = -26.0                 # inside the stem's end
PINCER_LEN_Z = 14.5
PINCER_BASE_Y = 1.45                 # each pincer's base, off the stem's centre plane
PINCER_BOW = 3.7                     # how far they bow apart
PINCER_TIP_Y = 0.35                  # tip gap is twice this
PINCER_R0, PINCER_R1 = 1.55, 0.3     # radius at the base and at the tip

# --- case (PROPOSAL) --------------------------------------------------------------------------------------------------
CASE_W, CASE_D, CASE_H = 62.0, 26.0, 48.0
CASE_R = 10.0                        # every edge rounded
LID_SPLIT = 0.62                     # the lid's split, as a fraction of the height
LID_GAP = 0.4

# --- the wig (PROPOSAL) -----------------------------------------------------------------------------------------------
HAIR_COUNT = 30000
HAIR_RADIUS = 0.035                  # 70 micron strands, doll-hair scale
HAIR_VOLUME = (0.3, 3.2)             # how far strands float off the lid, min to max
HAIR_CUT_BELOW_SPLIT = 1.8           # a bob, cut just below the lid's edge
