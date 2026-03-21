# metashapes/shape/boolean.py
# This module defines boolean operations on shapes: union, intersection, difference.

from __future__ import annotations

from dataclasses import dataclass

from .base import Shape


@dataclass(slots=True)
class BinaryShapeOp(Shape):
    left: Shape
    right: Shape


@dataclass(slots=True)
class Union(BinaryShapeOp):
    """
    Symbolic union of two shapes.
    """
    def to_parametric(self) -> dict:
        return {
            "type": "Union",
            "left": self.left.to_parametric(),
            "right": self.right.to_parametric(),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Union":
        return cls(
            left=Shape.from_parametric(data["left"]),
            right=Shape.from_parametric(data["right"]),
        )


@dataclass(slots=True)
class Intersection(BinaryShapeOp):
    """
    Symbolic intersection of two shapes.
    """
    def to_parametric(self) -> dict:
        return {
            "type": "Intersection",
            "left": self.left.to_parametric(),
            "right": self.right.to_parametric(),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Intersection":
        return cls(
            left=Shape.from_parametric(data["left"]),
            right=Shape.from_parametric(data["right"]),
        )


@dataclass(slots=True)
class Difference(BinaryShapeOp):
    """
    Symbolic difference of two shapes: left - right.
    """
    def to_parametric(self) -> dict:
        return {
            "type": "Difference",
            "left": self.left.to_parametric(),
            "right": self.right.to_parametric(),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Difference":
        return cls(
            left=Shape.from_parametric(data["left"]),
            right=Shape.from_parametric(data["right"]),
        )