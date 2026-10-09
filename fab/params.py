"""Every number the fabrication files use, in millimetres, in the frame spec/geometry.md defines:
x across the width (0 left face seen from the front, 390 right face), y depth (0 front face, 390 back face), z height (0 floor).

Three kinds of number live here, and each is marked:
  SPEC      from README.md or spec/geometry.md (those files win if this one disagrees)
  DERIVED   arithmetic on SPEC numbers
  PROPOSAL  a construction choice this folder had to make so the speaker can be built. Not a Decision: the owner can change
            any of them without touching the outside of the speaker. They are listed in fab/README.md under "Proposals".
  PLACEHOLDER  waits on a part that is not chosen yet (the drivers, the binding posts). Re-cut when the part is bought.
"""
import os
from math import atan2, degrees, hypot, tan, radians

# Two sizes share these files: the floorstander (a half-gallon carton, the spec) and the bookshelf (a quart: the same
# carton at 0.564 scale, 220 wide, PROPOSAL 2026-10-08 from fab/research/drivers-small.md). Pick one with the
# environment: EARMILK_SIZE=bookshelf .venv-fab/bin/python fab/cad.py. Outputs go to fab/out/ and fab/out-bookshelf/.
SIZE = os.environ.get('EARMILK_SIZE', 'floorstander')
assert SIZE in ('floorstander', 'bookshelf'), SIZE
BOOK = SIZE == 'bookshelf'

# --- The outside (SPEC) -------------------------------------------------------------------------------------------
PLAN = 220.0 if BOOK else 390.0          # SPEC square plan (bookshelf: PROPOSAL, the research's W 220)
BODY = 484.0 if BOOK else 860.0          # SPEC floor to the front top edge (bookshelf: 2.2 W, the floorstander's ratio)
RISE = round(PLAN / 2 * 150.0 / 195.0, 1) if BOOK else 150.0   # SPEC gable rise; the bookshelf keeps the 37.6 degree pitch
FIN_H = 25.0 if BOOK else 45.0           # SPEC fin height above the ridge
FIN_T = 6.0 if BOOK else 8.0             # SPEC "~8 thick", centred on the ridge (geometry.md assumption: y 191 to 199)
WALL = 18.0             # SPEC 18 mm Baltic birch
TOTAL = BODY + RISE + FIN_H   # DERIVED 1055
RIDGE_Z = BODY + RISE         # DERIVED 1010
RUN = PLAN / 2                # DERIVED 195
SLOPE = hypot(RUN, RISE)      # DERIVED 246.0
SLOPE_DEG = degrees(atan2(RISE, RUN))  # DERIVED 37.6
DY, DZ = RUN / SLOPE, RISE / SLOPE     # DERIVED unit vector up the front slope is (0, DY, DZ)

PLINTH_H = 62.0 if BOOK else 110.0       # SPEC plinth z 0 to 110, accent colour
SHADOW = 3.0            # SPEC shadow line z 110 to 113
SHADOW_DEPTH = 3.0      # PROPOSAL the shadow line is a groove 3 wide and 3 deep
GABLE_SHADOW_Z0 = BODY - 3.0             # SPEC 2026-10-07, the owner: a second 3 mm shadow line where the gable meets the body, z 857 to 860
EDGE_R = 4.0 if BOOK else 6.0            # SPEC 2026-10-08, the owner: the body's vertical corners and the gable's hips rounded 6 mm (3 mm on 2026-10-07)
FIN_EDGE_R = 2.0 if BOOK else 3.0        # SPEC 2026-10-08: the fin's edges 3 mm (1.5 on 2026-10-07)

if BOOK:
    WOOFER = dict(z=380.0, frame=171.0)  # PROPOSAL the bookshelf's one cone, high, near the tweeter (the research: under one wavelength apart at 2.2 kHz)
    MID = None
else:
    WOOFER = dict(z=320.0, frame=310.0)   # SPEC centre height and frame diameter (as drawn); 2026-10-08, the owner: z 320 (was 290)
    MID = dict(z=690.0, frame=170.0)      # SPEC

