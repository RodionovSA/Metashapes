#metashapes/library.py

# This module provides a library of shapes for easy access and use.

from shapely.geometry import Polygon
from typing import Tuple
import numpy as np

from .shape import Shape
from .utils import shp

# --- Simple Shapes ---
def rectangle(center: Tuple[float, float], 
              size: Tuple[float, float], 
              angle: float = 0.0,
              *,
              soft_radius: float = 0.0) -> Shape:
    """
    Create a rectangle shape given its center, size and angle.
    Parameters:
        center: (cx, cy) coordinates of the rectangle center.
        size: (width, height) dimensions of the rectangle.
        angle: Rotation angle in degrees (counter-clockwise).
        soft_radius: Radius for softening the rectangle corners. Default is 0 (sharp corners).
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
    
    # Rotation
    if angle != 0.0:
        from shapely import affinity
        poly = affinity.rotate(poly, angle, origin=center)
    
    # Create shape object
    poly = Shape(poly, min_width=min(w,h))

    # Soften corners if requested
    if abs(float(soft_radius)) > 0.0:
        if abs(float(soft_radius)) > min(w, h)/2:
            raise ValueError("soft_radius is too large for the given rectangle size.")
        poly = shp.soften_corners(poly, radius=soft_radius)

    return poly

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
        from shapely import affinity
        poly = affinity.rotate(poly, angle, origin=center)

    return Shape(poly, min_width=2*min(a,b))

def ngon(center: Tuple[float, float], 
          size: float, 
          n: int,
          angle: float = 0.0,
          *,
          soft_radius: float = 0.0) -> Shape:
    """
    Create a regular polygon shape given its center, side length and number of sides.
    Parameters:
        center: (cx, cy) coordinates of the polygon center.
        size: Length of each side of the polygon.
        n: Number of sides (vertices) of the polygon.
        angle: Rotation angle in degrees (counter-clockwise).
        soft_radius: Radius for softening the polygon corners. Default is 0 (sharp corners).
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
    
    # Rotation
    if angle != 0.0:
        from shapely import affinity
        poly = affinity.rotate(poly, angle, origin=center)
        
    # Create shape object
    poly = Shape(poly, min_width=size/(2*np.tan(np.pi / n)))
        
    # Soften corners if requested
    if abs(float(soft_radius)) > 0.0:
        if abs(float(soft_radius)) > min(size, size / (2*np.tan(np.pi / n))):
            raise ValueError("soft_radius is too large for the given polygon size.")
        poly = shp.soften_corners(poly, radius=soft_radius)

    return poly


# --- Compound Shapes ---
def cross(center: Tuple[float, float], 
          size: float, 
          width: float = 0.1,
          angle: float = 0.0,
          *,
          soft_radius: float = 0.0) -> Shape:
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
    cross_shape.min_width = min(width, size)
    
    # Rotation  
    if angle != 0.0:
        cross_shape = shp.rotate(cross_shape, angle, origin=center)
        
    # Soften corners if requested
    if abs(float(soft_radius)) > 0.0:
        if abs(float(soft_radius)) > min(width, size)/2:
            raise ValueError("soft_radius is too large for the given cross size.")
        cross_shape = shp.soften_corners(cross_shape, radius=soft_radius)
        
    return cross_shape

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
    ring_shape.min_width = min(outer_radius[0] - inner_radius[0], 
                               outer_radius[1] - inner_radius[1])
    ring_shape.min_gap = 2*min(inner_radius[0], inner_radius[1])
    
    # Rotation
    if angle != 0.0:
        ring_shape = shp.rotate(ring_shape, angle, origin=center)
    
    return ring_shape

def moon(center: Tuple[float, float], 
         radius: float, 
         cut_ratio: float = 0.5,
         angle: float = 0.0,
         resolution: int = 64,
         *,
         soft_radius: float = 0.0) -> Shape:
    """
    Create a moon shape given its center, radius and cut ratio.
    Parameters:
        center: (cx, cy) coordinates of the moon center.
        radius: Radius of the main circle.
        cut_ratio: Ratio of the cut circle radius to the main circle radius (0 < cut_ratio < 1).
        angle: Rotation angle in degrees (counter-clockwise).
        resolution: Number of points to approximate the circles.
        soft_radius: Radius for softening the polygon corners. Default is 0 (sharp corners).
    Returns:
        A Shape object representing the moon.
    """
    
    if radius <= 0:
        raise ValueError("radius must be positive.")
    if cut_ratio <= 0 or cut_ratio >= 1:
        raise ValueError("cut_ratio must be in the range (0, 1).")
    
    cx, cy = center
    main_circle = ellipse(center, (radius, radius), angle, resolution)
    cut_circle = ellipse((cx + 2*radius * (1 - cut_ratio), cy), 
                        (radius, radius), 
                        angle, resolution)
    
    moon_shape = main_circle.difference(cut_circle)
    moon_shape.min_width = 2*radius * (1 - cut_ratio)
    
    # Rotation
    if angle != 0.0:
        moon_shape = shp.rotate(moon_shape, angle, origin=center)
        
    # Soften corners if requested
    if abs(float(soft_radius)) > 0.0:
        if abs(float(soft_radius)) > radius:
            raise ValueError("soft_radius is too large for the given polygon size.")
        moon_shape = shp.soften_corners(moon_shape, radius=soft_radius)

    return moon_shape
