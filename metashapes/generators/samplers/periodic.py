# metashapes/generators/samplers/periodic.py
# Samplers for periodic primitive shapes.

from __future__ import annotations

from metashapes.canvas import Canvas
from metashapes.generators.registry import register_shape_sampler
from metashapes.generators.samplers.base import ShapeSampler
from metashapes.generators.samplers.utils import (
    get_fixed_param,
    get_param_range,
    intersect_ranges,
    resolve_param,
)
from metashapes.shape.primitives import Stripe


@register_shape_sampler("Stripe")
class StripeSampler(ShapeSampler):
    """
    Sampler for Stripe shapes.

    Configurable via ``fixed_shape_params["Stripe"]`` and
    ``shape_param_ranges["Stripe"]``:

    ============  ============================================================
    Key           Meaning
    ============  ============================================================
    ``axis``      ``'x'`` or ``'y'``; if absent, chosen randomly with equal
                  probability
    ``width``     Full stripe thickness; default range
                  ``[max(min_shape_size, min_feature_size), perp_len]`` where
                  *perp_len* is the canvas length in the perpendicular direction
    ``offset``    Centre position along the perpendicular axis; default range
                  derived from *width* so the stripe stays within the canvas
    ============  ============================================================
    """

    shape_name = "Stripe"

    def sample(self, rng, canvas: Canvas, config) -> Stripe:
        shape_name = self.shape_name

        min_size = config.min_shape_size or 0.1
        min_feature = config.min_feature_size or 0.0

        fixed_axis = get_fixed_param(config, shape_name, "axis")
        fixed_width = get_fixed_param(config, shape_name, "width")
        fixed_offset = get_fixed_param(config, shape_name, "offset")

        width_range = get_param_range(config, shape_name, "width")
        offset_range = get_param_range(config, shape_name, "offset")

        # --- axis ---
        axis = fixed_axis if fixed_axis is not None else rng.choice(["x", "y"])

        # Perpendicular inner bounds (the axis the stripe is bounded in)
        x0, y0, x1, y1 = canvas.inner_bounds
        perp_lo, perp_hi = (y0, y1) if axis == "x" else (x0, x1)
        perp_len = perp_hi - perp_lo

        # --- width ---
        width = resolve_param(
            rng,
            fixed_value=fixed_width,
            user_range=width_range,
            default_range=intersect_ranges(
                (min_size, perp_len),
                (min_feature, perp_len),
            ),
        )

        # --- offset ---
        # The stripe spans [offset - width/2, offset + width/2] in the
        # perpendicular direction.  Keep it fully inside the inner bounds.
        offset = resolve_param(
            rng,
            fixed_value=fixed_offset,
            user_range=offset_range,
            default_range=(perp_lo + width / 2.0, perp_hi - width / 2.0),
        )

        return Stripe(offset=offset, width=width, axis=axis)
