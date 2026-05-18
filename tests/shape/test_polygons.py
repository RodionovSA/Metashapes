# tests/shape/test_polygons.py

import math
import pytest
import torch
from metashapes.shape.primitives.polygons import RegularPolygon
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
