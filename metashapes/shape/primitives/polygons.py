# metashapes/shape/primitives/polygons.py
# This module defines shape primitives for general polygons

from __future__ import annotations

import math
import torch
import numpy as np

from metashapes.shape.base import Shape
from metashapes.shape.registry import register_shape
from metashapes.shape.utils import _to_local_coords, register

__all__ = [
    "RegularPolygon",
    "Triangle",
]

@register_shape("RegularPolygon")
class RegularPolygon(Shape):
    """
    Symbolic regular polygon.

    Parameters:
        center: (cx, cy)
        n: Number of sides.
        side_length: Length of each side.
        angle: Counter-clockwise rotation angle in degrees.
        corner_radius: rounding radius for corners.
    """
    def __init__(self,
                 center: torch.Tensor,
                 n: int,
                 side_length: torch.Tensor,
                 angle: torch.Tensor = 0.0,
                 corner_radius: torch.Tensor = 0.0):
        super().__init__()
        if n < 3:
            raise ValueError("n must be at least 3")
        self.n = n
        register(self, "center", center)
        register(self, "side_length", side_length)
        register(self, "angle", angle)
        register(self, "corner_radius", corner_radius)

        if torch.any(self.side_length <= 0):
            raise ValueError("side_length must be positive")
        if torch.any(self.corner_radius < 0):
            raise ValueError("corner_radius must be non-negative")

        an = torch.tensor(np.pi / n)
        rho = self.side_length / (2.0 * torch.tan(an))
        if torch.any(self.corner_radius >= rho):
            raise ValueError("corner_radius is too large")

    def sdf(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        cx, cy = self.center[0], self.center[1]
        s  = self.side_length
        rr = self.corner_radius
        n  = self.n

        pi = torch.as_tensor(np.pi, dtype=x.dtype, device=x.device)
        angle = self.angle

        # original polygon radii
        n_t = torch.as_tensor(float(n), dtype=x.dtype, device=x.device)
        an = pi / n_t
        R = s / (2.0 * torch.sin(an))     # circumradius
        rho = R * torch.cos(an)           # apothem

        # inset polygon: preserve outer support lines after rounding
        rho_in = rho - rr
        R_in = rho_in / torch.cos(an)

        # local coords
        x_local, y_local = _to_local_coords(x, y, cx, cy, angle)

        # inset polygon vertices, same convention as shapely
        phi0 = pi / 2.0
        verts = []
        for k in range(n):
            th = 2.0 * pi * k / n_t + phi0
            vx = R_in * torch.cos(th)
            vy = R_in * torch.sin(th)
            verts.append((vx, vy))

        min_d2 = None
        inside = torch.ones_like(x_local, dtype=torch.bool)

        for k in range(n):
            ax, ay = verts[k]
            bx, by = verts[(k + 1) % n]

            ex = bx - ax
            ey = by - ay
            wx = x_local - ax
            wy = y_local - ay

            ee = ex * ex + ey * ey
            t = torch.clamp((wx * ex + wy * ey) / ee, 0.0, 1.0)

            px = ax + t * ex
            py = ay + t * ey

            d2 = (x_local - px) ** 2 + (y_local - py) ** 2
            min_d2 = d2 if min_d2 is None else torch.minimum(min_d2, d2)

            cross = ex * (y_local - ay) - ey * (x_local - ax)
            inside = inside & (cross >= 0)

        d_in = torch.sqrt(torch.clamp(min_d2, min=0.0))
        d_in = torch.where(inside, -d_in, d_in)

        return d_in - rr

    def bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        cx, cy = self.center.detach().tolist()
        s = self.side_length.detach().item()
        angle = self.angle.detach().item()
        n = self.n

        an = np.pi / n
        R = s / (2.0 * np.sin(an))
        phi0 = np.pi / 2.0 + np.radians(angle)
        angles = [2.0 * np.pi * k / n + phi0 for k in range(n)]
        xs = [cx + R * np.cos(a) for a in angles]
        ys = [cy + R * np.sin(a) for a in angles]
        return (float(min(xs)), float(min(ys))), (float(max(xs)), float(max(ys)))

    def to_parametric(self) -> dict:
        d = super().to_parametric()
        d["n"] = self.n
        return d

    @property
    def min_feature_size(self) -> float:
        pi = np.pi
        R = self.side_length.detach().item() / (2.0 * np.sin(pi / self.n))
        a = R * np.cos(pi / self.n)

        if self.n % 2 == 0:
            return 2.0 * a

        return a * (1.0 + np.cos(pi / self.n))


@register_shape("Triangle")
class Triangle(Shape):
    """
    General triangle defined by two base angles and the base length (ASA).

    Parameters:
        center: (cx, cy) — centroid of the triangle
        base: length of the bottom side (between alpha and beta vertices)
        alpha: interior angle at the left base vertex in degrees
        beta: interior angle at the right base vertex in degrees
        angle: counter-clockwise rotation in degrees
        corner_radius: optional corner smoothing; must be < inradius
    """
    def __init__(self,
                 center: torch.Tensor,
                 base: torch.Tensor,
                 alpha: torch.Tensor,
                 beta: torch.Tensor,
                 angle: torch.Tensor = 0.0,
                 corner_radius: torch.Tensor = 0.0):
        super().__init__()
        register(self, "center", center)
        register(self, "base", base)
        register(self, "alpha", alpha)
        register(self, "beta", beta)
        register(self, "angle", angle)
        register(self, "corner_radius", corner_radius)

        if self.base <= 0:
            raise ValueError("Triangle base must be positive")
        if self.alpha <= 0 or self.beta <= 0:
            raise ValueError("Triangle angles must be positive")
        if self.alpha + self.beta >= 180.0:
            raise ValueError("Triangle alpha + beta must be less than 180°")
        if self.corner_radius < 0:
            raise ValueError("corner_radius must be non-negative")
        if self.corner_radius > 0 and self.corner_radius >= self._inradius():
            raise ValueError("corner_radius must be less than the triangle inradius")

    def _inradius(self) -> torch.Tensor:
        a_rad = torch.deg2rad(self.alpha)
        b_rad = torch.deg2rad(self.beta)
        sin_ab = torch.sin(a_rad + b_rad)
        return self.base * torch.sin(a_rad) * torch.sin(b_rad) / (
            sin_ab + torch.sin(a_rad) + torch.sin(b_rad)
        )

    def _vertices(self):
        """(A, B, C) as (x, y) tensor pairs, CCW, centroid at origin."""
        a_rad = torch.deg2rad(self.alpha)
        b_rad = torch.deg2rad(self.beta)
        sin_ab = torch.sin(a_rad + b_rad)

        # Apex in base-midpoint frame: base goes from -base/2 to +base/2
        cx_apex = self.base * 0.5 - self.base * torch.sin(a_rad) * torch.cos(b_rad) / sin_ab
        cy_apex = self.base * torch.sin(a_rad) * torch.sin(b_rad) / sin_ab

        # Centroid offset: (cx_apex/3, cy_apex/3)
        gcx = cx_apex / 3.0
        gcy = cy_apex / 3.0

        Ax = -self.base * 0.5 - gcx
        Ay = -gcy
        Bx =  self.base * 0.5 - gcx
        By = -gcy
        Cx = cx_apex - gcx
        Cy = cy_apex - gcy
        return (Ax, Ay), (Bx, By), (Cx, Cy)

    def sdf(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        cx, cy = self.center[0], self.center[1]
        rr = self.corner_radius

        x_local, y_local = _to_local_coords(x, y, cx, cy, self.angle)

        (Ax, Ay), (Bx, By), (Cx, Cy) = self._vertices()

        if rr > 0:
            alpha = self.alpha
            beta = self.beta
            gamma = torch.as_tensor(180.0, dtype=alpha.dtype, device=alpha.device) - alpha - beta

            def _inset(Vx, Vy, Nx, Ny, Px, Py, theta_deg):
                dnx, dny = Nx - Vx, Ny - Vy
                dpx, dpy = Px - Vx, Py - Vy
                dn_len = torch.sqrt(dnx * dnx + dny * dny).clamp(min=1e-8)
                dp_len = torch.sqrt(dpx * dpx + dpy * dpy).clamp(min=1e-8)
                dnx, dny = dnx / dn_len, dny / dn_len
                dpx, dpy = dpx / dp_len, dpy / dp_len
                sin_t = torch.sin(torch.deg2rad(theta_deg)).clamp(min=1e-8)
                return Vx + rr / sin_t * (dnx + dpx), Vy + rr / sin_t * (dny + dpy)

            # Inset all three vertices using original (un-inset) positions
            oAx, oAy, oBx, oBy, oCx, oCy = Ax, Ay, Bx, By, Cx, Cy
            Ax, Ay = _inset(oAx, oAy, oBx, oBy, oCx, oCy, alpha)
            Bx, By = _inset(oBx, oBy, oCx, oCy, oAx, oAy, beta)
            Cx, Cy = _inset(oCx, oCy, oAx, oAy, oBx, oBy, gamma)

        verts = [(Ax, Ay), (Bx, By), (Cx, Cy)]
        min_d2 = None
        inside = torch.ones_like(x_local, dtype=torch.bool)

        for k in range(3):
            vax, vay = verts[k]
            vbx, vby = verts[(k + 1) % 3]

            ex = vbx - vax
            ey = vby - vay
            wx = x_local - vax
            wy = y_local - vay

            ee = ex * ex + ey * ey
            t = torch.clamp((wx * ex + wy * ey) / ee, 0.0, 1.0)

            cpx = vax + t * ex
            cpy = vay + t * ey

            d2 = (x_local - cpx) ** 2 + (y_local - cpy) ** 2
            min_d2 = d2 if min_d2 is None else torch.minimum(min_d2, d2)

            cross = ex * (y_local - vay) - ey * (x_local - vax)
            inside = inside & (cross >= 0)

        d_in = torch.sqrt(torch.clamp(min_d2, min=0.0))
        d_in = torch.where(inside, -d_in, d_in)
        return d_in - rr

    def bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        cx, cy = self.center.detach().tolist()
        theta = math.radians(self.angle.detach().item())
        c_t, s_t = math.cos(theta), math.sin(theta)

        (Ax, Ay), (Bx, By), (Cx, Cy) = self._vertices()
        local_pts = [
            (Ax.item(), Ay.item()),
            (Bx.item(), By.item()),
            (Cx.item(), Cy.item()),
        ]

        xs = [cx + p[0] * c_t - p[1] * s_t for p in local_pts]
        ys = [cy + p[0] * s_t + p[1] * c_t for p in local_pts]
        return (min(xs), min(ys)), (max(xs), max(ys))

    @property
    def min_feature_size(self) -> float:
        return 2.0 * self._inradius().item()
