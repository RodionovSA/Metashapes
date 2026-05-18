# tests/shape/test_conics.py

import math
import pytest
import torch
from metashapes.shape import Shape
from metashapes.shape.primitives.conics import Ellipse
from .conftest import assert_inside, assert_outside, assert_round_trip, assert_bounds_contain, sdf_at


class TestEllipse:
    def test_center_is_inside(self):
        e = Ellipse(center=[0.0, 0.0], axes=[1.0, 0.5])
        assert_inside(e, [(0.0, 0.0)])

    def test_far_point_is_outside(self):
        e = Ellipse(center=[0.0, 0.0], axes=[1.0, 0.5])
        assert_outside(e, [(2.0, 0.0), (0.0, 2.0), (-1.5, -1.5)])

    def test_circle_boundary(self):
        # axes equal → circle; point on the boundary
        e = Ellipse(center=[0.0, 0.0], axes=[2.0, 2.0])
        d = sdf_at(e, 1.0, 0.0)
        assert abs(d) < 1e-4

    def test_circle_interior_value(self):
        e = Ellipse(center=[0.0, 0.0], axes=[2.0, 2.0])
        d = sdf_at(e, 0.0, 0.0)
        assert d == pytest.approx(-1.0, abs=5e-4)

    def test_ellipse_axis_boundary(self):
        # point at end of major axis
        e = Ellipse(center=[0.0, 0.0], axes=[2.0, 1.0])
        d = sdf_at(e, 1.0, 0.0)  # end of major semi-axis
        assert abs(d) < 1e-4

    def test_offset_center(self):
        e = Ellipse(center=[2.0, -1.0], axes=[0.6, 0.4])
        assert_inside(e, [(2.0, -1.0)])
        assert_outside(e, [(0.0, 0.0)])

    def test_rotated_ellipse(self):
        e = Ellipse(center=[0.0, 0.0], axes=[1.0, 0.4], angle=90.0)
        # after 90° rotation the long axis is now vertical
        assert_inside(e, [(0.0, 0.3)])   # inside along new long axis
        assert_outside(e, [(0.4, 0.0)]) # outside along new short axis

    def test_bounds(self):
        e = Ellipse(center=[1.0, 2.0], axes=[2.0, 1.0])
        (x0, y0), (x1, y1) = e.bounds()
        assert x0 == pytest.approx(0.0, abs=1e-5)
        assert x1 == pytest.approx(2.0, abs=1e-5)
        assert y0 == pytest.approx(1.5, abs=1e-5)
        assert y1 == pytest.approx(2.5, abs=1e-5)

    def test_bounds_contain_interior(self):
        e = Ellipse(center=[0.0, 0.0], axes=[1.2, 0.8], angle=35.0)
        assert_bounds_contain(e, [(0.0, 0.0)])

    def test_invalid_axes(self):
        with pytest.raises(ValueError):
            Ellipse(center=[0.0, 0.0], axes=[0.0, 1.0])
        with pytest.raises(ValueError):
            Ellipse(center=[0.0, 0.0], axes=[1.0, -0.5])

    def test_round_trip(self):
        e = Ellipse(center=[0.2, -0.3], axes=[0.8, 0.5], angle=25.0)
        assert_round_trip(e)

    def test_round_trip_circle(self):
        e = Ellipse(center=[0.0, 0.0], axes=[0.6, 0.6])
        assert_round_trip(e)
