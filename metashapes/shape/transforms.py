# metashapes/shape/transforms.py
# This module defines symbolic shape transformations: translation, rotation, scaling.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import Shape


@dataclass(slots=True)
class Translate(Shape):
    """
    Symbolic translation of a shape.
    """
    shape: Shape
    dx: Any = 0.0
    dy: Any = 0.0

    def to_parametric(self) -> dict:
        return {
            "type": "Translate",
            "shape": self.shape.to_parametric(),
            "dx": self.dx,
            "dy": self.dy,
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Translate":
        return cls(
            shape=Shape.from_parametric(data["shape"]),
            dx=data.get("dx", 0.0),
            dy=data.get("dy", 0.0),
        )


@dataclass(slots=True)
class Rotate(Shape):
    """
    Symbolic rotation of a shape.
    """
    shape: Shape
    angle: Any
    origin: tuple[Any, Any] = (0.0, 0.0)

    def to_parametric(self) -> dict:
        return {
            "type": "Rotate",
            "shape": self.shape.to_parametric(),
            "angle": self.angle,
            "origin": self.origin,
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Rotate":
        return cls(
            shape=Shape.from_parametric(data["shape"]),
            angle=data["angle"],
            origin=data.get("origin", "center"),
        )


@dataclass(slots=True)
class Scale(Shape):
    """
    Symbolic scaling of a shape.
    """
    shape: Shape
    sx: Any
    sy: Any
    origin: tuple[Any, Any] = (0.0, 0.0)

    def to_parametric(self) -> dict:
        return {
            "type": "Scale",
            "shape": self.shape.to_parametric(),
            "sx": self.sx,
            "sy": self.sy,
            "origin": self.origin,
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Scale":
        return cls(
            shape=Shape.from_parametric(data["shape"]),
            sx=data["sx"],
            sy=data["sy"],
            origin=data.get("origin", "center"),
        )