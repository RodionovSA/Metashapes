#metashapes/shape/base.py
# This module defines the base Shape class, which represents symbolic 2D shapes.

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from shapely.geometry.base import BaseGeometry
from metashapes.canvas import Canvas


class Shape(ABC):
    """
    Base class for all symbolic 2D shapes.

    A Shape stores a geometric recipe, not resolved polygon data.
    It can later be evaluated by different backends.
    """

    def __or__(self, other: "Shape") -> "Shape":
        from .boolean import Union
        return Union(self, other)

    def __and__(self, other: "Shape") -> "Shape":
        from .boolean import Intersection
        return Intersection(self, other)

    def __sub__(self, other: "Shape") -> "Shape":
        from .boolean import Difference
        return Difference(self, other)
    
    def union(self, other: "Shape") -> "Shape":
        from .boolean import Union
        return Union(self, other)
    
    def intersection(self, other: "Shape") -> "Shape":
        from .boolean import Intersection
        return Intersection(self, other)
    
    def difference(self, other: "Shape") -> "Shape":
        from .boolean import Difference
        return Difference(self, other)

    def translate(self, dx: Any = 0.0, dy: Any = 0.0) -> "Shape":
        from .transforms import Translate
        return Translate(self, dx=dx, dy=dy)

    def rotate(
        self,
        angle: Any,
        origin: tuple[Any, Any] = (0.0, 0.0),
    ) -> "Shape":
        from .transforms import Rotate
        return Rotate(self, angle=angle, origin=origin)

    def scale(
        self,
        sx: Any,
        sy: Any | None = None,
        origin: tuple[Any, Any] = (0.0, 0.0),
    ) -> "Shape":
        from .transforms import Scale
        if sy is None:
            sy = sx
        return Scale(self, sx=sx, sy=sy, origin=origin)

    @abstractmethod
    def to_parametric(self) -> dict:
        """
        Serialize the symbolic shape into a dictionary.
        """
        raise NotImplementedError
    
    @classmethod
    def from_parametric(cls, data: dict) -> "Shape":
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        shape_type = data.get("type")
        if shape_type is None:
            raise ValueError("Missing 'type' in shape parametric data")
        
        from .primitives import (
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
        from .boolean import Union, Intersection, Difference
        from .transforms import Translate, Rotate, Scale

        REGISTRY = {
                "Rectangle": Rectangle,
                "Ellipse": Ellipse,
                "RegularPolygon": RegularPolygon,
                "Cross": Cross,
                "Ring": Ring,
                "Moon": Moon,
                "RoundedRectangle": RoundedRectangle,
                "RoundedRegularPolygon": RoundedRegularPolygon,
                "RoundedCross": RoundedCross,
                "RoundedMoon": RoundedMoon,
                "Union": Union,
                "Intersection": Intersection,
                "Difference": Difference,
                "Translate": Translate,
                "Rotate": Rotate,
                "Scale": Scale,
                }

        try:
            shape_cls = REGISTRY[shape_type]
        except KeyError as e:
            raise ValueError(f"Unknown shape type: {shape_type}") from e

        return shape_cls.from_parametric(data)
    
    def to_shapely(self) -> BaseGeometry:
        """
        Convert this Shape into a Shapely geometry.
        """
        from metashapes.adapters import shape_to_shapely
        return shape_to_shapely(self)
    
    def to_numpy(self, 
                 canvas: Canvas, 
                 *, 
                 dtype=bool, 
                 soft: bool = False, 
                 soft_mode: str = "sigmoid", 
                 softness: float | None = None) -> np.ndarray:
        """
        Rasterize this Shape into a NumPy array of the given canvas size.

        Parameters:
            canvas: The canvas to rasterize onto.
            dtype: The desired data type of the output array.
            soft: If True, return a soft mask instead of a hard binary mask.
            soft_mode: The mode to use for softening the mask ("sigmoid" or "fourier").
            softness: The scale of the softness in world units. If None, defaults to one pixel.
        """
        from metashapes.adapters import shape_to_numpy
        return shape_to_numpy(self, canvas, dtype=dtype, soft=soft, soft_mode=soft_mode, softness=softness)