# metashapes/shape/primitives/periodic.py
# Shapes that span the full unit cell in one periodic direction.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar
import torch

from metashapes.shape.base import Shape, to_plain_scalar
from metashapes.shape.registry import register_shape

__all__ = [
    "Stripe",
]


@register_shape("Stripe")
@dataclass(slots=True)
class Stripe(Shape):
    """
    An infinite stripe spanning the full unit cell along one axis.

    The stripe is unbounded along `axis` and has a finite thickness
    (`width`) in the perpendicular direction, centred at `offset`.

    Parameters:
        offset: position of the stripe centre along the *perpendicular* axis
        width:  full thickness of the stripe (must be positive)
        axis:   ``'x'`` — stripe runs along x, bounded in y  (default)
                ``'y'`` — stripe runs along y, bounded in x

    Example::

        # Horizontal stripe of width 0.3 centred on y = 0
        s = Stripe(offset=0.0, width=0.3, axis='x')

        # Vertical stripe of width 0.2 shifted to x = 0.1
        s = Stripe(offset=0.1, width=0.2, axis='y')

    Notes:
        ``allowed_self_periodic_shifts`` is set automatically so the
        generator and ``UnitCell`` know this shape spans the cell boundary
        and must not be clipped or gap-checked in the periodic direction.
    """

    offset: Any
    width: Any
    axis: str = 'x'

    _scalar_fields: ClassVar[tuple[str, ...]] = Shape._scalar_fields + ('offset', 'width')

    def __post_init__(self) -> None:
        if self.axis not in ('x', 'y'):
            raise ValueError("axis must be 'x' or 'y'")

    def sdf(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        w = torch.as_tensor(self.width, dtype=x.dtype, device=x.device)
        off = torch.as_tensor(self.offset, dtype=x.dtype, device=x.device)

        if torch.any(w <= 0):
            raise ValueError("Stripe width must be positive")

        # SDF of a 1-D band along the perpendicular coordinate t:
        #   d = |t - offset| - width/2
        t = y if self.axis == 'x' else x
        return torch.abs(t - off) - 0.5 * w

    @property
    def min_feature_size(self) -> float:
        return to_plain_scalar(self.width)

    @property
    def allowed_self_periodic_shifts(self) -> set[tuple[int, int]]:
        """
        The stripe reaches both boundaries of the unit cell along its axis,
        so its periodic images are allowed to be in contact with it.
        """
        if self.axis == 'x':
            return {(-1, 0), (1, 0)}   # periodic in x
        return {(0, -1), (0, 1)}        # periodic in y
