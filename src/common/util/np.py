import numpy as np


def arr_get_safe(arr, idx, default=None):
    """Get a value from a numpy.array, or return a default if out of bounds."""
    try:
        return arr.item(idx)
    except IndexError:
        return default
