# metashapes/fabtol.py

# This module provides functions to compute fabrication tolerances for geometric shapes.

from shapely.geometry import box, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
from shapely.geometry.base import BaseGeometry

from typing import List
from .shape import Shape

