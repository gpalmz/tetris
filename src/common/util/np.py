import numpy as np


def arr_get_safe(arr, idx, default=None):
    """Get a value from a numpy.array, or return a default if out of bounds."""
    try:
        return arr.item(idx)
    except IndexError:
        return default


def arr_to_coords(arr, is_present):
    """Create a list of coordinates in a numpy.array where values are present."""
    return [coord for coord, val in np.ndenumerate(arr) if is_present(val)]


def arr_rotated_90_cw(arr, rotation_count=1):
    """Produce a numpy.array from the given array rotated clockwise."""
    rotated_grid = np.copy(arr)
    for _ in range(rotation_count):
        rotated_grid = np.flip(np.transpose(rotated_grid), axis=1)
    return rotated_grid
