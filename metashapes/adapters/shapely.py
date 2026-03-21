# metashapes/adapters/shapely.py
# Adapter to convert symbolic Shapes into Shapely geometries for visualization and export.

from __future__ import annotations
from typing import Literal

from shapely.affinity import rotate as shp_rotate
from shapely.affinity import scale as shp_scale
from shapely.affinity import translate as shp_translate
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry

import numpy as np

from metashapes.shape.base import Shape
from metashapes.shape.primitives import (
    Rectangle,
    Ellipse,
    RegularPolygon,
    Cross,
    Ring,
    Moon,
    RoundedRectangle,
    RoundedRegularPolygon,
    RoundedCross,
    RoundedMoon,
)
from metashapes.shape.boolean import Union, Intersection, Difference
from metashapes.shape.transforms import Translate, Rotate, Scale


def shape_to_shapely(shape: Shape) -> BaseGeometry:
    """
    Convert a symbolic Shape into a Shapely geometry.
    """
    if isinstance(shape, Rectangle):
        return _rectangle_to_shapely(shape)

    if isinstance(shape, Ellipse):
        return _ellipse_to_shapely(shape)

    if isinstance(shape, RegularPolygon):
        return _regular_polygon_to_shapely(shape)

    if isinstance(shape, Cross):
        return _cross_to_shapely(shape)

    if isinstance(shape, Ring):
        return _ring_to_shapely(shape)

    if isinstance(shape, Moon):
        return _moon_to_shapely(shape)

    if isinstance(shape, RoundedRectangle):
        return _rounded_rectangle_to_shapely(shape)

    if isinstance(shape, RoundedRegularPolygon):
        return _rounded_regular_polygon_to_shapely(shape)

    if isinstance(shape, RoundedCross):
        return _rounded_cross_to_shapely(shape)

    if isinstance(shape, RoundedMoon):
        return _rounded_moon_to_shapely(shape)

    if isinstance(shape, Union):
        return shape_to_shapely(shape.left).union(shape_to_shapely(shape.right))

    if isinstance(shape, Intersection):
        return shape_to_shapely(shape.left).intersection(shape_to_shapely(shape.right))

    if isinstance(shape, Difference):
        return shape_to_shapely(shape.left).difference(shape_to_shapely(shape.right))

    if isinstance(shape, Translate):
        geom = shape_to_shapely(shape.shape)
        return shp_translate(geom, xoff=shape.dx, yoff=shape.dy)

    if isinstance(shape, Rotate):
        geom = shape_to_shapely(shape.shape)
        return shp_rotate(geom, shape.angle, origin=shape.origin)

    if isinstance(shape, Scale):
        geom = shape_to_shapely(shape.shape)
        return shp_scale(geom, xfact=shape.sx, yfact=shape.sy, origin=shape.origin)

    raise TypeError(f"Unsupported shape type: {type(shape).__name__}")


def _rectangle_to_shapely(shape: Rectangle) -> BaseGeometry:
    cx, cy = shape.center
    w, h = shape.size

    geom = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    if shape.angle != 0:
        geom = shp_rotate(geom, shape.angle, origin=shape.center)
    return geom


