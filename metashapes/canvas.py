#metashapes/canvas.py
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Tuple, Literal
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .shape import Shape  # type-only
    
from .library import rectangle

@dataclass
class Canvas:
    """
    Defines unit cell size and grid size, and do resterization. 
    """
    # world window and raster size
    x0: float; y0: float; Lx: float; Ly: float  # lower-left (x0,y0), width/height
    H: int; W: int;                               # rows, cols
    spacing: float = 0.0                     # optional spacing from edges (in world units)

    def __post_init__(self):
        self.sx, self.sy = self.W / self.Lx, self.H / self.Ly
        self.spacing = abs(self.spacing)  # ensure non-negative

        # Check spacing validity
        if self.spacing > self.Lx/2 or self.spacing > self.Ly/2:
            raise ValueError("Spacing is too large for the given canvas size.")

    def world_to_rc(self, x: np.ndarray, y: np.ndarray) -> Tuple[int, int]:
        cols = (x - self.x0) * self.sx
        rows = (self.y0 + self.Ly - y) * self.sy  # y-up world -> y-down image
        return rows, cols
    
    @property
    def dx(self) -> float:
        """Pixel size along X (same units as Lx)."""
        return self.Lx / self.W

    @property
    def dy(self) -> float:
        """Pixel size along Y (same units as Ly)."""
        return self.Ly / self.H
    
    @property
    def unit_cell(self) -> 'Shape':
        """
        Return a Rectangle of the unit cell (with spacing).
        """
        return rectangle(
            center=(self.x0 + 0.5 * self.Lx, self.y0 + 0.5 * self.Ly),
            size=(self.Lx - 2 * self.spacing, self.Ly - 2 * self.spacing),
            angle=0.0
        )

    def set_grid(self, H: int, W: int) -> None:
        """
        Update H/W (keeping physical Lx/Ly). 
        """
        self.H = int(H)
        self.W = int(W)
        self.__post_init__()  # refresh sx, sy

    def set_pixel_size(
        self,
        pixel_size: float,
        rounding: Literal["round","floor","ceil"] = "round"
    ) -> None:
        """
        Choose H,W from a target *isotropic* pixel size (≈ pixel_size in both axes).
        """
        f = {"round": np.round, "floor": np.floor, "ceil": np.ceil}[rounding]
        H = int(f(self.Ly / pixel_size))
        W = int(f(self.Lx / pixel_size))
        H = max(H, 1); W = max(W, 1)
        self.set_grid(H=H, W=W)

    @contextmanager
    def temporary_pixel_size(
        self,
        pixel_size: float,
        rounding: Literal["round","floor","ceil"] = "round"
    ):
        """
        Temporarily switch resolution, then restore H/W automatically.
        Usage:
            with canvas.temporary_pixel_size(0.01):
                # do high-res stuff
                ...
            # back to original H/W here
        """
        _H, _W = self.H, self.W
        try:
            self.set_pixel_size(pixel_size, rounding=rounding)
            yield self
        finally:
            self.set_grid(H=_H, W=_W)
            
    