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
TWEETER_PART = dict(model='SB Acoustics Satori TW29DN-B', dome_d=29.0, surround_w=8.0, flange_d=70.0, flange_t=5.0, body_d=70.0,
                    body_depth=16.7, screws=4, bolt_circle=62.0, mount='sleeve')
# SPEC SB's drawing (fab/research/datasheets-2026-10-09.json; the drawing check's d4, round 8): behind its 5.0 faceplate the
# unit is one ø70.0 body 21.7 deep (29.3 overall, the dome 2.6 proud of the faceplate), so with the faceplate off it is
# drawn as that cylinder, its first 5 the 'front ring' that seats on the throat (flange_t + body_depth = 21.7). The bore is
# the body + 0.4, so it centres the unit; the cap's ring follows. The 73 x 6 ring and 66 x 26 motor drawn before were
# placeholders SB's figures contradict. Still measure first (M4): the shops' cut-outs run 71 to 74.
# How it is held (the drawing check's d1, round 2): the faceplate's screws thread into the motor from the front, and a
# circle of screws inside the 66 motor cannot be driven from behind, so nothing screws through the tweeter. A printed
# retaining sleeve slides over the motor from behind and presses the front ring onto the throat's seat (on a 0.5 foam
# gasket); its own flange, on the boss's back face, takes three screws in the boss's wall, outside the bore. Whatever
# SB's screw circle turns out to be, it is not needed. PROPOSAL; its bore follows body_d (measure the motor first).
RETAINER = dict(mode='cap', gasket=0.5, preload=0.25, clear=0.5, fit=0.2, rim=6.0, flange_d=85.0, flange_t=3.0, screws=3,
                screw_circle=78.8, pilot_d=2.4, pilot_depth=10.0, hole_d=3.2, head_h=2.4, start_deg=0.0,
                screw='3.0 x 12 thread-forming screws for plastics (WN 1411 / PT K30, pan head)')
# mode 'cap' (the drawing check's d2, round 7): a printed ring in the bore behind the tweeter, bearing on its motor's back
# face (a rim `rim` wide round the motor's edge; its tabs and lead pass the centre hole), its flange screwed to the boss's
# back face. It holds whatever the front ring and the motor measure, ring over motor or one cylinder (SB's faceplate
# drawing shows ø70.0 behind the faceplate, where the 'sleeve' mode, a tube over the motor pressing a ring that stands
# past it, needs the motor 3 + 2 x clear under the ring and failed at a 70 motor in a 73 ring).
# The heads stand head_h proud of the flange (a 3 mm pan head is 1.8 to 2.4): the pocket's bore runs that and 1.1 more
# behind the flange, or the insert stops short of home (the drawing check's d3, round 3). The circle starts on the
# horizontal (start_deg 0, the speaker's right), so no pilot lies on the insert's split at the centre plane (d5).
# The tube is `preload` longer than the gap from the front ring to the boss's back face, so its flange stands 0.25 off
# the boss until the three screws press the gasket by that much (a tube printed 0.15 short still holds: d5, round 5).
# The flange ø85 with ø3.2 holes on ø78.8 keeps 1.5 of flange outside each hole and the heads inside its rim (ø84
# with ø3.4 on ø79.6 left a 0.5 web: d6, round 6); the boss's pilots move with the circle, 1.5 inside the bore.
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
DIVIDER_SHORT = 1.0       # PROPOSAL the divider cut this far short of the top panel, the gap sealed by G6's PU fillet (planing it
                          # 0.3 down between the sides after glue-up could not be done: the drawing check's d8, round 8)
# One window brace between the woofer and the mid chamber.
BRACE_Z = 500.0           # PROPOSAL brace z 500 to 518
BRACE_WINDOW = 254.0      # PROPOSAL square opening, 50 mm frame
BRACE_WINDOW_R = 30.0     # PROPOSAL corner radius of the opening

# The gable: a solid block, laminated from 18 mm birch layers and carved by CNC (SPEC: "a solid carved birch block").
GABLE_LAYER = WALL        # PROPOSAL the gable's layers are the measured ply (M1): 11 of 18 mm, glued up, the top trimmed,
                          # 198 for a 195 block with its fin; under 17.73 a 12th layer (the drawing check's d2, round 5)
GABLE_SPLIT_Z = BODY + 3 * GABLE_LAYER     # PROPOSAL split for 3-axis milling: 3 layers below (z 860 to 914), 8 above. The bowl's floor is
                          # all below z 873 and its ceiling all above 940, so each half is cut from one side. The side walls
                          # overhang the split a little: up to 1.2 mm in the lower half and 2.8 in the upper (80 to 105 deep,
                          # 7 to 12 above the split) since the throat came forward on 2026-10-08 (1.3 and 0.3 before). Sand
                          # them, or mill the upper half's bowl with the block tilted onto the slope, along the mouth's axis.
                          # No split height does better than about 1.9 in both (z 916).
