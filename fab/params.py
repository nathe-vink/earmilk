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
GABLE_SHADOW_Z0 = 857.0 # SPEC 2026-10-07, the owner: a second 3 mm shadow line where the gable meets the body, z 857 to 860
EDGE_R = 6.0            # SPEC 2026-10-08, the owner: the body's vertical corners and the gable's hips rounded 6 mm (3 mm on 2026-10-07)
FIN_EDGE_R = 3.0        # SPEC 2026-10-08: the fin's edges 3 mm (1.5 on 2026-10-07)

WOOFER = dict(z=320.0, frame=310.0)   # SPEC centre height and frame diameter (as drawn); 2026-10-08, the owner: z 320 (was 290)
MID = dict(z=690.0, frame=170.0)      # SPEC

TWEETER = dict(faceplate_y=176.0, z=935.0, faceplate=62.0, faceplate_t=6.0, apex_forward=8.0,
               body_d=43.0, body_depth=30.0)  # SPEC faceplate <= 62 at y = 125 (2026-10-08, the owner; was 170). Body: PLACEHOLDER sized for the shortlisted
               # Scan-Speak Illuminator (43 mm cutout behind a 62 mm faceplate), which leaves a 9 mm shoulder for its screws.
BOWL = dict(mouth_w=211.0, mouth_l=118.0, mouth_s=79.0, throat=74.0,
            bulge=4.5)  # SPEC mouth and throat (74 since 2026-10-08, the owner; was 66: the faceplate seats on the throat's flat
                        # floor, a ring 6 wide); bulge as built in render/src/model.mjs: the floor sags 3, the ceiling arches 6

# 2026-10-08, the owner: the tweeter's waveguide is shaped for what it does to sound, not for looks. Its wall is the
# oblate-spheroidal profile in fab/waveguide.py, cut into the roof's front slope; fab/bem.py simulates the polar response
# and fab/out/acoustics/waveguide/ holds the study that chose these numbers. BOWL above is the look it replaces.
WAVEGUIDE = dict(throat_y=176.0, throat_z=935.0, r0=15.0, a0=12.0, a_h=45.0, a_up=35.0, a_down=30.0, k=1.4, lip_r=12.0)
               # 2026-10-08, the study (fab/out/acoustics/waveguide/study.md): the throat 176 behind the front face and 935 up
               # holds about +-40 degrees horizontally from 2 to 8 kHz with the listening axis within 0.8 dB of the loudest
               # direction; the owner's 125 / 903.5 beamed 30 degrees up at 2 kHz, the axis 4 dB down. r0: the tweeter's
               # dome and surround (PLACEHOLDER 30 mm until the tweeter is bought)
# The waveguide is a separate insert in a pocket in the roof. The tweeter screws to its back (rear mount, its flange in
# a counterbore behind the throat); the insert slides out forward, level, like a drawer, with the tweeter on it, and its
# wires unplug at a connector. Magnets in its back hold it; two pins locate it. PROPOSAL 2026-10-08.
INSERT = dict(margin=2.0, eave_clip=25.0, back_y=200.0, boss_d=52.0, boss_back_y=226.0, clear=0.3,
              magnet_d=12.0, magnet_t=4.0, pin_d=6.0, pin_l=10.0)
# The tweeter as the mount sees it. PLACEHOLDER until the tweeter is chosen (fab/research): a 1 in dome whose dome and
# surround fill the 30 mm throat, on a 50 mm round flange 4 thick, its body 43 across and 30 deep behind the flange.
TWEETER_PART = dict(dome_d=26.0, surround_w=2.0, flange_d=50.0, flange_t=4.0, body_d=43.0, body_depth=30.0, screws=3, bolt_circle=42.0)

PORT = dict(z=405.0, d=100.0, bore=92.0, flange=112.0)   # SPEC round port at z 405, 92 bore in a 112 flange (as drawn)
POSTS = dict(w=128.0, h=64.0, z=175.0, post_d=24.0, spacing=64.0)  # SPEC terminal cup's flange, centre z 175 (2026-10-08, the owner; the plate at 150 before)
TERMINAL_CUP = dict(w=112.0, h=48.0, r=5.0, wall=3.0, depth=21.0, flange_t=3.0, flange_r=7.0, recess=18.0)
                        # SPEC 2026-10-08, the owner: a recessed cup, the posts on its floor 18 in from the flange's face.
                        # PROPOSAL its make: printed (PETG or ASA), sprayed satin black; the body 112 x 48 runs through the back,
                        # flush with its inner face, the 128 x 64 flange 3 proud of the finish on four screws
