# metashapes/utils.py
# Package-wide utility functions.

from __future__ import annotations

__all__ = ["periodic_shift_skipped"]


def periodic_shift_skipped(ix: int, iy: int, allowed: set[tuple[int, int]]) -> bool:
    """
    Return True if the periodic shift ``(ix, iy)`` should be excluded from
    gap checking for a shape with the given ``allowed_self_periodic_shifts``.

    A shape that is periodic along an axis reaches the cell boundary in that
    direction, so **every** shift involving that axis is skipped — including
    diagonals — to avoid false gap violations from boundary contacts.

    Examples
    --------
    >>> periodic_shift_skipped(1, 0, {(-1, 0), (1, 0)})   # x-periodic, x-shift
    True
    >>> periodic_shift_skipped(1, 1, {(-1, 0), (1, 0)})   # x-periodic, diagonal
    True
    >>> periodic_shift_skipped(0, 1, {(-1, 0), (1, 0)})   # x-periodic, y-shift
    False
    >>> periodic_shift_skipped(0, 1, set())                # non-periodic
    False
    """
    if (ix, iy) in allowed:
        return True
    periodic_x = any(i != 0 for i, j in allowed)
    periodic_y = any(j != 0 for i, j in allowed)
    if periodic_x and ix != 0:
        return True
    if periodic_y and iy != 0:
        return True
    return False