WIRE_HOLE_D = 14.0        # PROPOSAL tweeter wires drop from the pocket into the woofer chamber through the block and the top
DOWEL_D, DOWEL_DEPTH = 10.0, 20.0  # PROPOSAL four 10 mm dowels register the block on the body

# --- Waits on the drivers (PLACEHOLDER) ------------------------------------------------------------------------------
WOOFER_CUTOUT = 282.0     # SPEC Dayton's page: 'baffle cutout diameter 282' (fab/research/datasheets-2026-10-09.json; 272 for the DS315-8 / DSA315-8)
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
AMP_BOX = dict(depth=90.0, margin=12.0, glands=3, gland='M16 x 1.5', gland_hole=16.5, gland_pitch=35.0, nut_cb=(24.0, 8.0))   # clear depth in front of the back's inner face; space above and below the cutout;
                                                            # one M16 x 1.5 long-thread gland per cable (clamping about 4.5 to 10: the
                                                            # 9.0, 8.0 and 6.4 round cables), on 35 mm centres, each lock nut in a
                                                            # 24 x 8 counterbore in the lid's underside (a 15 thread: 18 of lid less 8).
                                                            # One three-hole seal could not take three cables of three sizes (the
                                                            # drawing check's d8, round 3)
TERMINAL_CUTOUT = (113.0, 49.0)  # DERIVED the terminal cup's body plus 0.5 a side, through the back (was 96 x 36 behind a flat plate)
# 2026-10-08, the owner: the drivers flush. Each frame sits in a rebate as deep as its flange and the printed trim ring over it, so
# the ring's face is level with the finish, with a 0.8 reveal round it.
# The drivers' screws: holes for M4 T-nuts fitted from inside, on each frame's bolt circle. PLACEHOLDER circles and counts
# (the research's estimates, fab/research/drivers-*.md): measure the frame before drilling. The woofer's 8 holes are
# Dayton's own count; their circle, 295, is Audiophonics' 'mounting bolt diameter', the one published figure (Dayton's
# page leaves it blank; the 298 before it was an estimate): fab/research/datasheets-2026-10-09.json
DRIVER_SCREWS = dict(woofer=dict(n=8, pcd=295.0, hole=5.5, start_deg=22.5), mid=dict(n=4, pcd=154.0, hole=5.5, start_deg=45.0))
# The screws and the nuts they go into, by limits a named part has to meet (the drawing check's d15, round 3): a low head,
# so the trim ring's channel over them stays inside the ring, and T-nuts whose flanges stay clear of the cut-outs
DRIVER_SCREW = dict(thread='M4 x 20', head='low-profile (wafer) button head, A2', head_d=8.0, head_h=1.6,
                    tnut_flange=dict(woofer=12.0, mid=12.0), tnut_barrel=dict(woofer=8.0, mid=6.0))
# the woofer's T-nuts 12 across or less: on the 295 circle a 15 mm flange overhung its 282 cut-out by 1 (a CAD check)
LEAD_ABOVE_GROMMET = 77.0    # the cabinet's tweeter lead above the top panel's underside: 67 up the channel to the bay's floor
                             # and 10 past it into its socket, which stands on the floor (the drawing check's d2, round 4:
                             # 30 past the floor put a 24 mm pair through the bay's ceiling). The slack to plug it is the
                             # tweeter's own lead (TWEETER_LEAD): a 6.4 mm round cable cannot fold in a 36 mm bay
TWEETER_LEAD = dict(l=320.0, wire='2 x 0.75 mm2 silicone-insulated flex, twisted (about 2.2 mm each)')   # 320 since the unit is drawn
# 21.7 deep (SB): its tabs 10 further from the socket than the 32 deep placeholder put them (round 8)
                             # soldered to the tweeter's tabs, the plug on its end. It must reach the socket in the bay
                             # with the insert held just clear of its pocket, the tabs about 225 from the socket, 75 for a hand
                             # in the pocket and 10 spare; home, its spare loops into the bay (the drawing check's d1, round 4: at 150 it
                             # could not be plugged in)
# The connector: Molex Mini-Fit Jr., two circuits, a locking wire-to-wire pair (the drawing check's d2, round 4). The
# socket, female contacts, on the cabinet's lead (the amplifier's side); the plug, male, on the tweeter's
CONNECTOR = dict(series='Molex Mini-Fit Jr., 2 circuits',
                 socket='receptacle housing 39-01-2020 with female terminals 39-00-0077 (16 AWG) on the cabinet\'s 1.0 mm2 lead',
                 plug='plug housing 39-01-2021 with male terminals 39-00-0041 (18 to 24 AWG) on the tweeter\'s 0.75 mm2 flex',
                 mated_l=24.0, pin1='red +')
