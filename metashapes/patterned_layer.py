# metashapes/patterned_layer.py
# Definition of PatternedLayer, representing one patterned layer on a canvas with a symbolic shape and thickness.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canvas import Canvas
from .shape.base import Shape
from .shape.primitives import Rectangle


@dataclass(frozen=True, slots=True)
class PatternedLayer:
    """
    One 2D patterned layer on a canvas, homogeneous along z with given thickness.

    - `shape` defines the symbolic pattern
    - `canvas` defines the unit-cell region in x-y
    - `inverted=False`: shape = material region
    - `inverted=True`:  shape = void region inside the unit cell
    """
    shape: Shape
    canvas: Canvas
    thickness: Any
    inverted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.shape, Shape):
            raise TypeError("shape must be a Shape")
        if not isinstance(self.canvas, Canvas):
            raise TypeError("canvas must be a Canvas")

    @property
    def unit_cell_shape(self) -> Shape:
        """
        Rectangle corresponding to the usable inner canvas region
        (canvas area excluding spacing).
        """
        x0, y0, x1, y1 = self.canvas.inner_bounds
        return Rectangle(
            center=((x0 + x1) / 2, (y0 + y1) / 2),
            size=(x1 - x0, y1 - y0),
        )

    @property
    def filled_region(self) -> Shape:
        """
        Symbolic material region inside the unit cell.
        """
        cell = self.unit_cell_shape
        if self.inverted:
            return cell - self.shape
        return cell & self.shape

    @property
    def void_region(self) -> Shape:
        """
        Symbolic complementary empty region inside the unit cell.
        """
        cell = self.unit_cell_shape
        if self.inverted:
            return cell & self.shape
        return cell - self.shape

    def with_shape(self, shape: Shape) -> PatternedLayer:
        """
        Return a new PatternedLayer with the same canvas, thickness, and inversion,
        but a different pattern shape.
        """
        return PatternedLayer(
            shape=shape,
            canvas=self.canvas,
            thickness=self.thickness,
            inverted=self.inverted,
        )

    def with_canvas(self, canvas: Canvas) -> PatternedLayer:
        """
        Return a new PatternedLayer with the same shape, thickness, and inversion,
        but a different canvas.
        """
        return PatternedLayer(
            shape=self.shape,
            canvas=canvas,
            thickness=self.thickness,
            inverted=self.inverted,
        )

    def with_thickness(self, thickness: float) -> PatternedLayer:
        """
        Return a new PatternedLayer with the same shape, canvas, and inversion,
        but a different layer thickness.
        """
        return PatternedLayer(
            shape=self.shape,
            canvas=self.canvas,
            thickness=thickness,
            inverted=self.inverted,
        )

    def invert(self) -> PatternedLayer:
        """
        Return a new PatternedLayer with inverted material/void interpretation.
        """
        return PatternedLayer(
            shape=self.shape,
            canvas=self.canvas,
            thickness=self.thickness,
            inverted=not self.inverted,
        )

    def to_parametric(self) -> dict:
        """
        Serialize the PatternedLayer into a dictionary of defining parameters.
        """
        return {
            "shape": self.shape.to_parametric(),
            "canvas": self.canvas.to_parametric(),
            "thickness": self.thickness,
            "inverted": self.inverted,
        }

    @classmethod
    def from_parametric(cls, data: dict) -> PatternedLayer:
        """
        Reconstruct a PatternedLayer from a dictionary created by `to_parametric`.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        try:
            shape_data = data["shape"]
            canvas_data = data["canvas"]
            thickness = data["thickness"]
            inverted = data["inverted"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e.args[0]}") from e

        shape = Shape.from_parametric(shape_data)
        canvas = Canvas.from_parametric(canvas_data)

        return cls(
            shape=shape,
            canvas=canvas,
            thickness=float(thickness),
            inverted=bool(inverted),
        )