TWEETER = dict(faceplate_y=176.0, z=935.0, faceplate=62.0, faceplate_t=6.0, apex_forward=8.0,
               body_d=43.0, body_depth=30.0)  # SPEC faceplate <= 62 (2026-10-08, the owner), now at y 176, z 935 from the waveguide study (was 125). Body: PLACEHOLDER sized for the shortlisted
               # Scan-Speak Illuminator (43 mm cutout behind a 62 mm faceplate), which leaves a 9 mm shoulder for its screws.
BOWL = dict(mouth_w=211.0, mouth_l=118.0, mouth_s=79.0, throat=74.0,
            bulge=4.5)  # SPEC mouth and throat (74 since 2026-10-08, the owner; was 66: the faceplate seats on the throat's flat
                        # floor, a ring 6 wide); bulge as built in render/src/model.mjs: the floor sags 3, the ceiling arches 6

# 2026-10-08, the owner: the tweeter's waveguide is shaped for what it does to sound, not for looks. Its wall is the
# oblate-spheroidal profile in fab/waveguide.py, cut into the roof's front slope; fab/bem.py simulates the polar response
# and fab/out/acoustics/waveguide/ holds the study that chose these numbers. BOWL above is the look it replaces.
WAVEGUIDE = dict(throat_y=176.0, throat_z=935.0, r0=22.5, a0=12.0, a_h=45.0, a_up=35.0, a_down=30.0, k=1.4, lip_r=12.0)
               # 2026-10-08, the study (fab/out/acoustics/waveguide/study.md): the throat 176 behind the front face and 935 up
               # holds about +-40 degrees horizontally from 2 to 8 kHz with the listening axis within 0.8 dB of the loudest
               # direction; the owner's 125 / 903.5 beamed 30 degrees up at 2 kHz, the axis 4 dB down. r0 22.5: the SB Satori
               # TW29DN-B's 29 mm dome and 8 mm surround, 45 across (fab/research/drivers-floorstander.md; PLACEHOLDER
               # until one is measured), so the wall runs on from the surround with no flat ring
# The waveguide is a separate insert in a pocket in the roof. The tweeter screws to its back (rear mount, its flange in
# a counterbore behind the throat); the insert slides out forward, level, like a drawer, with the tweeter on it, and its
# wires unplug at a connector. Magnets in its back hold it; two pins locate it. PROPOSAL 2026-10-08.
INSERT = dict(margin=2.0, eave_clip=25.0, back_y=200.0, boss_d=86.0, boss_back_y=216.0, clear=0.3,
              magnet_d=12.0, magnet_t=4.0, pin_d=6.0, pin_l=10.0,
              bay_d=36.0, bay_l=35.0, bay_dz=-8.0)
# The connector bay: a bore behind the boss, in the block, that holds the plugged connector and a loop of slack, so the
# insert can come forward far enough to unplug it. Its centre bay_dz below the throat's axis keeps 20 mm of birch under
# the back slope. The cable channel leaves its floor at its middle.
# The tweeter as the mount sees it: the SB Acoustics Satori TW29DN-B with its faceplate taken off (SB documents it: 2.5 mm
# hex), the motor unit's front ring seated on the throat's ring. PLACEHOLDER sizes from the research (no drawing found):
# the unit no wider than its 71 to 74 cutout and about 32 deep; measure one first.
TWEETER_PART = dict(model='SB Acoustics Satori TW29DN-B', dome_d=29.0, surround_w=8.0, flange_d=73.0, flange_t=6.0, body_d=66.0,
                    body_depth=26.0, screws=4, bolt_circle=62.0, mount='sleeve')
# How it is held (the drawing check's d1, round 2): the faceplate's screws thread into the motor from the front, and a
# circle of screws inside the 66 motor cannot be driven from behind, so nothing screws through the tweeter. A printed
# retaining sleeve slides over the motor from behind and presses the front ring onto the throat's seat (on a 0.5 foam
# gasket); its own flange, on the boss's back face, takes three screws in the boss's wall, outside the bore. Whatever
# SB's screw circle turns out to be, it is not needed. PROPOSAL; its bore follows body_d (measure the motor first).
RETAINER = dict(gasket=0.5, clear=0.5, fit=0.2, flange_d=84.0, flange_t=3.0, screws=3, screw_circle=79.6,
                pilot_d=2.4, pilot_depth=10.0, hole_d=3.4,
                screw='3.0 x 12 thread-forming screws for plastics (WN 1411 / PT K30, pan head)')
