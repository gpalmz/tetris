from functools import reduce


def identity(v):
    return v


def group(sequence, get_key=identity):
    groupings = {}
    for e in sequence:
        groupings.setdefault(get_key(e), []).append(e)
    return groupings