WOOFER_REBATE = dict(d=315.6, depth=9.0)  # PLACEHOLDER the RSS315HF-4's 314 frame + 2 x 0.8; depth its flange (about 5, measure it) + 1.0 of compressed gasket + the 3 mm ring
MID_REBATE = dict(d=166.6, depth=11.5)    # PLACEHOLDER the MR16P-8's 165 frame + 2 x 0.8; depth its 7.5 front flange + 1.0 of gasket + the 3 mm ring
TRIM_RING = dict(t=3.0, width=20.0)       # PROPOSAL printed trim ring over each frame and its screws, sprayed satin black, held by three dots of neutral-cure silicone
# Each ring's inner diameter: the driver's surround at its glue line + 2, so the ring covers the flange and its screw heads
# and never the surround. PLACEHOLDER from the research's estimates (the RSS315HF-4's surround about 280 to 295, the
# MR16P-8's not found, about 139 for its 140 cutout): measure each driver's surround and print the rings last.
TRIM_RING_ID = dict(woofer=290.0, mid=141.0)
# 2026-10-10, the owner: a non-aluminium woofer, performant and in keeping with the carton. Candidates from
# fab/research/woofers-nonmetal-2026-10-10.md, each with what the CAD needs: the cut-out, the rebate for its frame and
# ring (frame + 1.6; flange + 1.0 of gasket + the 3 mm ring deep), the ring's inner edge (the surround's glue line + 2,
# from Sd and a proportioned roll) and the screws. PLACEHOLDER: from search snippets of the datasheets; the screw
# circles are proportioned (halfway between the cut-out and the frame's edge). Not chosen yet: DRIVER_SET keeps the
# RSS315HF-4 until the owner picks. EARMILK_WOOFER=<key> builds with one in its place, for comparisons.
WOOFER_OPTIONS = {
    'rss315hf-4': dict(cutout=282.0, rebate=dict(d=315.6, depth=9.0), ring_id=290.0, screws=dict(n=8, pcd=295.0, hole=5.5, start_deg=22.5)),
    'sb34nrxl75-8': dict(cutout=305.2, rebate=dict(d=347.6, depth=17.0), ring_id=281.0, screws=dict(n=8, pcd=326.0, hole=5.5, start_deg=22.5)),
    '32w-4878t00': dict(cutout=290.5, rebate=dict(d=321.6, depth=12.0), ring_id=286.0, screws=dict(n=8, pcd=305.0, hole=5.5, start_deg=22.5)),
    'tiw300-8': dict(cutout=288.0, rebate=dict(d=330.6, depth=10.0), ring_id=281.0, screws=dict(n=8, pcd=309.0, hole=5.5, start_deg=22.5)),
}
POST_HOLE = 10.0          # PLACEHOLDER binding-post hole in the plate
_W = os.environ.get('EARMILK_WOOFER')
if _W and not BOOK:          # a comparison build with a candidate woofer (WOOFER_OPTIONS) in the RSS315HF-4's place
    DRIVER_SET = dict(DRIVER_SET, woofer=_W)
    WOOFER_CUTOUT, WOOFER_REBATE = WOOFER_OPTIONS[_W]['cutout'], WOOFER_OPTIONS[_W]['rebate']
    TRIM_RING_ID = dict(TRIM_RING_ID, woofer=WOOFER_OPTIONS[_W]['ring_id'])
    DRIVER_SCREWS = dict(DRIVER_SCREWS, woofer=WOOFER_OPTIONS[_W]['screws'])

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
    INSERT = dict(margin=1.5, eave_clip=14.0, back_y=113.0, boss_d=68.4, boss_back_y=126.0, clear=0.3,   # PROPOSAL boss 68.4 round the faceplate's 62.4 bore, flattened on the top panel (1.5 of insert under the bore); to y 126, 9.5 behind the tweeter's body, so 4 mm of gable stays over its bore under the back slope (the drawing check's d4, round 3: at 131 it was 0.26)
                  magnet_d=8.0, magnet_t=3.0, pin_d=4.0, pin_l=8.0,
                  bay_d=32.0, bay_l=22.0, bay_dz=-5.0)   # bay ø32 (was 26): a 24 mm mated pair and its lead's bend (round 4's d2)
    # Scan-Speak Illuminator D3004/602200: its 62 mm faceplate screwed to the insert's back, the dome in the 34 mm throat
    TWEETER_PART = dict(model='Scan-Speak Illuminator D3004/602200', dome_d=26.0, surround_w=4.0, flange_d=62.0, flange_t=4.5,
                        body_d=48.0, body_depth=17.0, screws=3, bolt_circle=54.0, mount='screws')
    # Shops give its cut-out as 47.8 (SoundImports) and 48 (Willy's), so the 48 body holds; its three holes are ø3.3 (M3
    # clearance: the M2.5 screws pass), their circle still unpublished; SoundImports lists it 45.3 deep without saying
    # from where: a body behind the faceplate deeper than the bore holds fails a CAD check (M3).
    # Its faceplate has its own three holes (about 55 apart, the research's estimate), so it screws to the seat from behind:
    # M2.5 low heads (ISO 7380, head 4.7 across) on the 54 circle clear the 48 body by 0.65; a body over 49 would need the
    # floorstander's sleeve, which the 3 mm boss wall here cannot hold. Knurled brass inserts bonded with epoxy hold in
    # any of the insert's materials (a heat-set insert will not melt into cured resin). PLACEHOLDER circle: measure first.
    RETAINER = None
    INSERT_SCREW = dict(hole_d=3.6, depth=5.0, insert='M2.5 x 4 knurled brass', bond='epoxy',
                        screw='M2.5 x 8 button heads (ISO 7380, A2)', head_d=4.7)
    TWEETER = dict(TWEETER, faceplate_y=WAVEGUIDE['throat_y'], z=WAVEGUIDE['throat_z'])
    DRIVER_SET = dict(woofer='sb17nrx2c35-8', mid=None, tweeter='d3004-602200')
    WOOFER_CUTOUT = 144.9                     # SPEC SB's drawing, ø144.9 (fab/research/datasheets-2026-10-09.json)
    DRIVER_SCREWS = dict(woofer=dict(n=4, pcd=159.0, hole=5.5, start_deg=45.0))   # 4 x 4.3 on 159 (fab/research/drivers-small.md)
    DRIVER_SCREW = dict(DRIVER_SCREW, tnut_flange=dict(woofer=12.0), tnut_barrel=dict(woofer=7.0))
    LEAD_ABOVE_GROMMET = 40.0    # 30 up the channel to the ø32 bay's floor and 10 into its socket (the tweeter's own lead is the slack)
    TWEETER_LEAD = dict(TWEETER_LEAD, l=220.0)   # the tabs about 134 from the socket with the insert clear of its pocket, 75 for a hand, 10 spare
    WOOFER_REBATE = dict(d=172.6, depth=10.5)  # the 171 frame + 2 x 0.8; its 6.5 flange + 1.0 of gasket + the 3 mm ring
    # SPEC 6.5: SB's drawing (REV.2, 2019) carries 6.5, which NB Audio lists as the flange's thickness; the 10.9 a shop
    # lists as 'front thickness' is everything in front of the baffle, its 85.9 overall less 75 behind: the surround
    # stands 4.4 above the flange, 1.4 proud of the ring (fab/research/datasheets-2026-10-09.json). Check the drawing's
    # labels on the part in hand (M2).
    MID_CUTOUT = None; MID_REBATE = None
    PORT = None                               # sealed: 9.2 L net (fab/out-bookshelf/acoustics.json), f3 63 Hz, a DSP shelf to 45 Hz
    POSTS = dict(POSTS, z=180.0)
    # Hypex FusionAmp FA122 upright on the back (its 315 plate will not lie across a 220 back)
    AMP = dict(model='Hypex FusionAmp FA122', plate_w=120.0, plate_h=315.0, plate_t=3.0, plate_r=4.0, module_depth=55.0,
               cut_w=96.0, cut_h=291.0, z=235.0, rebate=4.5)   # SPEC 291: Hypex's manual (R4; an Audiophonics drawing shows 293): offer the module to the 291 slot cut in scrap, and open it to 293 only if it binds (the drawing check's d10, round 7)
    AMP_BOX = dict(depth=70.0, margin=10.0, glands=2, gland='M16 x 1.5', gland_hole=16.5, gland_pitch=35.0, nut_cb=(24.0, 8.0))   # one M16 per cable
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

# Sheet 7's 'Measure first' numbers, one per bought part the drawings wait on (the HOLD marks on the sheets, the DXFs
# and stl/HOLD.txt use them): the ply, each driver, the tweeter, the amplifier, the connector
M_NUM = {'ply': 1, 'woofer': 2, **({'mid': 3} if MID else {}), 'tweeter': 3 + bool(MID), 'amp': 4 + bool(MID), 'connector': 5 + bool(MID)}