INSERT_SCREW = None          # the bookshelf's: screws through its tweeter's faceplate into the seat (below)
# 2026-10-08, the research's recommended set for the active floorstander (fab/research/drivers-floorstander.md)
DRIVER_SET = dict(woofer='rss315hf-4', mid='mr16p-8', tweeter='tw29dn-b')

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
WOOFER_CUTOUT = 282.0     # PLACEHOLDER the Dayton RSS315HF-4 (fab/research/drivers-floorstander.md; 272 for the DS315-8 / DSA315-8)
MID_CUTOUT = 140.3        # PLACEHOLDER the SB Acoustics Satori MR16P-8 (146 for the SB17MFC35-8)
CLEAR = 1.0               # PLACEHOLDER radial clearance for the tweeter pocket
# 2026-10-08: active. A Hypex FusionAmp FA253 per speaker (fab/research/amps.md): 250 + 250 + 100 W into 4 ohm, the DSP
# crossover and EQ on board, mains in on the plate. Its 360 x 135 plate lies on its side across the back's foot, flush in a
# 4.5 mm rebate (below), centred at z 185 so it clears the shadow line at 113 (the research put it at 175).
# FusionAmps are not airtight, so the module sits in its own sealed box behind the plate, the cabinet's sides its ends.
AMP = dict(model='Hypex FusionAmp FA253', plate_w=360.0, plate_h=135.0, plate_t=3.0, plate_r=4.0, module_depth=55.0,
           cut_w=336.0, cut_h=111.0, z=185.0, rebate=4.5)   # PLACEHOLDER outline radius and screw pattern: Hypex's 2D drawing
# The plate's rebate is 4.5 deep: the 3.0 plate on 3 mm closed-cell EPDM tape compressed to 1.5, so it seals and lies flush
# (fab/research/amps.md); it is held by ten 4.3 x 16 self-tappers in 3.5 pilot holes through the 13.5 left under the rebate,
# where Hypex's 2D drawing puts them (not obtained: ask Hypex, or mark them from the plate in hand).
AMP_BOX = dict(depth=90.0, margin=12.0, gland_d=25.0, nut_cb=(40.0, 8.0))   # clear depth in front of the back's inner face; space above and below the cutout;
                                                            # the gland's lock nut in a 40 x 8 counterbore in the lid's underside (an M25 long thread is 15: 18 of lid less 8);
                                                            # the lid's gland an M25 with a three-hole seal (woofer, mid, tweeter)
TERMINAL_CUTOUT = (113.0, 49.0)  # DERIVED the terminal cup's body plus 0.5 a side, through the back (was 96 x 36 behind a flat plate)
# 2026-10-08, the owner: the drivers flush. Each frame sits in a rebate as deep as its flange and the printed trim ring over it, so
# the ring's face is level with the finish, with a 0.8 reveal round it.
# The drivers' screws: holes for M4 T-nuts fitted from inside, on each frame's bolt circle. PLACEHOLDER circles and counts
# (the research's estimates, fab/research/drivers-*.md): measure the frame before drilling.
DRIVER_SCREWS = dict(woofer=dict(n=8, pcd=298.0, hole=5.5, start_deg=22.5), mid=dict(n=4, pcd=154.0, hole=5.5, start_deg=45.0))
LEAD_ABOVE_GROMMET = 250.0   # the cabinet's tweeter lead past the grommet: 67 up the channel, 167 to 20 proud of the roof
                             # in front of the bay (so the socket comes out through the empty pocket), 16 of slack