# 2026-10-07, the owner: no bronze plate (it was 318 x 312 x 3, 1.5 proud, at x 36 to 354, z 484 to 796). The Facts are
# printed on the back's finish under the 2K clear.
LABEL = dict(w=266.0, h=260.0, top=770.0)  # SPEC printed Facts panel, centred on the back, 14 mm padding inside its border
FACTS_INK = '#1E1A17'                      # SPEC on the white flavours; Chocolate cream #F1E3CC, Oat brown #2B2118
BADGE = dict(type=44.0, relief=1.5, z=55.0, tracking=-0.035)       # SPEC cast letters on the plinth's front (Archivo Black); 1.5 proud since 2026-10-08 (was 2.5)
BACK_BADGE = dict(type=44.0, relief=1.5, z=813.0, tracking=-0.035)  # SPEC the same letters on the back; 2026-10-07 centred between the body's top edge (857) and the Facts (770), was 826
MARK_OPEN = dict(text='OPEN OTHER SIDE', type=27.0, tracking=0.04, arrow=True)   # SPEC on the fin's back face (2026-10-07, the owner; was the back slope), Archivo 700
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
                          # all below z 873 and its ceiling all above 940, so each half is cut from one side. The side walls
                          # overhang the split a little: up to 1.2 mm in the lower half and 2.8 in the upper (80 to 105 deep,
                          # 7 to 12 above the split) since the throat came forward on 2026-10-08 (1.3 and 0.3 before). Sand
                          # them, or mill the upper half's bowl with the block tilted onto the slope, along the mouth's axis.
                          # No split height does better than about 1.9 in both (z 916).
WIRE_HOLE_D = 14.0        # PROPOSAL tweeter wires drop from the pocket into the woofer chamber through the block and the top
DOWEL_D, DOWEL_DEPTH = 10.0, 20.0  # PROPOSAL four 10 mm dowels register the block on the body

# --- Waits on the drivers (PLACEHOLDER) ------------------------------------------------------------------------------
WOOFER_CUTOUT = 272.0     # PLACEHOLDER the shortlisted Dayton DSA315-8 / DS315-8 (fab/drivers.json); re-cut for another driver
MID_CUTOUT = 146.0        # PLACEHOLDER the shortlisted SB Acoustics SB17MFC35-8; the Satori MR16P-8 wants 140.3
CLEAR = 1.0               # PLACEHOLDER radial clearance for the tweeter pocket
# 2026-10-08: active. A Hypex FusionAmp FA253 per speaker (fab/research/amps.md): 250 + 250 + 100 W into 4 ohm, the DSP
# crossover and EQ on board, mains in on the plate. Its 360 x 135 plate lies on its side across the back's foot, flush in a
# 3 mm rebate like the drivers' rings, centred at z 185 so it clears the shadow line at 113 (the research put it at 175).
# FusionAmps are not airtight, so the module sits in its own sealed box behind the plate, the cabinet's sides its ends.
AMP = dict(model='Hypex FusionAmp FA253', plate_w=360.0, plate_h=135.0, plate_t=3.0, plate_r=4.0, module_depth=55.0,
           cut_w=336.0, cut_h=111.0, z=185.0, rebate=3.0)   # PLACEHOLDER outline radius and screw pattern: Hypex's 2D drawing
AMP_BOX = dict(depth=90.0, margin=12.0, gland_d=20.0)       # clear depth in front of the back's inner face; space above and below the cutout
TERMINAL_CUTOUT = (113.0, 49.0)  # DERIVED the terminal cup's body plus 0.5 a side, through the back (was 96 x 36 behind a flat plate)
# 2026-10-08, the owner: the drivers flush. Each frame sits in a rebate as deep as its flange and the printed trim ring over it, so
# the ring's face is level with the finish, with a 0.8 reveal round it.
WOOFER_REBATE = dict(d=315.6, depth=8.0)  # PLACEHOLDER the DSA315-8's 314 frame + 2 x 0.8; depth its flange (about 5, measure it) + the 3 mm ring
MID_REBATE = dict(d=172.6, depth=6.0)     # PLACEHOLDER the SB17MFC35-8's 171 frame + 2 x 0.8; depth its flange (about 3, measure it) + the ring
TRIM_RING = dict(t=3.0, width=20.0)       # PROPOSAL printed trim ring over each frame and its screws, sprayed satin black, a friction fit
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
