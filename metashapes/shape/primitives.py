# metashapes/shape/primitives.py
# This module defines shape primitives

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import Shape, to_plain_data, to_plain_scalar


@dataclass(slots=True)
class Rectangle(Shape):
    """
    Symbolic rectangle.

    Parameters:
        center: (cx, cy)
        size: (width, height)
        angle: counter-clockwise rotation angle in degrees
    """
    center: tuple[Any, Any]
    size: tuple[Any, Any]
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if len(self.size) != 2:
            raise ValueError("size must have length 2")

    def to_parametric(self) -> dict:
        return {
            "type": "Rectangle",
            "center": to_plain_data(self.center),
            "size": to_plain_data(self.size),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Rectangle":
        return cls(
            center=tuple(data["center"]),
            size=tuple(data["size"]),
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class Ellipse(Shape):
    """
    Symbolic ellipse.

    Parameters:
        center: (cx, cy)
        axes: semi-axes (a, b)
        angle: counter-clockwise rotation angle in degrees
        resolution: optional hint for evaluators that approximate the ellipse
    """
    center: tuple[Any, Any]
    axes: tuple[Any, Any]
    angle: Any = 0.0
    resolution: int = 64

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if len(self.axes) != 2:
            raise ValueError("axes must have length 2")
        if self.resolution < 8:
            raise ValueError("resolution must be at least 8")

    def to_parametric(self) -> dict:
        return {
            "type": "Ellipse",
            "center": to_plain_data(self.center),
            "axes": to_plain_data(self.axes),
            "angle": to_plain_scalar(self.angle),
            "resolution": int(self.resolution),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Ellipse":
        return cls(
            center=tuple(data["center"]),
            axes=tuple(data["axes"]),
            angle=data.get("angle", 0.0),
            resolution=data.get("resolution", 64),
        )
        
@dataclass(slots=True)
class RegularPolygon(Shape):
    """
    Symbolic regular polygon.

    Parameters:
        center: (cx, cy)
        n: Number of sides.
        side_length: Length of each side.
        angle: Counter-clockwise rotation angle in degrees.
    """
    center: tuple[Any, Any]
    n: int
    side_length: Any
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if self.n < 3:
            raise ValueError("n must be at least 3")

    def to_parametric(self) -> dict:
        return {
            "type": "RegularPolygon",
            "center": to_plain_data(self.center),
            "n": int(self.n),
            "side_length": to_plain_data(self.side_length),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "RegularPolygon":
        return cls(
            center=tuple(data["center"]),
            n=data["n"],
            side_length=data["side_length"],
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class Cross(Shape):
    """
    Symbolic cross.

    Parameters:
        center: (cx, cy)
        size: Total arm length.
        width: Arm width.
        angle: Counter-clockwise rotation angle in degrees.
    """
    center: tuple[Any, Any]
    size: Any
    width: Any
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")

    def to_parametric(self) -> dict:
        return {
            "type": "Cross",
            "center": to_plain_data(self.center),
            "size": to_plain_scalar(self.size),
            "width": to_plain_scalar(self.width),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Cross":
        return cls(
            center=tuple(data["center"]),
            size=data["size"],
            width=data["width"],
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class Ring(Shape):
    """
    Symbolic elliptical ring.

    Parameters:
        center: (cx, cy)
        outer_axes: Outer semi-axes (a_out, b_out)
        inner_axes: Inner semi-axes (a_in, b_in)
        angle: Counter-clockwise rotation angle in degrees.
        resolution: Optional approximation hint for evaluators.
    """
    center: tuple[Any, Any]
    outer_axes: tuple[Any, Any]
    inner_axes: tuple[Any, Any]
    angle: Any = 0.0
    resolution: int = 64

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if len(self.outer_axes) != 2:
            raise ValueError("outer_axes must have length 2")
        if len(self.inner_axes) != 2:
            raise ValueError("inner_axes must have length 2")
        if self.resolution < 8:
            raise ValueError("resolution must be at least 8")

    def to_parametric(self) -> dict:
        return {
            "type": "Ring",
            "center": to_plain_data(self.center),
            "outer_axes": to_plain_data(self.outer_axes),
            "inner_axes": to_plain_data(self.inner_axes),
            "angle": to_plain_scalar(self.angle),
            "resolution": int(self.resolution),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Ring":
        return cls(
            center=tuple(data["center"]),
            outer_axes=tuple(data["outer_axes"]),
            inner_axes=tuple(data["inner_axes"]),
            angle=data.get("angle", 0.0),
            resolution=data.get("resolution", 64),
        )


@dataclass(slots=True)
class Moon(Shape):
    """
    Symbolic crescent / moon shape.

    Parameters:
        center: (cx, cy)
        radius: Radius of the main circle.
        cut_ratio: Controls crescent thickness.
        angle: Counter-clockwise rotation angle in degrees.
        resolution: Optional approximation hint for evaluators.
    """
    center: tuple[Any, Any]
    radius: Any
    cut_ratio: Any = 0.5
    angle: Any = 0.0
    resolution: int = 64

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if self.resolution < 8:
            raise ValueError("resolution must be at least 8")

    def to_parametric(self) -> dict:
        return {
            "type": "Moon",
            "center": to_plain_data(self.center),
            "radius": to_plain_scalar(self.radius),
            "cut_ratio": to_plain_scalar(self.cut_ratio),
            "angle": to_plain_scalar(self.angle),
            "resolution": int(self.resolution),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "Moon":
        return cls(
            center=tuple(data["center"]),
            radius=data["radius"],
            cut_ratio=data.get("cut_ratio", 0.5),
            angle=data.get("angle", 0.0),
            resolution=data.get("resolution", 64),
        )


@dataclass(slots=True)
class RoundedRectangle(Shape):
    """
    Symbolic rounded rectangle.

    Parameters:
        center: (cx, cy)
        size: (width, height)
        radius: Corner rounding radius.
        angle: Counter-clockwise rotation angle in degrees.
    """
    center: tuple[Any, Any]
    size: tuple[Any, Any]
    radius: Any
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if len(self.size) != 2:
            raise ValueError("size must have length 2")

    def to_parametric(self) -> dict:
        return {
            "type": "RoundedRectangle",
            "center": to_plain_data(self.center),
            "size": to_plain_data(self.size),
            "radius": to_plain_scalar(self.radius),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "RoundedRectangle":
        return cls(
            center=tuple(data["center"]),
            size=tuple(data["size"]),
            radius=data["radius"],
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class RoundedRegularPolygon(Shape):
    """
    Symbolic rounded regular polygon.

    Parameters:
        center: (cx, cy)
        n: Number of sides.
        side_length: Length of each side.
        radius: Corner rounding radius.
        angle: Counter-clockwise rotation angle in degrees.
    """
    center: tuple[Any, Any]
    n: int
    side_length: Any
    radius: Any
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if self.n < 3:
            raise ValueError("n must be at least 3")

    def to_parametric(self) -> dict:
        return {
            "type": "RoundedRegularPolygon",
            "center": to_plain_data(self.center),
            "n": int(self.n),
            "side_length": to_plain_scalar(self.side_length),
            "radius": to_plain_scalar(self.radius),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "RoundedRegularPolygon":
        return cls(
            center=tuple(data["center"]),
            n=data["n"],
            side_length=data["side_length"],
            radius=data["radius"],
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class RoundedCross(Shape):
    """
    Symbolic rounded cross.

    Parameters:
        center: (cx, cy)
        size: Total arm length.
        width: Arm width.
        radius: Corner rounding radius.
        angle: Counter-clockwise rotation angle in degrees.
    """
    center: tuple[Any, Any]
    size: Any
    width: Any
    radius: Any
    angle: Any = 0.0

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")

    def to_parametric(self) -> dict:
        return {
            "type": "RoundedCross",
            "center": to_plain_data(self.center),
            "size": to_plain_scalar(self.size),
            "width": to_plain_scalar(self.width),
            "radius": to_plain_scalar(self.radius),
            "angle": to_plain_scalar(self.angle),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "RoundedCross":
        return cls(
            center=tuple(data["center"]),
            size=data["size"],
            width=data["width"],
            radius=data["radius"],
            angle=data.get("angle", 0.0),
        )


@dataclass(slots=True)
class RoundedMoon(Shape):
    """
    Symbolic rounded moon shape.

    Parameters:
        center: (cx, cy)
        radius: Radius of the main circle.
        cut_ratio: Controls crescent thickness.
        rounding_radius: Corner rounding radius.
        angle: Counter-clockwise rotation angle in degrees.
        resolution: Optional approximation hint for evaluators.
    """
    center: tuple[Any, Any]
    radius: Any
    cut_ratio: Any = 0.5
    rounding_radius: Any = 0.0
    angle: Any = 0.0
    resolution: int = 64

    def __post_init__(self) -> None:
        if len(self.center) != 2:
            raise ValueError("center must have length 2")
        if self.resolution < 8:
            raise ValueError("resolution must be at least 8")

    def to_parametric(self) -> dict:
        return {
            "type": "RoundedMoon",
            "center": to_plain_data(self.center),
            "radius": to_plain_scalar(self.radius),
            "cut_ratio": to_plain_scalar(self.cut_ratio),
            "rounding_radius": to_plain_scalar(self.rounding_radius),
            "angle": to_plain_scalar(self.angle),
            "resolution": int(self.resolution),
        }
        
    @classmethod
    def from_parametric(cls, data: dict) -> "RoundedMoon":
        return cls(
            center=tuple(data["center"]),
            radius=data["radius"],
            cut_ratio=data.get("cut_ratio", 0.5),
            rounding_radius=data.get("rounding_radius", 0.0),
            angle=data.get("angle", 0.0),
            resolution=data.get("resolution", 64),
        )