# metashapes/utils.py

# This module provides utility functions for the metashapes package.

from .shape import Shape
    
# --- Shape Transformations ---
# Just wrappers around shapely.affinity functions to maintain Shape type

def rotate(shape: 'Shape', angle: float, origin = 'center') -> 'Shape':
    """
    Rotate a Shape by a given angle around a specified origin.
    Parameters:
        shape: The Shape to rotate.
        angle: Rotation angle in degrees (counter-clockwise).
        origin: The point of rotation. Can be 'center', 'centroid', or a tuple (x, y).
    Returns:
        A new rotated Shape.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
        
    from shapely.affinity import rotate as shapely_rotate
    rotated_geom = shapely_rotate(shape.geom, angle, origin=origin)
    return Shape(rotated_geom)

def translate(shape: 'Shape', dx: float, dy: float) -> 'Shape':
    """
    Translate a Shape by a given distance in the x and y directions.
    Parameters:
        shape: The Shape to translate.
        dx: Distance to move in the x direction.
        dy: Distance to move in the y direction.
    Returns:
        A new translated Shape.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
    
    from shapely.affinity import translate as shapely_translate
    translated_geom = shapely_translate(shape.geom, xoff=dx, yoff=dy)
    return Shape(translated_geom)

def scale(shape: 'Shape', sx: float, sy: float = None, origin = 'center') -> 'Shape':
    """
    Scale a Shape by given factors in the x and y directions.
    Parameters:
        shape: The Shape to scale.
        sx: Scaling factor in the x direction.
        sy: Scaling factor in the y direction. If None, sy = sx.
        origin: The point of scaling. Can be 'center', 'centroid', or a tuple (x, y).
    Returns:
        A new scaled Shape.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
    
    from shapely.affinity import scale as shapely_scale
    if sy is None:
        sy = sx
    scaled_geom = shapely_scale(shape.geom, xfact=sx, yfact=sy, origin=origin)
    return Shape(scaled_geom)

def skew(shape: 'Shape', angle_x: float = 0.0, angle_y: float = 0.0, origin = 'center') -> 'Shape':
    """
    Skew a Shape by given angles in the x and y directions.
    Parameters:
        shape: The Shape to skew.
        angle_x: Skew angle in degrees along the x axis.
        angle_y: Skew angle in degrees along the y axis.
        origin: The point of skewing. Can be 'center', 'centroid', or a tuple (x, y).
    Returns:
        A new skewed Shape.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
    
    from shapely.affinity import skew as shapely_skew
    skewed_geom = shapely_skew(shape.geom, xs=angle_x, ys=angle_y, origin=origin)
    return Shape(skewed_geom)

# --- WKT and WKB Conversions ---
import shapely.wkt as wkt
import shapely.wkb as wkb

def to_wkt(shape: 'Shape') -> str:
    """
    Convert a Shape to its WKT (Well-Known Text) representation.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
    return wkt.dumps(shape.geom)

def from_wkt(wkt_string: str) -> 'Shape':
    """
    Convert a WKT (Well-Known Text) representation to a Shape.
    """
    geom = wkt.loads(wkt_string)
    return Shape(geom)

def to_wkb(shape: 'Shape') -> bytes:
    """
    Convert a Shape to its WKB (Well-Known Binary) representation.
    """
    if not isinstance(shape, Shape):
        raise TypeError("shape must be an instance of Shape.")
    return wkb.dumps(shape.geom)

def from_wkb(wkb_bytes: bytes) -> 'Shape':
    """
    Convert a WKB (Well-Known Binary) representation to a Shape.
    """
    geom = wkb.loads(wkb_bytes)
    return Shape(geom)

# --- Additional Utilities ---
def unary_union(shapes: list['Shape']) -> 'Shape':
    """
    Perform a unary union on a list of Shapes.
    Parameters:
        shapes: List of Shape objects to union.
    Returns:
        A new Shape representing the union of all input shapes.
    """
    from shapely import unary_union as shapely_unary_union
    geoms = [shape.geom for shape in shapes if isinstance(shape, Shape)]
    if not geoms:
        raise ValueError("The input list must contain at least one Shape.")
    unioned_geom = shapely_unary_union(geoms)
    return Shape(unioned_geom)
