import json
import math
import random

from common.model.task import create_select_action_by_utility


def get_scaled_param_weights(dct):
    """Produce a dict with all param weights scaled to sum to 1."""
    total = sum(dct.values())
    return {k: v / total for k, v in dct.items()}


with open("../config/params.json") as f:
    PARAM_WEIGHTS = get_scaled_param_weights(json.load(f))
WEIGHT_CONCEALED_SPACE_UTILITY = PARAM_WEIGHTS["weight_concealed_space_utility"]
WEIGHT_EMPTY_ROW_UTILITY = PARAM_WEIGHTS["weight_empty_row_utility"]
WEIGHT_ROW_SUM_UTILITY = PARAM_WEIGHTS["weight_row_sum_utility"]


def get_concealed_space_count_for_coord(state, row, col):
    """Produce the number of empty spaces concealed by a block at the given position."""
    # if there isn't a block at the coord, it's not concealing anything.
    if state.board.is_coord_empty(row, col):
        return 0

    curr_row = row
    while state.board.is_coord_empty(curr_row + 1, col):
        curr_row += 1

    return curr_row - row


def get_concealed_space_count(state):
    """Produce the number of empty spaces concealed by blocks."""
    return sum(
        get_concealed_space_count_for_coord(
            state, placement.row, placement.col)
        for placement
        in state.board.block_placements
    )


def get_unconcealed_space_proportion(state):
    """Produce the proportion of squares that are not concealed spaces."""
    return 1 - get_concealed_space_count(state) / (state.board.row_count * state.board.col_count)


def get_empty_row_count(state):
    """Produce the number of empty rows."""
    placements = state.board.block_placements
    return min(p.row for p in placements) if placements else state.board.row_count


def get_empty_row_proportion(state):
    """Produce the proportion of rows that are empty."""
    return get_empty_row_count(state) / state.board.row_count


def get_row_sum(state):
    """Produce the sum of the row indices of all blocks."""
    return sum(p.row for p in state.board.block_placements)


def get_max_row_sum(state):
    r = state.board.row_count
    c = state.board.col_count
    return r * (r - 1) * c // 2


def get_row_sum_proportion(state):
    """Produce the proportion of total row coordinates to the maximum possible."""
    return get_row_sum(state) / get_max_row_sum(state)


def get_complex_utility(
    state,
    weight_concealed_space_utility=WEIGHT_CONCEALED_SPACE_UTILITY,
    weight_empty_row_utility=WEIGHT_EMPTY_ROW_UTILITY,
    weight_row_sum_utility=WEIGHT_ROW_SUM_UTILITY,
):
    return (
        get_unconcealed_space_proportion(state.state) * weight_concealed_space_utility
        + get_empty_row_proportion(state.state) * weight_empty_row_utility
        + get_row_sum_proportion(state.state) * weight_row_sum_utility
    ) * 20  # TODO: magic number to make these vary similarly to a win/loss scheme


select_move_smart = create_select_action_by_utility(get_complex_utility)


def select_move_random(state, possible_moves):
    return random.choice(possible_moves)
# a slower implementation of select_move_random that actually applies all possible moves
# select_move_random = create_select_action_by_utility(lambda state: 0)
