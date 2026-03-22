#metashapes/shape/base.py
# This module defines the base Shape class, which represents symbolic 2D shapes.

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numbers
import numpy as np
import torch

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
        shape_plain = Shape.from_parametric(self.to_parametric())
        return shape_to_shapely(shape_plain)
    
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
    
    def to_torch(
        self,
        canvas: Canvas,
        *,
        dtype: torch.dtype = torch.float32,
        device: str | torch.device = "cpu",
        soft: bool = True,
        soft_mode: str = "sigmoid",
        softness: float | torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Rasterize this Shape into a torch mask on the given canvas.

        Parameters:
            canvas: The canvas to rasterize onto.
            dtype: Torch dtype of the output mask.
            device: Torch device.
            soft: If True, return a soft mask instead of a hard binary mask.
            soft_mode: "sigmoid" (support differentiable optimization) or "fourier" (support anti-aliasing). 
            softness: Edge smoothing scale in world units. If None, defaults to one pixel.
        
        Returns:
            Tensor of shape (H, W).
        
        Notes:
            soft_mode behavior:
                - "sigmoid": Signed-distance sigmoid smoothing. Intended for
                differentiable optimization and preserves gradient flow from
                shape parameters to the mask. Smaller `softness` makes the mask
                sharper but can lead to vanishing gradients, while larger
                `softness` gives smoother gradients but blurs geometry more.
                - "fourier": Gaussian low-pass filtering of a hard mask in Fourier
                space. Useful for anti-aliasing and smooth visual filtering, but
                generally not suitable for gradient-based optimization because
                hard thresholding largely destroys gradients before filtering.
        """
        from metashapes.adapters import shape_to_torch
        return shape_to_torch(
            self,
            canvas,
            dtype=dtype,
            device=device,
            soft=soft,
            soft_mode=soft_mode,
            softness=softness,
        )
    
def to_plain_data(x: Any):
    """
    Convert values to plain Python-serializable data.

    Rules:
        - Python scalars stay unchanged
        - torch scalar tensors -> Python scalar
        - torch vectors/matrices -> nested Python lists
        - NumPy scalars -> Python scalar
        - NumPy arrays -> nested Python lists
        - tuples/lists -> recursively converted, preserving container type
    """
    if isinstance(x, numbers.Number):
        return x

    if isinstance(x, torch.Tensor):
        x = x.detach().cpu()
        if x.ndim == 0:
            return x.item()
        return x.tolist()

    if isinstance(x, np.ndarray):
        if x.ndim == 0:
            return x.item()
        return x.tolist()

    if isinstance(x, tuple):
        return tuple(to_plain_data(v) for v in x)

    if isinstance(x, list):
        return [to_plain_data(v) for v in x]

    if isinstance(x, dict):
        return {k: to_plain_data(v) for k, v in x.items()}

    return x

def to_plain_scalar(x: Any):
    """
    Convert scalar-like values to a plain Python scalar.

    Accepts:
        - Python/NumPy scalars
        - 0D torch tensors
        - 1-element tensors / arrays / lists / tuples
    """
    x = to_plain_data(x)

    if isinstance(x, tuple):
        if len(x) != 1:
            raise ValueError(f"Expected scalar-like value, got tuple {x}")
        return x[0]

    if isinstance(x, list):
        if len(x) != 1:
            raise ValueError(f"Expected scalar-like value, got list {x}")
        return x[0]

    return x