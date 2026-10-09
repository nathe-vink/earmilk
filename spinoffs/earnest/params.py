"""earnest: every number the model uses, in millimetres. Marked like earmilk's fab/params.py:
SPEC (signed off by the owner), PROPOSAL (this repo's suggestion), PLACEHOLDER (waits on a bought part).

The owner's idea (2026-10-08): if earmilk gets a standalone amplifier, it is an egg crate whose eggs are the valves,
egg-shaped glass bulbs sitting in the cups, in a 6-pack and a 12-pack, maybe a Costco-sized 24-pack; the egg-crate
shape on top. Everything below is PROPOSAL unless marked."""

# The packs: rows x columns of cups (PROPOSAL). Half a dozen, a dozen, and the warehouse-club flat.
PACKS = {6: (2, 3), 12: (2, 6), 24: (4, 6)}

# The crate (PROPOSAL)
PITCH = 74.0          # cup centre to cup centre, both ways
CUP_TOP = 66.0        # the cup's mouth: a rounded square this wide at the top plane
CUP_TOP_R = 22.0      # its corner radius
CUP_DEPTH = 38.0      # top plane to the cup's floor
CUP_FLOOR_D = 40.0    # the floor's diameter
POST_D = (26.0, 9.0) # the cones that stand between four cups (and hold the lid on a real carton): base, top
POST_H = 26.0         # how far a cone stands above the top plane
MARGIN = 16.0         # outer cup mouth to the crate's edge
HEIGHT = 112.0        # floor to the top plane: room for the transformers under the cups
DRAFT_DEG = 5.0       # the sides lean in toward the top, like a moulded tray
EDGE_R = 12.0         # the crate's corner radius in plan
FOOT = (34.0, 6.0)    # four rubber feet: diameter, height
RIM = (7.0, 4.0)      # the flange round the top edge where a carton's lid would close: width, height

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
GETTER_FROM = 0.88    # the getter's silver mirror covers the dome above this fraction of the egg's length

# The knobs are eggs too (PROPOSAL): a white one turns the volume, a brown one picks the input.
KNOB_SCALE = 0.86     # a knob egg against a valve egg