WOOFER_REBATE = dict(d=315.6, depth=9.0)  # PLACEHOLDER the RSS315HF-4's 314 frame + 2 x 0.8; depth its flange (about 5, measure it) + 1.0 of compressed gasket + the 3 mm ring
MID_REBATE = dict(d=166.6, depth=11.5)    # PLACEHOLDER the MR16P-8's 165 frame + 2 x 0.8; depth its 7.5 front flange + 1.0 of gasket + the 3 mm ring
TRIM_RING = dict(t=3.0, width=20.0)       # PROPOSAL printed trim ring over each frame and its screws, sprayed satin black, held by three dots of neutral-cure silicone
# Each ring's inner diameter: the driver's surround at its glue line + 2, so the ring covers the flange and its screw heads
# and never the surround. PLACEHOLDER from the research's estimates (the RSS315HF-4's surround about 280 to 295, the
# MR16P-8's not found, about 139 for its 140 cutout): measure each driver's surround and print the rings last.
TRIM_RING_ID = dict(woofer=290.0, mid=141.0)
POST_HOLE = 10.0          # PLACEHOLDER binding-post hole in the plate

# --- Port (DERIVED in fab/acoustics.py; this is the length the files are cut to) ------------------------------------
PORT_WALL = 4.0           # PROPOSAL printed tube wall: 92 bore + 2 x 4 = 100 OD, which is the spec's port diameter
PORT_FLANGE_T = 5.0       # PROPOSAL
PORT_FLARE_R = 18.0       # PROPOSAL inner end flared on an 18 mm radius to keep it quiet
PORT_LENGTH = None        # filled from out/acoustics.json if present (total tube length, flange face to inner lip)
PORT_TRIM = 10.0          # the printed tube is this much longer, trimmed to tune by measurement (fab/README.md)

BIRCH_DENSITY = 680.0     # kg/m3, Baltic birch plywood, for the weight check


def slope_point(u, s, w=0.0):
    """A point in the front slope's frame: u across from the centreline, s up the slope from the front top edge,
    w along the outward normal. Returns (x, y, z) in the spec frame."""
    return (RUN + u, DY * s - DZ * w, BODY + DZ * s + DY * w)


def depth_at(z):
    """Front-to-back depth of the gable block at height z (it is a triangular prism with its ridge at y = 195)."""
    return max(0.0, PLAN * (RIDGE_Z - z) / RISE)


