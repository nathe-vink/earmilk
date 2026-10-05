"""earworm: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).
Nothing here is SPEC yet. Wired in-ear earphones since 2026-10-04 (the owner's call); the over-ear version is in git
history and in renders/over-ear/.

Each earbud's own frame: x along the barrel, from its back face (x = 0) toward the nozzle; the worm leaves the back
(x < 0). The splitter's frame: x along its barrel, from the main cable's end (x = 0) to the branches' end.
"""

# --- earbuds: a short barrel, a gunmetal back cap with the burrow, a graphite front shell, a nozzle (PROPOSAL) -------
BUD_LEN = 17.0            # barrel, back face to front face
BUD_D = 10.0              # barrel diameter
BUD_BACK_R = 3.6          # round on the back edge
BUD_FRONT_R = 1.5         # round on the front edge (the shoulder to the nozzle is 1.8 mm)
BUD_SPLIT = 9.0           # the parting line between back cap and front shell, from the back face
SEAM_W, SEAM_D = 0.35, 0.25
NOZZLE_D = 5.2
NOZZLE_LEN = 5.0
EYELET_D = 5.0            # the burrow: a gunmetal collar at the back that the worm's head goes into
EYELET_LEN = 2.4
TIP_D = 11.5              # PLACEHOLDER: medium silicone tips, as bought
TIP_LEN = 7.4

# --- the worm cable (PROPOSAL) ----------------------------------------------------------------------------------------
BRANCH_R = 1.85           # each earbud's branch: 3.7 mm across
MAIN_R = 2.3              # below the splitter: 4.6 mm
SEG_PITCH_BRANCH = 2.5    # segments that overlap like a jointed snake toy, each lapping over the next toward the tail
SEG_PITCH_MAIN = 2.9
SEG_DEPTH = 0.16          # how far each segment flares toward its rear lip, as a fraction of the radius
SADDLE_FROM_BUD = 120.0   # the saddle (the worm's clitellum) on the right branch is the remote and microphone
SADDLE_LEN = 22.0
SADDLE_SWELL = 1.7 
BRANCH_LEN = 300.0        # bud to splitter
MAIN_LEN = 900.0          # splitter to plug

# --- splitter: where the two worms become one (PROPOSAL) ---------------------------------------------------------------
SPLIT_D = 9.0 
SPLIT_LEN = 13.0
SPLIT_HOLE_OFFSET = 2.2   # the branch holes' offset either side of the axis: the branches enter apart, not in a knot

# --- plug (PLACEHOLDER: 3.5 mm TRRS, CTIA, as bought) ----------------------------------------------------------------
PLUG_D = 3.5
PLUG_BARREL_D, PLUG_BARREL_LEN = 6.0, 13.0   # PROPOSAL: the tail runs into a gunmetal barrel
PLUG_LEN = 14.0
PLUG_RINGS = (3.2, 6.6, 9.9)

# --- printable shell, for making one (PROPOSAL; the driver is a PLACEHOLDER: a 9 to 10 mm dynamic IEM driver) ------
PRINT_WALL = 1.2
DRIVER_D = 9.4            # the driver sits in the front shell, against the nozzle's shoulder
DRIVER_T = 3.2
