"""earnest: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).

The owner's idea (2026-10-08): if earmilk gets a standalone amplifier, it is an egg crate whose eggs are the valves,
egg-shaped glass bulbs sitting in the cups, in a 6-pack and a 12-pack, maybe a Costco-sized 24-pack; the egg-crate
shape on top. Everything below is PROPOSAL unless marked."""

# The packs: rows x columns of cups (PROPOSAL). Half a dozen, a dozen, and the warehouse-club flat.
PACKS = {6: (2, 3), 12: (2, 6), 24: (4, 6)}

# The crate (PROPOSAL)
PITCH = 74.0          # cup centre to cup centre, both ways
CUP_TOP = 66.0        # a cup's nominal width; with MARGIN it sets the crate's size
CUP_DEPTH = 38.0      # top plane to the cup's floor
MARGIN = 10.0         # outer cup to the crate's edge: narrow, so the cups run nearly to the edge as on a carton
HEIGHT = 112.0        # floor to the top plane: room for the transformers under the cups
DRAFT_DEG = 5.0       # the sides lean in toward the top, like a moulded tray
EDGE_R = 12.0         # the crate's corner radius in plan
FOOT = (34.0, 6.0)    # four rubber feet: diameter, height

# The top is a pulp tray's surface (PROPOSAL), not a deck with holes in it: each cup fills its square cell, its wall
# rising from a flat floor to a low ridge it shares with the next cup; a cone stands where four cups meet (on a real
# carton, the posts that hold the lid); a flat flange runs round the edge. Built as a height field, then a CAD surface.
CUP_PLAN_P = 3.2      # the cups' shape in plan, a superellipse's exponent: 2 is round, larger is squarer
FLOOR_R = 19.0        # the cup's flat floor, radius: the valve's socket sits in it
RIDGE_H = 2.0         # where two cups meet, above the top plane
POST_TIP_D = 9.0      # a cone's rounded tip
POST_H = 26.0         # how far a cone's tip stands above the top plane
CONE_FOOT_R = 19.0    # where a cone leaves the ridges
CONE_BLEND = 7.0      # the fillet where cones and ridges meet
FLANGE = (4.0, 8.0)   # the flat flange round the edge, where a carton's lid would close: height above the top plane,
                      # and the width over which the cups' surface eases into it
SURFACE_STEP = 3.0    # the height field's sample spacing for the top's CAD surface (STEP)
MESH_STEP = 1.0       # and for the crate's mesh (STL)

# The egg valves (PROPOSAL for the envelope; the valve inside is a PLACEHOLDER until a maker quotes custom glass).
# A real candidate: a 300B power triode in an egg-shaped envelope, as some makers still blow special envelopes (KR Audio's
# balloon 300B, for one).
# Eggs sit in a carton blunt end up, so the valves stand on their tips, the getter's silver in the dome.
EGG_L = 80.0          # tip to dome
EGG_D = 58.0          # widest
EGG_K = 0.14          # how much narrower the tip end is than the dome end
GLASS_T = 1.4         # the envelope's wall
BASE_D = 30.0         # the valve's base (Bakelite), seated in its socket in the cup's floor
BASE_H = 14.0
BASE_SINK = 9.0       # how far the base sits below the cup's floor
PLATE = (24.0, 11.0, 30.0)   # the anode inside: width, depth, height
GETTER_FROM = 0.94    # the getter's silver mirror covers the dome above this fraction of the egg's length: a cap, so
                      # the glass still reads as glass from above

# The knobs are eggs too (PROPOSAL): a white one turns the volume, a brown one picks the input.
KNOB_SCALE = 0.86     # a knob egg against a valve egg