# --- The bookshelf (PROPOSAL 2026-10-08, fab/research/drivers-small.md) ----------------------------------------------
# A quart beside the half-gallon: the same carton at 0.564 scale (220 for 390), two-way and active, sealed. Everything
# above that depends on size is restated here; anything not restated is shared (wall, shadow lines, finishes).
if BOOK:
    # the waveguide, from the bookshelf's own study (fab/out-bookshelf/acoustics/waveguide/README.md): candidate BkD,
    # the throat 95 behind the face, r0 17 (the Illuminator's 26 mm dome and its roll, 34 across), a0 4 so the wall
    # opens gently from the dome, s_min 10 so the mouth reaches the eave. It holds about +-56 degrees horizontally at
    # 2.5 kHz and +-32 from 6.3 kHz, the listening axis within 0.8 dB of the loudest direction at 2.5 kHz. The
    # simulated throat was 514 up; it is 517 here so the 62 mm faceplate clears the top panel (2 mm of insert under
    # it), which moves nothing measurable at these wavelengths.
    WAVEGUIDE = dict(throat_y=95.0, throat_z=517.0, r0=17.0, a0=4.0, a_h=45.0, a_up=35.0, a_down=30.0, k=1.4, lip_r=7.0, s_min=10.0)
    INSERT = dict(margin=1.5, eave_clip=14.0, back_y=113.0, boss_d=68.4, boss_back_y=131.0, clear=0.3,   # PROPOSAL boss 68.4 round the faceplate's 62.4 bore, flattened on the top panel (1.5 of insert under the bore)
                  magnet_d=8.0, magnet_t=3.0, pin_d=4.0, pin_l=8.0,
                  bay_d=26.0, bay_l=22.0, bay_dz=-5.0)
    # Scan-Speak Illuminator D3004/602200: its 62 mm faceplate screwed to the insert's back, the dome in the 34 mm throat
    TWEETER_PART = dict(model='Scan-Speak Illuminator D3004/602200', dome_d=26.0, surround_w=4.0, flange_d=62.0, flange_t=4.5,
                        body_d=48.0, body_depth=17.0, screws=3, bolt_circle=54.0, mount='screws')
    # Its faceplate has its own three holes (about 55 apart, the research's estimate), so it screws to the seat from behind:
    # M2.5 low heads (ISO 7380, head 4.7 across) on the 54 circle clear the 48 body by 0.65; a body over 49 would need the
    # floorstander's sleeve, which the 3 mm boss wall here cannot hold. Knurled brass inserts bonded with epoxy hold in
    # any of the insert's materials (a heat-set insert will not melt into cured resin). PLACEHOLDER circle: measure first.
    RETAINER = None
    INSERT_SCREW = dict(hole_d=3.6, depth=5.0, insert='M2.5 x 4 knurled brass, bonded with epoxy',
                        screw='M2.5 x 8 button head, ISO 7380, A2', head_d=4.7)
    TWEETER = dict(TWEETER, faceplate_y=WAVEGUIDE['throat_y'], z=WAVEGUIDE['throat_z'])
    DRIVER_SET = dict(woofer='sb17nrx2c35-8', mid=None, tweeter='d3004-602200')
    WOOFER_CUTOUT = 144.9                     # PLACEHOLDER unconfirmed in the research
    DRIVER_SCREWS = dict(woofer=dict(n=4, pcd=159.0, hole=5.5, start_deg=45.0))   # 4 x 4.3 on 159 (fab/research/drivers-small.md)
    LEAD_ABOVE_GROMMET = 185.0   # 33 up the channel to the bay's floor, about 115 to the roof, 20 proud, 16 of slack (the drawing check's d14)
    WOOFER_REBATE = dict(d=172.6, depth=10.5)  # the 171 frame + 2 x 0.8; its 6.5 flange + 1.0 of gasket + the 3 mm ring
    MID_CUTOUT = None; MID_REBATE = None
    PORT = None                               # sealed: 9.2 L net (fab/out-bookshelf/acoustics.json), f3 63 Hz, a DSP shelf to 45 Hz
    POSTS = dict(POSTS, z=180.0)
    # Hypex FusionAmp FA122 upright on the back (its 315 plate will not lie across a 220 back)
    AMP = dict(model='Hypex FusionAmp FA122', plate_w=120.0, plate_h=315.0, plate_t=3.0, plate_r=4.0, module_depth=55.0,
               cut_w=96.0, cut_h=293.0, z=235.0, rebate=4.5)   # the cut-out 291 in Hypex's data, 293 on an Audiophonics drawing: cut 293 (the 315 plate still laps 11 each end) unless the module offered to a test cut-out says otherwise
    AMP_BOX = dict(depth=70.0, margin=10.0, gland_d=20.0, nut_cb=(32.0, 8.0))   # an M20 with a two-hole seal, its nut in a 32 x 8 counterbore
    # The back holds the amplifier, so the Facts go on the right side, as on a real carton
    LABEL = dict(w=150.0, h=147.0, top=420.0, face='right')
    BADGE = dict(type=25.0, relief=1.2, z=31.0, tracking=-0.035)
    BACK_BADGE = dict(type=25.0, relief=1.2, z=440.0, tracking=-0.035)
    MARK_OPEN = dict(text='OPEN OTHER SIDE', type=15.0, tracking=0.04, arrow=True)
    MARK_SHAKE = dict(text='SHAKE WELL', type=15.0, tracking=0.04, z=31.0)
    INNER = PLAN - 2 * WALL
    TOP_Z0 = BODY - WALL
    MID_CHAMBER_DEPTH = None; MID_SHELF_TOP = None
    BRACE_Z = None; BRACE_WINDOW = None; BRACE_WINDOW_R = None   # no window brace: the amplifier's box fills the back half from
                                                                  # z 62 to 409 and its 18 mm front, glued to both sides, braces them
    GABLE_SPLIT_Z = None
    TRIM_RING = dict(t=3.0, width=12.0)
    TRIM_RING_ID = dict(woofer=147.0)      # PLACEHOLDER the SB17NRX2C35-8's surround just inside its 145 cutout (the research) + 2
