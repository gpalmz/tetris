import numpy as np


def arr_get_safe(arr, idx, default=None):
    """Get a value from a numpy.array, or return a default if out of bounds."""
    try:
        return arr.item(idx)
    except IndexError:
        return default


def arr_rotated_90_cw(arr, rotation_count=1):
    """Produce a numpy.array from the given array rotated clockwise."""
    rotated_grid = np.copy(arr)
    for _ in range(rotation_count):
        rotated_grid = np.flip(np.transpose(rotated_grid), axis=1)
    return rotated_grid
