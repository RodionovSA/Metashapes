# tests/shape/test_polygons.py

import math
import pytest
import torch
from metashapes.shape.primitives.polygons import RegularPolygon, Triangle
from .conftest import assert_inside, assert_outside, assert_round_trip, assert_bounds_contain, sdf_at


class TestRegularPolygon:
    # --- triangle ---------------------------------------------------------

    def test_triangle_center_inside(self):
        p = RegularPolygon(center=[0.0, 0.0], n=3, side_length=1.0)
        assert_inside(p, [(0.0, 0.0)])

    def test_triangle_far_outside(self):
        p = RegularPolygon(center=[0.0, 0.0], n=3, side_length=1.0)
        assert_outside(p, [(2.0, 0.0), (0.0, -2.0)])

    # --- square (n=4) acts as a diamond by default ------------------------

    def test_square_center_inside(self):
        p = RegularPolygon(center=[0.0, 0.0], n=4, side_length=1.0)
        assert_inside(p, [(0.0, 0.0)])

    def test_square_corner_outside(self):
        # circumradius of a square with side 1 is sqrt(2)/2 ≈ 0.707
        p = RegularPolygon(center=[0.0, 0.0], n=4, side_length=1.0)
        assert_outside(p, [(0.8, 0.8)])

    # --- hexagon ----------------------------------------------------------

    def test_hexagon_center_inside(self):
        p = RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.5)
        assert_inside(p, [(0.0, 0.0)])

    def test_hexagon_far_outside(self):
        p = RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.5)
        assert_outside(p, [(1.0, 0.0), (0.0, 1.0)])

    # --- rotation ---------------------------------------------------------

    def test_rotated(self):
        p = RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.6, angle=30.0)
        assert_inside(p, [(0.0, 0.0)])

    # --- corner radius ----------------------------------------------------

    def test_corner_radius(self):
        p = RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.6, corner_radius=0.05)
        assert_inside(p, [(0.0, 0.0)])

    def test_corner_radius_too_large(self):
        # apothem of hexagon with side 0.4: rho = 0.4 / (2*tan(π/6)) ≈ 0.346
        with pytest.raises(ValueError):
            RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.4, corner_radius=0.5)

    # --- offset center ----------------------------------------------------

    def test_offset_center(self):
        p = RegularPolygon(center=[1.0, -1.0], n=5, side_length=0.4)
        assert_inside(p, [(1.0, -1.0)])
        assert_outside(p, [(0.0, 0.0)])

    # --- validation -------------------------------------------------------

    def test_n_too_small(self):
        with pytest.raises(ValueError):
            RegularPolygon(center=[0.0, 0.0], n=2, side_length=1.0)

    def test_negative_side_length(self):
        with pytest.raises(ValueError):
            RegularPolygon(center=[0.0, 0.0], n=4, side_length=-1.0)

    # --- bounds -----------------------------------------------------------

    def test_bounds_contain_interior(self):
        p = RegularPolygon(center=[0.0, 0.0], n=5, side_length=0.6, angle=18.0)
        assert_bounds_contain(p, [(0.0, 0.0)])

    # --- serialization ----------------------------------------------------

    def test_round_trip_triangle(self):
        p = RegularPolygon(center=[0.1, 0.2], n=3, side_length=0.7, angle=15.0)
        assert_round_trip(p)

    def test_round_trip_hexagon(self):
        p = RegularPolygon(center=[0.0, 0.0], n=6, side_length=0.5, corner_radius=0.04)
        assert_round_trip(p)

    def test_round_trip_preserves_n(self):
        from metashapes.shape import Shape
        p = RegularPolygon(center=[0.0, 0.0], n=5, side_length=0.5)
        restored = Shape.from_parametric(p.to_parametric())
        assert restored.n == 5


