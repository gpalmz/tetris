import math
import random
from dataclasses import dataclass

import rx

from tetris.model.gameplay import Player
from common.model.task import create_select_action_by_utility
from tetris.model.task import TetrisTaskState

WEIGHT_CONCEALED_SPACE_UTILITY = -62600
WEIGHT_EMPTY_ROW_UTILITY = 391
WEIGHT_ROW_SUM_UTILITY = 0.0056500000000000005


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


def get_empty_row_count(state):
    """Produce the number of empty rows."""
    placements = state.board.block_placements
    return min(p.row for p in placements) if placements else state.board.row_count


def get_row_sum(state):
    """Produce the sum of the row indices of all blocks."""
    return sum(p.row for p in state.board.block_placements)


def get_complex_utility(
    state,
    weight_concealed_space_utility=WEIGHT_CONCEALED_SPACE_UTILITY,
    weight_empty_row_utility=WEIGHT_EMPTY_ROW_UTILITY,
    weight_row_sum_utility=WEIGHT_ROW_SUM_UTILITY,
):
    return (
        get_concealed_space_count(state.state) * weight_concealed_space_utility
        + get_empty_row_count(state.state) * weight_empty_row_utility
        + get_row_sum(state.state) * weight_row_sum_utility
    )


select_move_smart = create_select_action_by_utility(get_complex_utility)


def select_move_random(state, possible_moves):
    return random.choice(possible_moves)
# a slower implementation of select_move_random that actually applies all possible moves
# select_move_random = create_select_action_by_utility(lambda state: 0)


@dataclass
class SimplePlayer(Player):
    """A Tetris player that uses hardcoded logic."""

    def get_move_obs(self, state, timer):
        return rx.of(select_move_smart(TetrisTaskState(state), state.possible_moves))