def _ellipse_to_shapely(shape: Ellipse) -> BaseGeometry:
    cx, cy = shape.center
    a, b = shape.axes

    geom = Point(0.0, 0.0).buffer(1.0, quad_segs=shape.resolution // 4)
    geom = shp_scale(geom, xfact=a, yfact=b, origin=(0.0, 0.0))
    geom = shp_rotate(geom, shape.angle, origin=(0.0, 0.0))
    geom = shp_translate(geom, xoff=cx, yoff=cy)
    return geom


def _regular_polygon_to_shapely(shape: RegularPolygon) -> BaseGeometry:
    cx, cy = shape.center
    n = shape.n
    s = shape.side_length

    R = s / (2.0 * np.sin(np.pi / n))
    phi = np.pi / 2.0

    points = [
        (
            cx + R * np.cos(2.0 * np.pi * k / n + phi),
            cy + R * np.sin(2.0 * np.pi * k / n + phi),
        )
        for k in range(n)
    ]

    geom = Polygon(points)
    if shape.angle != 0:
        geom = shp_rotate(geom, shape.angle, origin=shape.center)
    return geom


def _cross_to_shapely(shape: Cross) -> BaseGeometry:
    cx, cy = shape.center
    vertical = _rectangle_to_shapely(Rectangle(center=(cx, cy), size=(shape.width, shape.size)))
    horizontal = _rectangle_to_shapely(Rectangle(center=(cx, cy), size=(shape.size, shape.width)))
    geom = vertical.union(horizontal)
    if shape.angle != 0:
        geom = shp_rotate(geom, shape.angle, origin=shape.center)
    return geom


def _ring_to_shapely(shape: Ring) -> BaseGeometry:
    outer = _ellipse_to_shapely(
        Ellipse(
            center=shape.center,
            axes=shape.outer_axes,
            angle=shape.angle,
            resolution=shape.resolution,
        )
    )
    inner = _ellipse_to_shapely(
        Ellipse(
            center=shape.center,
            axes=shape.inner_axes,
            angle=shape.angle,
            resolution=shape.resolution,
        )
    )
    return outer.difference(inner)


def _moon_to_shapely(shape: Moon) -> BaseGeometry:
    cx, cy = shape.center
    main = _ellipse_to_shapely(
        Ellipse(center=shape.center, axes=(shape.radius, shape.radius), resolution=shape.resolution)
    )
    cut = _ellipse_to_shapely(
        Ellipse(
            center=(cx + 2.0 * shape.radius * (1.0 - shape.cut_ratio), cy),
            axes=(shape.radius, shape.radius),
            resolution=shape.resolution,
        )
    )
    geom = main.difference(cut)
    if shape.angle != 0:
        geom = shp_rotate(geom, shape.angle, origin=shape.center)
    return geom


def _rounded_rectangle_to_shapely(shape: RoundedRectangle):
    cx, cy = shape.center
    w, h = shape.size
    r = shape.radius

    if r == 0:
        return _rectangle_to_shapely(
            Rectangle(center=shape.center, size=shape.size, angle=shape.angle)
        )

    if r > min(w, h) / 2:
        raise ValueError("RoundedRectangle radius is too large")

    inner = box(
        cx - (w / 2 - r),
        cy - (h / 2 - r),
        cx + (w / 2 - r),
        cy + (h / 2 - r),
    ).buffer(r)

    if shape.angle != 0:
        inner = shp_rotate(inner, shape.angle, origin=shape.center)

    return inner


def _rounded_regular_polygon_to_shapely(shape: RoundedRegularPolygon) -> BaseGeometry:
    base = _regular_polygon_to_shapely(
        RegularPolygon(
            center=shape.center,
            n=shape.n,
            side_length=shape.side_length,
            angle=shape.angle,
        )
    )
    if shape.radius == 0:
        return base
    return round_corners(base, radius=shape.radius, mode="inner")


def _rounded_cross_to_shapely(shape: RoundedCross) -> BaseGeometry:
    base = _cross_to_shapely(
        Cross(center=shape.center, size=shape.size, width=shape.width, angle=shape.angle)
    )
    if shape.radius == 0:
        return base
    return round_corners(base, radius=shape.radius, mode="both")


def _rounded_moon_to_shapely(shape: RoundedMoon) -> BaseGeometry:
    base = _moon_to_shapely(
        Moon(
            center=shape.center,
            radius=shape.radius,
            cut_ratio=shape.cut_ratio,
            angle=shape.angle,
            resolution=shape.resolution,
        )
    )
    if shape.rounding_radius == 0:
        return base
    return round_corners(base, radius=shape.rounding_radius, mode="inner")

RoundMode = Literal["inner", "outer", "both"]

def round_corners(
    geom: BaseGeometry,
    radius: float,
    *,
    mode: RoundMode = "both",
    quad_segs: int = 32,
) -> BaseGeometry:
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if quad_segs < 1:
        raise ValueError("quad_segs must be at least 1")
    if radius == 0:
        return geom

    if mode in {"outer", "both"}:
        geom = geom.buffer(radius, quad_segs=quad_segs)
        geom = geom.buffer(-radius, quad_segs=quad_segs)

    if mode in {"inner", "both"}:
        geom = geom.buffer(-radius, quad_segs=quad_segs)
        geom = geom.buffer(radius, quad_segs=quad_segs)

    return geom