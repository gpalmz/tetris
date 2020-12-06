import json
import numpy as np


def arr_get_safe(arr, idx, default=None):
    """Get a value from a numpy.array, or return a default if out of bounds."""
    try:
        return arr.item(idx)
    except IndexError:
        return default


class NumpyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super().default(obj)