class TestTriangle:
    def test_center_inside(self):
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=60.0, beta=60.0)
        assert_inside(t, [(0.0, 0.0)])

    def test_far_outside(self):
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=60.0, beta=60.0)
        assert_outside(t, [(5.0, 0.0), (0.0, -5.0), (-5.0, 0.0)])

    def test_base_right_vertex_boundary(self):
        # Equilateral, base=2: right base vertex B is at (1, -cy_apex/3)
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=60.0, beta=60.0)
        cy_apex = 2.0 * math.sin(math.radians(60.0)) ** 2 / math.sin(math.radians(120.0))
        Bx = 1.0 - 0.0          # base/2 - 0 (gcx=0 for equilateral)
        By = -cy_apex / 3.0
        d = sdf_at(t, Bx, By)
        assert abs(d) < 1e-4

    def test_isosceles_left_right_symmetry(self):
        # alpha == beta → triangle symmetric about y-axis, SDF(x, y) == SDF(-x, y)
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=50.0, beta=50.0)
        xs = torch.linspace(-0.5, 0.5, 10)
        ys = torch.tensor([0.0]).expand(10)
        X, Y = torch.meshgrid(xs, ys, indexing="xy")
        sdf_pos = t.sdf(X, Y)
        sdf_neg = t.sdf(-X, Y)
        assert torch.allclose(sdf_pos, sdf_neg, atol=1e-5)

    def test_right_triangle(self):
        # alpha=90, beta=45 → right triangle; center inside, far points outside
        t = Triangle(center=[0.0, 0.0], base=1.0, alpha=90.0, beta=45.0)
        assert_inside(t, [(0.0, 0.0)])
        assert_outside(t, [(3.0, 0.0), (0.0, -3.0)])

    def test_scalene_inside_outside(self):
        t = Triangle(center=[0.0, 0.0], base=1.5, alpha=40.0, beta=70.0)
        assert_inside(t, [(0.0, 0.0)])
        assert_outside(t, [(2.0, 0.0)])

    def test_offset_center(self):
        t = Triangle(center=[1.0, -1.0], base=1.0, alpha=60.0, beta=60.0)
        assert_inside(t, [(1.0, -1.0)])
        assert_outside(t, [(0.0, 0.0)])

    def test_rotation(self):
        # Rotation preserves centroid inside; same triangle rotated 90°
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=60.0, beta=60.0, angle=90.0)
        assert_inside(t, [(0.0, 0.0)])
        # A point clearly beyond the rotated apex should be outside
        assert_outside(t, [(0.0, -2.0)])

    def test_corner_radius_center_inside(self):
        t = Triangle(center=[0.0, 0.0], base=2.0, alpha=60.0, beta=60.0, corner_radius=0.1)
        assert_inside(t, [(0.0, 0.0)])

    def test_corner_radius_too_large(self):
        # inradius of equilateral with base=1: r = base / (2*sqrt(3)) ≈ 0.289
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=1.0, alpha=60.0, beta=60.0, corner_radius=0.5)

    def test_bounds_contain_centroid(self):
        t = Triangle(center=[0.5, -0.3], base=1.5, alpha=45.0, beta=70.0, angle=30.0)
        assert_bounds_contain(t, [(0.5, -0.3)])

    def test_invalid_base(self):
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=0.0, alpha=60.0, beta=60.0)
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=-1.0, alpha=60.0, beta=60.0)

    def test_invalid_angles_zero(self):
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=1.0, alpha=0.0, beta=60.0)
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=1.0, alpha=60.0, beta=0.0)

    def test_invalid_angles_sum(self):
        with pytest.raises(ValueError):
            Triangle(center=[0.0, 0.0], base=1.0, alpha=90.0, beta=90.0)

    def test_round_trip(self):
        t = Triangle(center=[0.1, -0.2], base=1.2, alpha=55.0, beta=75.0, angle=20.0)
        assert_round_trip(t)

    def test_round_trip_with_corner_radius(self):
        t = Triangle(center=[0.0, 0.0], base=1.5, alpha=60.0, beta=60.0, corner_radius=0.05)
        assert_round_trip(t)
