import math

WEIGHT_CONCEALED_SPACE_UTILITY = 50
WEIGHT_EMPTY_ROW_UTILITY = 1
WEIGHT_ROW_SUM_UTILITY = 0.0001


def get_concealed_space_count_for_coord(state, row, col):
    """Produce the number of blocks concealed by a block at the given position."""
    # if there isn't a block at the coord, it's not concealing anything.
    if state.board.is_coord_empty(row, col):
        return 0

    curr_row = row
    while state.board.is_coord_empty(curr_row + 1, col):
        curr_row += 1

    return curr_row - row


def get_concealed_space_count(state):
    return sum(
        get_concealed_space_count_for_coord(
            state, placement.row, placement.col)
        for placement
        in state.board.block_placements
    )


def get_empty_row_count(state):
    return min(placement.row for placement in state.board.block_placements)


def get_row_sum(state):
    return sum(placement.row for placement in state.board.block_placements)


def get_concealed_space_utility(state):
    square_count = (state.board.row_count * state.board.col_count)
    return (
        WEIGHT_CONCEALED_SPACE_UTILITY *
        (square_count - get_concealed_space_count(state)) / square_count
    )


def get_empty_row_utility(state):
    return WEIGHT_EMPTY_ROW_UTILITY * get_empty_row_count(state) / state.board.row_count


def get_row_sum_utility(state):
    return WEIGHT_ROW_SUM_UTILITY * get_row_sum(state)


def get_complex_utility(state):
    return get_concealed_space_utility(state) + get_empty_row_utility(state) + get_row_sum_utility(state)
