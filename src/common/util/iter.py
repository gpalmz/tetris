# TODO: see what can be removed
import operator
from functools import reduce


def identity(v):
    return v


def _place_into(groupings, element, group):
    groupings.setdefault(group, []).append(element)
    return groupings


def group(iterable, get_group=identity):
    return reduce(lambda g, e: _place_into(g, e, get_group(e)), iterable, {})


def best(iterable, cmp):
    return reduce(lambda acc, e: acc if cmp(acc, e) else e, iterable)


def best_by(iterable, cmp, get=identity):
    return best(iterable, lambda v0, v1: cmp(get(v0), get(v1)))


def min_by(iterable, get=identity):
    return best_by(iterable, operator.lt, get=get)


def max_by(iterable, get=identity):
    return best_by(iterable, operator.gt, get=get)
