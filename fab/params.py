"""Every number the fabrication files use, in millimetres, in the frame spec/geometry.md defines:
x across the width (0 left face seen from the front, 390 right face), y depth (0 front face, 390 back face), z height (0 floor).

Three kinds of number live here, and each is marked:
  SPEC      from README.md or spec/geometry.md (those files win if this one disagrees)
  DERIVED   arithmetic on SPEC numbers
  PROPOSAL  a construction choice this folder had to make so the speaker can be built. Not a Decision: the owner can change
            any of them without touching the outside of the speaker. They are listed in fab/README.md under "Proposals".
  PLACEHOLDER  waits on a part that is not chosen yet (the drivers, the binding posts). Re-cut when the part is bought.
"""
from math import atan2, degrees, hypot

# --- The outside (SPEC) -------------------------------------------------------------------------------------------
PLAN = 390.0            # SPEC square plan
BODY = 860.0            # SPEC floor to the front top edge
RISE = 150.0            # SPEC gable rise, front top edge to ridge
FIN_H = 45.0            # SPEC fin height above the ridge
FIN_T = 8.0             # SPEC "~8 thick", centred on the ridge (geometry.md assumption: y 191 to 199)
WALL = 18.0             # SPEC 18 mm Baltic birch
TOTAL = BODY + RISE + FIN_H   # DERIVED 1055
RIDGE_Z = BODY + RISE         # DERIVED 1010
RUN = PLAN / 2                # DERIVED 195
SLOPE = hypot(RUN, RISE)      # DERIVED 246.0
SLOPE_DEG = degrees(atan2(RISE, RUN))  # DERIVED 37.6
DY, DZ = RUN / SLOPE, RISE / SLOPE     # DERIVED unit vector up the front slope is (0, DY, DZ)

PLINTH_H = 110.0        # SPEC plinth z 0 to 110, accent colour
SHADOW = 3.0            # SPEC shadow line z 110 to 113
SHADOW_DEPTH = 3.0      # PROPOSAL the shadow line is a groove 3 wide and 3 deep

WOOFER = dict(z=290.0, frame=310.0)   # SPEC centre height and frame diameter (as drawn)
MID = dict(z=690.0, frame=170.0)      # SPEC

TWEETER = dict(faceplate_y=170.0, z=903.5, faceplate=62.0, faceplate_t=6.0, apex_forward=8.0,
               body_d=43.0, body_depth=30.0)  # SPEC faceplate <= 62 at y = 170. Body: PLACEHOLDER sized for the shortlisted
               # Scan-Speak Illuminator (43 mm cutout behind a 62 mm faceplate), which leaves a 9 mm shoulder for its screws.
BOWL = dict(mouth_w=211.0, mouth_l=118.0, mouth_s=79.0, throat=66.0,
            bulge=4.5)  # SPEC mouth and throat; bulge as built in render/src/model.mjs: the floor sags 3, the ceiling arches 6

PORT = dict(z=405.0, d=100.0, bore=92.0, flange=112.0)   # SPEC round port at z 405, 92 bore in a 112 flange (as drawn)
POSTS = dict(w=128.0, h=64.0, z=150.0, post_d=24.0, spacing=64.0)  # SPEC binding-post plate, centre z 150 (2026-10-02)
PLATE = dict(x0=36.0, x1=354.0, z0=484.0, z1=796.0, t=3.0, proud=1.5, r=3.0)  # SPEC bronze Facts plate on the back
LABEL = dict(w=266.0, h=260.0, top=770.0)  # SPEC engraved Facts panel, 14 mm padding on every side
BADGE = dict(type=44.0, relief=2.5, z=55.0, tracking=-0.035)       # SPEC cast letters on the plinth's front (Archivo Black)
BACK_BADGE = dict(type=44.0, relief=2.5, z=826.0, tracking=-0.035)  # SPEC the same letters on the back, above the plate
MARK_OPEN = dict(text='OPEN OTHER SIDE', type=27.0, tracking=0.04, arrow=True)   # SPEC on the back slope, Archivo 700
MARK_SHAKE = dict(text='SHAKE WELL', type=26.0, tracking=0.04, z=55.0)          # SPEC on the plinth's back face, Archivo 700

