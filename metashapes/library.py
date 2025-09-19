#metashapes/library.py

# This module provides a library of shapes for easy access and use.

from shapely.geometry import Polygon
from typing import Tuple
import numpy as np

from .shape import Shape

# --- Simple Shapes ---
def rectangle(center: Tuple[float, float], 
              size: Tuple[float, float], 
              angle: float = 0.0) -> Shape:
    """
    Create a rectangle shape given its center, size and angle.
    Parameters:
        center: (cx, cy) coordinates of the rectangle center.
        size: (width, height) dimensions of the rectangle.
        angle: Rotation angle in degrees (counter-clockwise).
    Returns:
        A Shape object representing the rectangle.
    """

    if size[0] <= 0 or size[1] <= 0:
        raise ValueError("size dimensions must be positive.")

    cx, cy = center
    w, h = size
    
    poly = Polygon([
            (cx - w/2, cy - h/2),
            (cx + w/2, cy - h/2),
            (cx + w/2, cy + h/2),
            (cx - w/2, cy + h/2)
        ])
    
    if angle != 0.0:
        from shapely.affinity import rotate
        poly = rotate(poly, angle, origin=center)
    return Shape(poly)

def ellipse(center: Tuple[float, float], 
            axes: Tuple[float, float],
            angle: float = 0.0,
            resolution: int = 64) -> Shape:
    """
    Create an ellipse shape given its center and axes lengths.
    Parameters:
        center: (cx, cy) coordinates of the ellipse center.
        axes: (a, b) lengths of the semi-major and semi-minor axes.
        angle: Rotation angle in degrees (counter-clockwise).
        resolution: Number of points to approximate the ellipse.
    Returns:
        A Shape object representing the ellipse.
    """
    if axes[0] <= 0 or axes[1] <= 0:
        raise ValueError("axes lengths must be positive.")
    
    cx, cy = center
    a, b = axes
    
    points = np.zeros((resolution, 2))
    points[:,0] = cx + a * np.cos(2 * np.pi * np.arange(resolution) / resolution)
    points[:,1] = cy + b * np.sin(2 * np.pi * np.arange(resolution) / resolution)

    poly = Polygon(points)
    if angle != 0.0:
        from shapely.affinity import rotate
        poly = rotate(poly, angle, origin=center)
        
    return Shape(poly)

def ngon(center: Tuple[float, float], 
          size: float, 
          n: int,
          angle: float = 0.0) -> Shape:
    """
    Create a regular polygon shape given its center, side length and number of sides.
    Parameters:
        center: (cx, cy) coordinates of the polygon center.
        size: Length of each side of the polygon.
        n: Number of sides (vertices) of the polygon.
        angle: Rotation angle in degrees (counter-clockwise).
    Returns:
        A Shape object representing the regular polygon.
    """
    if size <= 0:
        raise ValueError("size must be positive.")

    if n < 3:
        raise ValueError("n must be at least 3.")
    
    # Convert side length -> circumradius
    # For a regular n-gon: s = 2 R sin(pi/n)  =>  R = s / (2 sin(pi/n))
    R = size / (2.0 * np.sin(np.pi / n))
    phi = np.pi / 2.0  # put one vertex at the top


    # Build unrotated vertices (counterclockwise), centered at `center`.
    cx, cy = center
    points = [(cx + R * np.cos(2 * np.pi * k / n + phi),
               cy + R * np.sin(2 * np.pi * k / n + phi))
              for k in range(n)]
    
    poly = Polygon(points)
    if angle != 0.0:
        from shapely.affinity import rotate
        poly = rotate(poly, angle, origin=center)

    return Shape(poly)


# --- Compound Shapes ---
def cross(center: Tuple[float, float], 
          size: float, 
          width: float = 0.1,
          angle: float = 0.0) -> Shape:
    """
    Create a cross shape given its center, size and arm width.
    Parameters:
        center: (cx, cy) coordinates of the cross center.
        size: Total length of each arm of the cross.
        width: Width of each arm of the cross.
        angle: Rotation angle in degrees (counter-clockwise).
    Returns:
        A Shape object representing the cross.
    """
    if size <= 0:
        raise ValueError("size must be positive.")
    if width <= 0:
        raise ValueError("width must be positive.")

    cx, cy = center

    # Create the vertical and horizontal rectangles
    vertical = rectangle((cx, cy), (width, size))
    horizontal = rectangle((cx, cy), (size, width))

    # Combine the two rectangles into a single shape
    cross_shape = vertical.union(horizontal)
    
    if angle != 0.0:
        from shapely.affinity import rotate
        cross_shape = rotate(cross_shape.geom, angle, origin=center)
        
    return Shape(cross_shape)

def ring(center: Tuple[float, float], 
         outer_radius: Tuple[float, float], 
         inner_radius: Tuple[float, float],
         angle: float = 0.0,
         resolution: int = 64) -> Shape:
    """
    Create a ring shape given its center, outer and inner radii.
    Parameters:
        center: (cx, cy) coordinates of the ring center.
        outer_radius: Radius of the outer circle.
        inner_radius: Radius of the inner circle (hole).
        angle: Rotation angle in degrees (counter-clockwise).
        resolution: Number of points to approximate the circles.
    Returns:
        A Shape object representing the ring.
    """
    if outer_radius[0] <= 0 or outer_radius[1] <= 0:
        raise ValueError("outer_radius must be positive.")
    if inner_radius[0] <= 0 or inner_radius[1] <= 0:
        raise ValueError("inner_radius must be positive.")
    
    if inner_radius[0] >= outer_radius[0] or inner_radius[1] >= outer_radius[1]:
        raise ValueError("inner_radius must be smaller than outer_radius.")

    outer_circle = ellipse(center, outer_radius, angle, resolution)
    inner_circle = ellipse(center, inner_radius, angle, resolution)

    ring_shape = outer_circle.difference(inner_circle)
    if angle != 0.0:
        from shapely.affinity import rotate
        ring_shape = rotate(ring_shape.geom, angle, origin=center)
    
    return Shape(ring_shape)
