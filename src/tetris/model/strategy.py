import math
from dataclasses import dataclass

import rx

from common.util.iter import max_by
from tetris.model.gameplay import Player

WEIGHT_CONCEALED_SPACE_UTILITY = 314
WEIGHT_EMPTY_ROW_UTILITY = 19.53
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


def get_concealed_space_utility(state, weight=WEIGHT_CONCEALED_SPACE_UTILITY):
    square_count = state.board.row_count * state.board.col_count
    return weight * (square_count - get_concealed_space_count(state)) / square_count


def get_empty_row_utility(state, weight=WEIGHT_EMPTY_ROW_UTILITY):
    return weight * get_empty_row_count(state) / state.board.row_count


def get_row_sum_utility(state, weight=WEIGHT_ROW_SUM_UTILITY):
    return weight * get_row_sum(state)


def get_complex_utility(
    state,
    weight_concealed_space_utility=WEIGHT_CONCEALED_SPACE_UTILITY,
    weight_empty_row_utility=WEIGHT_EMPTY_ROW_UTILITY,
    weight_row_sum_utility=WEIGHT_ROW_SUM_UTILITY,
):
    return get_concealed_space_utility(state, weight_concealed_space_utility) + get_empty_row_utility(state, weight_empty_row_utility) + get_row_sum_utility(state, weight_row_sum_utility)

 
def select_move(
    state,
    weight_concealed_space_utility=WEIGHT_CONCEALED_SPACE_UTILITY,
    weight_empty_row_utility=WEIGHT_EMPTY_ROW_UTILITY,
    weight_row_sum_utility=WEIGHT_ROW_SUM_UTILITY,
    possible_moves=None,
):

    if possible_moves is None:
        possible_moves = state.possible_moves
        
    return (
        max_by(
            [
                (
                    move,
                    get_complex_utility(
                        state.play_move(move), 
                        weight_concealed_space_utility, 
                        weight_empty_row_utility, 
                        weight_row_sum_utility,
                    )
                ) 
                for move in possible_moves
            ], 
            lambda item: item[1],
        )[0]
        if possible_moves
        else None
    )


@dataclass
class SimplePlayer(Player):
    """A Tetris player that uses hardcoded logic."""

    def get_move_obs(self, state, timer):
        return rx.of(select_move(state))