# --- Inside the cabinet (PROPOSAL) -----------------------------------------------------------------------------------
# Joinery: front and back run the full 390 width; the sides sit between them (354 wide); top and bottom sit inside all four.
# Every panel is a plain 2D cut so any CNC or panel-saw service can make it. The four walls are 860 tall, floor to the block.
INNER = PLAN - 2 * WALL   # DERIVED 354
TOP_Z0 = BODY - WALL      # 842: the top panel, under the gable block
# The midrange's own sealed chamber: a shelf under it and a divider behind it, the cabinet's walls and top doing the rest.
MID_CHAMBER_DEPTH = 90.0  # PROPOSAL clear depth behind the baffle, y 18 to 108 (a 6.5 in mid is 65 to 85 deep)
MID_SHELF_TOP = 590.0     # PROPOSAL shelf z 572 to 590, 15 below the mid's frame
# One window brace between the woofer and the mid chamber.
BRACE_Z = 500.0           # PROPOSAL brace z 500 to 518
BRACE_WINDOW = 254.0      # PROPOSAL square opening, 50 mm frame
BRACE_WINDOW_R = 30.0     # PROPOSAL corner radius of the opening

# The gable: a solid block, laminated from 18 mm birch layers and carved by CNC (SPEC: "a solid carved birch block").
GABLE_LAYER = 18.0        # PROPOSAL 11 layers of 18 mm, glued up, the top trimmed: 198 for a 195 block with its fin
GABLE_SPLIT_Z = 914.0     # PROPOSAL split for 3-axis milling: 3 layers below (z 860 to 914), 8 above. The bowl's floor is
                          # all below z 872 and its ceiling all above 936, so each half is cut from one side with no undercut
                          # worth the name (under 0.5 mm at the side walls, which sanding takes).
WIRE_HOLE_D = 14.0        # PROPOSAL tweeter wires drop from the pocket into the woofer chamber through the block and the top
DOWEL_D, DOWEL_DEPTH = 10.0, 20.0  # PROPOSAL four 10 mm dowels register the block on the body

# --- Waits on the drivers (PLACEHOLDER) ------------------------------------------------------------------------------
WOOFER_CUTOUT = 272.0     # PLACEHOLDER the shortlisted Dayton DSA315-8 / DS315-8 (fab/drivers.json); re-cut for another driver
MID_CUTOUT = 146.0        # PLACEHOLDER the shortlisted SB Acoustics SB17MFC35-8; the Satori MR16P-8 wants 140.3
CLEAR = 1.0               # PLACEHOLDER radial clearance for the tweeter pocket
TERMINAL_CUTOUT = (96.0, 36.0)   # PLACEHOLDER hole behind the post plate, for the posts' threads and nuts; leaves wood for its four screws
POST_HOLE = 10.0          # PLACEHOLDER binding-post hole in the plate

# --- Port (DERIVED in fab/acoustics.py; this is the length the files are cut to) ------------------------------------
PORT_WALL = 4.0           # PROPOSAL printed tube wall: 92 bore + 2 x 4 = 100 OD, which is the spec's port diameter
PORT_FLANGE_T = 5.0       # PROPOSAL
PORT_FLARE_R = 18.0       # PROPOSAL inner end flared on an 18 mm radius to keep it quiet
PORT_LENGTH = None        # filled from out/acoustics.json if present (total tube length, flange face to inner lip)

BIRCH_DENSITY = 680.0     # kg/m3, Baltic birch plywood, for the weight check


def slope_point(u, s, w=0.0):
    """A point in the front slope's frame: u across from the centreline, s up the slope from the front top edge,
    w along the outward normal. Returns (x, y, z) in the spec frame."""
    return (RUN + u, DY * s - DZ * w, BODY + DZ * s + DY * w)


def depth_at(z):
    """Front-to-back depth of the gable block at height z (it is a triangular prism with its ridge at y = 195)."""
    return max(0.0, PLAN * (RIDGE_Z - z) / RISE)
