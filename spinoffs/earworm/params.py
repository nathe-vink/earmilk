"""earworm: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).
Nothing here is SPEC yet: the owner has not seen earworm.

Frame: x ear to ear (left cup at -x), y front to back (front is -y), z up. The ear canal is the origin.
The headphones stand on their cups on the floor at z = FLOOR_Z, the way they sit on a desk.
"""

# --- cups (PROPOSAL) -------------------------------------------------------------------------------------------------
CUP_D = 100.0             # outside diameter of shell and cushion; round, over-ear
CUSHION_IN_X = 72.0       # inner (head-side) face of the cushion: 144 between the cushions, uncompressed
CUSHION_T = 24.0          # cushion thickness along x
CUSHION_HOLE_D = 56.0     # ear opening
CUSHION_ROUND = 9.0       # radius of the cushion's rolled edges
SHELL_DEPTH = 30.0        # shell from the cushion's back to the cup's back face
SHELL_BACK_D = 84.0       # the flat back face; the shell rounds from CUP_D down to this
SHELL_ROUND = 11.0        # the shell's rounded shoulder
PARTING_X = 11.0          # the shell's parting line, from its front
CAP_R = 35.0              # the back cap's line (the cap carries the wordmark)
SEAM_W, SEAM_D = 0.6, 0.4 # every seam and parting line: width, depth
WORDMARK_SIZE = 11.0      # font size of the debossed wordmark on each cup back (Archivo Black, as earmilk)
WORDMARK_DEPTH = 0.5      # deboss depth
WORDMARK_TRACK = -0.035   # tracking in em, as earmilk's cast letters

# --- yoke and band (PROPOSAL) ----------------------------------------------------------------------------------------
YOKE_R = 57.0             # centreline radius of the U-shaped yoke around the cup axis, in the y-z plane
YOKE_W = 7.0              # yoke section, radial
YOKE_T = 6.0              # yoke section, along x
PIVOT_D = 9.0             # pivot boss diameter, front and back of the cup
BAND_APEX_Z = 140.0       # band centreline at the crown
BAND_END = (111.0, 60.0)  # band centreline where it meets the yoke's top (x, z)
BAND_W = 26.0             # band width along y
BAND_T = 6.0              # band thickness, radial
PAD_W = 24.0              # crown pad width
PAD_T = 9.0               # crown pad thickness
PAD_SPAN_DEG = 104.0      # crown pad length, as an angle of the band's arc
SLIDER_LEN = 34.0         # slider sleeve at each end of the band
SLIDER_W, SLIDER_T = 28.0, 8.5

# --- cable entry and the worm (PROPOSAL) ----------------------------------------------------------------------------
GROMMET_D = 12.0          # the burrow: a gunmetal eyelet low on the left cup's front, where the worm's head goes in
GROMMET_LEN = 6.0
GROMMET_ANGLE = 50.0      # degrees from straight down, toward the front: the worm leaves forward, where the camera sees it
WORM_R = 3.2              # cable radius: 6.4 mm, a thick cable and a thin worm; thinner stops reading as a worm
WORM_RING_PITCH = 2.4     # annuli
WORM_RING_DEPTH = 0.04    # groove depth as a fraction of the radius
CLITELLUM_FROM_HEAD = 290.0   # the saddle band, which is the inline remote, measured along the cable from the cup
CLITELLUM_LEN = 34.0
CLITELLUM_SWELL = 1.4     # radius factor at the saddle
CABLE_LEN = 1200.0        # cup to plug
WORM_FLATTEN = 0.1        # a soft sleeve lying on a floor is 10 % lower and wider than it is round

# --- plug (PLACEHOLDER: 3.5 mm TRRS, CTIA, as bought) ----------------------------------------------------------------
PLUG_D = 3.5
PLUG_BARREL_D, PLUG_BARREL_LEN = 7.0, 14.0   # PROPOSAL: the tail runs into a gunmetal barrel
PLUG_LEN = 14.0           # exposed pin
PLUG_RINGS = (3.2, 6.6, 9.9)   # insulating bands from the tip, mm

# --- printable parts, for making one (PROPOSAL; the driver is a PLACEHOLDER: a 50 mm headphone driver) ------------
PRINT_WALL = 2.4
BAFFLE_T = 2.5
DRIVER_HOLE_D = 46.0      # through the baffle, behind the driver's diaphragm
DRIVER_FLANGE_D = 50.6    # the driver's rim sits in a 1.5 mm recess

FLOOR_Z = -CUP_D / 2      # the cups' lowest point
