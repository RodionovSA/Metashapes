# metashapes/adapters/shapely/conics.py
# This file contains the adapter function to convert Conic shapes to Shapely geometries.

from __future__ import annotations

import numpy as np
from shapely.affinity import rotate as shp_rotate
from shapely.affinity import scale as shp_scale
from shapely.affinity import translate as shp_translate
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry

import metashapes.shape.primitives as prim

def ellipse_to_shapely(shape: prim.Ellipse) -> BaseGeometry:
    cx, cy = shape.center.tolist()
    a, b = shape.axes.tolist()
    angle = shape.angle.item()

    geom = Point(0.0, 0.0).buffer(1.0, quad_segs=64 // 4)
    geom = shp_scale(geom, xfact=a*0.5, yfact=b*0.5, origin=(0.0, 0.0))
    geom = shp_rotate(geom, angle, origin=(0.0, 0.0))
    geom = shp_translate(geom, xoff=cx, yoff=cy)
    return geom


def egg_to_shapely(shape: prim.Egg) -> BaseGeometry:
    cx, cy = shape.center.tolist()
    a = shape.width.item() / 2.0
    skew = shape.skew.item()
    h_half = shape.height.item() / 2.0
    b_top = h_half * (1.0 + skew)
    b_bot = h_half * (1.0 - skew)
    angle = shape.angle.item()

    n = 64
    t_upper = np.linspace(0.0, np.pi, n, endpoint=False)
    t_lower = np.linspace(np.pi, 2.0 * np.pi, n, endpoint=False)

    xs = np.concatenate([a * np.cos(t_upper), a * np.cos(t_lower)])
    ys = np.concatenate([b_top * np.sin(t_upper), b_bot * np.sin(t_lower)])

    theta = np.deg2rad(angle)
    c, s = np.cos(theta), np.sin(theta)
    xs_rot = xs * c - ys * s + cx
    ys_rot = xs * s + ys * c + cy

    return Polygon(zip(xs_rot, ys_rot))


def stadium_to_shapely(shape: prim.Stadium) -> BaseGeometry:
    cx, cy = shape.center.tolist()
    radius = shape.width.item() / 2.0
    half_span = max(shape.length.item() / 2.0 - radius, 0.0)
    angle = shape.angle.item()

    if half_span == 0.0:
        geom = Point(0.0, 0.0).buffer(radius)
    else:
        geom = LineString([(-half_span, 0.0), (half_span, 0.0)]).buffer(radius)

    geom = shp_rotate(geom, angle, origin=(0.0, 0.0))
    geom = shp_translate(geom, xoff=cx, yoff=cy)
    return geom
