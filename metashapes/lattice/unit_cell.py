# metashapes/lattice/unit_cell.py
# 

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import math

from metashapes.shape import Shape
from .basis import Lattice
from .grid import cartesian_grid

__all__ = ["UnitCell"]

class UnitCell(nn.Module):
    """
    A periodic structure: one Lattice + one Shape (the scene).

    The lattice owns the in-plane periodicity; the shape lives in
    infinite, continuous space and knows nothing about the cell. The
    UnitCell turns the shape's SDF into a *periodic* SDF by taking the
    minimum over lattice copies, and samples it on a one-cell grid.

    The cell is only a sampling viewport: shapes are never clipped to
    it, so shapes touching or crossing the boundary stay continuous.

    Parameters
    ----------
    lattice : Lattice
        Fixed in-plane periodicity.
    scene : Shape
        The shape (usually a Union of primitives) to make periodic.
    """

    def __init__(self, lattice: Lattice, scene: Shape):
        super().__init__()
        self.lattice = lattice          # frozen dataclass, not a submodule
        self.scene = scene              # nn.Module -> auto-registered

    # --- ring sizing -------------------------------------------------
    def _ring_for(self, shape: Shape) -> tuple[int, int]:
        """Number of periodic copies to search per lattice direction.

        A finite shape spanning k cells needs ceil(k)+1 copies so that
        a query point can always reach its nearest copy. An infinite
        extent collapses to ring 1: every copy along that direction is
        identical, so one is enough.
        """
        (x0, y0), (x1, y1) = shape.bounds()

        # the four bbox corners, mapped to fractional lattice coords
        corners_x = torch.tensor([x0, x0, x1, x1], dtype=self.lattice.dtype, device=self.lattice.device)
        corners_y = torch.tensor([y0, y1, y0, y1], dtype=self.lattice.dtype, device=self.lattice.device)
        f1, f2 = self.lattice.to_fractional(corners_x, corners_y)

        rings = []
        for frac in (f1, f2):
            vals = frac[torch.isfinite(frac)]
            if vals.numel() < 2:
                # infinite extent in this direction -> identical copies
                rings.append(1)
            else:
                ext = (vals.max() - vals.min()).item()
                rings.append(int(math.ceil(ext)) + 1)
        return rings[0], rings[1]

    # --- periodic SDF ------------------------------------------------
    def sdf(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Periodic signed distance of the scene at Cartesian (x, y).

        Minimum over lattice copies. The ring is sized from the scene's
        bounding box, so shapes larger than one cell are still connected
        correctly and infinite shapes continue across the seam.
        """
        r1, r2 = self._ring_for(self.scene)
        best = None
        for i in range(-r1, r1 + 1):
            for j in range(-r2, r2 + 1):
                ox, oy = self.lattice.offset(i, j)
                d = self.scene.sdf(x - ox, y - oy)
                best = d if best is None else torch.minimum(best, d)
        return best

    # --- rasterization ----------------------------------------------
    def rasterize(self, nx: int, ny: int, *,
                  repeat: tuple[int, int] = (1, 1),
                  cartesian: bool = False):
        """Periodic SDF sampled over a supercell.

        repeat=(n1, n2) — tile n1 cells along a1 and n2 along a2.

        cartesian=False (default) — samples on the fractional parallelogram
            grid; output shape [ny·n2, nx·n1]. Rows run along a2, so for
            oblique lattices the image appears sheared when displayed with
            imshow.

        cartesian=True — samples on an axis-aligned Cartesian bounding box
            of the supercell; output shape [ny·n2, nx·n1]. Rows are
            horizontal in world space — correct for imshow display of any
            lattice geometry, including hexagonal.
            Query points are folded back into the unit cell via fractional
            modulo before SDF evaluation, so the ring search stays valid
            regardless of repeat size.
        """
        n1, n2 = repeat

        if not cartesian:
            X, Y = cartesian_grid(self.lattice, nx, ny,
                                  dtype=self.lattice.dtype, device=self.lattice.device)
            d = self.sdf(X, Y)
            return d if (n1 == 1 and n2 == 1) else d.tile(n2, n1)

        # Cartesian bounding box of the n1×n2 supercell
        fc = torch.tensor(
            [[0.0, 0.0], [float(n1), 0.0], [0.0, float(n2)], [float(n1), float(n2)]],
            dtype=self.lattice.dtype, device=self.lattice.device,
        )
        cx, cy = self.lattice.to_cartesian(fc[:, 0], fc[:, 1])
        xmin, xmax = cx.min(), cx.max()
        ymin, ymax = cy.min(), cy.max()

        xs = torch.linspace(xmin.item(), xmax.item(), nx * n1,
                            dtype=self.lattice.dtype, device=self.lattice.device)
        ys = torch.linspace(ymin.item(), ymax.item(), ny * n2,
                            dtype=self.lattice.dtype, device=self.lattice.device)
        X, Y = torch.meshgrid(xs, ys, indexing="xy")

        # Fold to unit cell: points stay in [0,1) fractional → ring search valid
        f1, f2 = self.lattice.to_fractional(X, Y)
        Xw, Yw = self.lattice.to_cartesian(f1 % 1.0, f2 % 1.0)
        return self.sdf(Xw, Yw)

    def mask(self, nx, ny, *, soft=False, softness=None,
             repeat: tuple[int, int] = (1, 1),
             cartesian: bool = False):
        """Rasterize the periodic structure into a mask. Shape [ny·n2, nx·n1].

        soft=False      -> hard binary mask (non-differentiable, for inference).
        soft=True       -> differentiable sigmoid mask; `softness` is the edge
                           scale in world units, defaulting to one pixel.
        repeat=(n1, n2) -> tile n1 cells along a1 and n2 cells along a2.
        cartesian=True  -> sample on an axis-aligned Cartesian grid so the
                           result displays correctly with imshow for any
                           lattice geometry (see rasterize for details).
        """
        d = self.rasterize(nx, ny, repeat=repeat, cartesian=cartesian)

        if not soft:
            return (d <= 0).to(d.dtype)

        if softness is None:
            if cartesian:
                n1, n2 = repeat
                fc = torch.tensor(
                    [[0.0, 0.0], [float(n1), 0.0], [0.0, float(n2)], [float(n1), float(n2)]],
                    dtype=self.lattice.dtype, device=self.lattice.device,
                )
                cx, cy = self.lattice.to_cartesian(fc[:, 0], fc[:, 1])
                softness = min(
                    ((cx.max() - cx.min()) / (nx * n1)).item(),
                    ((cy.max() - cy.min()) / (ny * n2)).item(),
                )
            else:
                dx = (self.lattice.a1.norm() / nx).item()
                dy = (self.lattice.a2.norm() / ny).item()
                softness = min(dx, dy)

        softness = torch.as_tensor(softness, dtype=d.dtype, device=d.device)
        return torch.sigmoid(-d / softness)

    # --- boundary continuity check -----------------------------------
    def boundary_points(self, *, resolution: int = 512) -> np.ndarray:
        """
        Return world-coordinate points on the material boundary (zero-level-set).

        Evaluates the *periodic* SDF on a ``resolution × resolution`` grid over
        one unit cell, detects sign changes between adjacent samples — including
        across the cell seam, since opposite edges are identified under
        periodicity — and linearly interpolates each crossing to sub-pixel
        accuracy.

        Non-differentiable: intended for visualization, export, and Shapely
        interop, not for use inside a loss.

        Parameters
        ----------
        resolution : int
            Grid resolution per dimension (default 512). Must be fine enough
            to resolve the smallest feature; thinner features may be missed.

        Returns
        -------
        np.ndarray, shape (M, 2)
            ``(x, y)`` world coordinates on the boundary. Empty ``(0, 2)`` if
            the cell is uniform (no zero-crossing).
        """
        n = resolution

        # --- sample the periodic SDF on one cell -------------------------
        # fractional grid, endpoint-excluded so the seam is not duplicated
        f = torch.arange(n, dtype=torch.float32) / n
        F1, F2 = torch.meshgrid(f, f, indexing="xy")          # [n, n]
        X, Y = self.lattice.to_cartesian(F1, F2)
        with torch.no_grad():
            D = self.sdf(X, Y)                                # periodic SDF, [n, n]

        D = D.detach().cpu().numpy()
        X = X.detach().cpu().numpy()
        Y = Y.detach().cpu().numpy()

        # uniform cell -> no boundary
        if np.all(D > 0) or np.all(D < 0):
            return np.empty((0, 2), dtype=np.float64)

        eps = 1e-12
        pts = []

        def _crossings(d0, d1, x0, y0, x1, y1):
            """Sub-pixel boundary points where d0 and d1 straddle zero.

            d* are SDF arrays, (x*, y*) the corresponding world coords of
            the two endpoints. Returns a list of (x, y).
            """
            # a sign change: one side <= 0, the other > 0 (treat exact 0 as inside)
            sign_change = (d0 <= 0) != (d1 <= 0)
            if not np.any(sign_change):
                return []
            i = np.where(sign_change)
            a = d0[i]
            b = d1[i]
            denom = a - b
            # linear interp; guard the degenerate equal-value case
            t = np.where(np.abs(denom) > eps, a / denom, 0.5)
            px = x0[i] + t * (x1[i] - x0[i])
            py = y0[i] + t * (y1[i] - y0[i])
            return list(zip(px, py))

        # --- interior crossings, horizontal neighbours (column j -> j+1) -
        pts += _crossings(D[:, :-1], D[:, 1:],
                        X[:, :-1], Y[:, :-1],
                        X[:, 1:],  Y[:, 1:])

        # --- interior crossings, vertical neighbours (row i -> i+1) ------
        pts += _crossings(D[:-1, :], D[1:, :],
                        X[:-1, :], Y[:-1, :],
                        X[1:, :],  Y[1:, :])

        # --- seam crossings: last column <-> first column ----------------
        # opposite edges are identified under periodicity, so the first
        # column's true world position for interpolation is shifted by a1.
        a1 = self.lattice.a1.detach().cpu().numpy()
        pts += _crossings(D[:, -1], D[:, 0],
                        X[:, -1],        Y[:, -1],
                        X[:, 0] + a1[0], Y[:, 0] + a1[1])

        # --- seam crossings: last row <-> first row ----------------------
        a2 = self.lattice.a2.detach().cpu().numpy()
        pts += _crossings(D[-1, :], D[0, :],
                        X[-1, :],        Y[-1, :],
                        X[0, :] + a2[0], Y[0, :] + a2[1])

        if not pts:
            return np.empty((0, 2), dtype=np.float64)
        return np.asarray(pts, dtype=np.float64)

    # --- serialization -----------------------------------------------
    def to_parametric(self) -> dict:
        return {
            "type": "UnitCell",
            "lattice": {
                "a1": self.lattice.a1.detach().cpu().tolist(),
                "a2": self.lattice.a2.detach().cpu().tolist(),
            },
            "scene": self.scene.to_parametric(),
        }

    @classmethod
    def from_parametric(cls, data: dict) -> "UnitCell":
        lat = data["lattice"]
        lattice = Lattice(
            a1=torch.tensor(lat["a1"]),
            a2=torch.tensor(lat["a2"]),
        )
        scene = Shape.from_parametric(data["scene"])
        return cls(lattice=lattice, scene=scene)
