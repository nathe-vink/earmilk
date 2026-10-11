"""Everything a product file needs, in one import:

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'studio', 'fabkit'))
    from kit import *
"""
from model import Part, Product, Sheet, Printed, Machined, Bought, SHEETS, PRINTS, SOLIDS  # noqa: F401
from geom import box, cyl, prism, rounded_rect, circle_pts, revolve_profile, union, bbox, slotted_panel  # noqa: F401

__all__ = ['Part', 'Product', 'Sheet', 'Printed', 'Machined', 'Bought', 'SHEETS', 'PRINTS', 'SOLIDS',
           'box', 'cyl', 'prism', 'rounded_rect', 'circle_pts', 'revolve_profile', 'union', 'bbox', 'slotted_panel']
