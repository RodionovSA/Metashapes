# metashapes/generators/samplers/quads.py
# This module defines samplers for quadrilateral shapes

from __future__ import annotations

import numpy as np

from metashapes.canvas import Canvas
from metashapes.generators.samplers.base import ShapeSampler
from metashapes.generators.samplers.utils import get_fixed_param, sample_param
from metashapes.generators.registry import register_shape_sampler
from metashapes.shape.primitives import Rectangle
from metashapes.generators.samplers.utils import (
    get_fixed_param,
    get_param_range,
    intersect_ranges,
    resolve_param,
    resolve_pair_param,
    sample_center_in_bounds,
)

@register_shape_sampler("Rectangle")
class RectangleSampler(ShapeSampler):
    shape_name = "Rectangle"

    def sample(self, rng, canvas: Canvas, config) -> Rectangle:
        shape_name = self.shape_name

        min_size = config.min_shape_size or 0.1
        min_feature = config.min_feature_size or 0.0

        fixed_size = get_fixed_param(config, shape_name, "size")
        fixed_angle = get_fixed_param(config, shape_name, "angle")
        fixed_center = get_fixed_param(config, shape_name, "center")
        fixed_corner_radius = get_fixed_param(config, shape_name, "corner_radius")

        size_range = get_param_range(config, shape_name, "size")
        angle_range = get_param_range(config, shape_name, "angle")
        center_range = get_param_range(config, shape_name, "center")
        corner_radius_range = get_param_range(config, shape_name, "corner_radius")

        x0, y0, x1, y1 = canvas.inner_bounds
        iw, ih = x1 - x0, y1 - y0  # inner width / height

        for _ in range(config.max_tries_per_shape):
            width, height = resolve_pair_param(
                rng,
                fixed_value=fixed_size,
                user_range=size_range,
                default_x_range=intersect_ranges(
                    (min_size, iw),
                    (min_feature, iw),
                ),
                default_y_range=intersect_ranges(
                    (min_size, ih),
                    (min_feature, ih),
                ),
            )

            angle = resolve_param(
                rng,
                fixed_value=fixed_angle,
                user_range=angle_range,
                default_range=(0.0, 360.0),
            )

            corner_radius = resolve_param(
                rng,
                fixed_value=fixed_corner_radius,
                user_range=corner_radius_range,
                default_range=(0.0, min(width, height) / 2.0),
            )

            hx = width / 2.0
            hy = height / 2.0
            theta = np.deg2rad(angle)

            dx = abs(hx * np.cos(theta)) + abs(hy * np.sin(theta))
            dy = abs(hx * np.sin(theta)) + abs(hy * np.cos(theta))

            if dx > iw / 2 or dy > ih / 2:
                continue

            cx, cy = sample_center_in_bounds(
                rng,
                fixed_center=fixed_center,
                center_range=center_range,
                x_bounds=(x0 + dx, x1 - dx),
                y_bounds=(y0 + dy, y1 - dy),
            )

            return Rectangle(
                center=(cx, cy),
                size=(width, height),
                angle=angle,
                corner_radius=corner_radius,
            )

        raise RuntimeError("rectangle_too_large_for_canvas")