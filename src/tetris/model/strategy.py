WEIGHT_CONCEALED_BLOCK_UTILITY = 100
WEIGHT_EMPTY_ROW_UTILITY = 1


def get_concealed_by_block_count(state, row, col):
    curr_row = row + 1
    while state.board.is_coord_empty(curr_row, col):
        curr_row += 1
    return curr_row - row


def get_concealed_block_count(state):
    return sum(
        get_concealed_by_block_count(state, row, col) 
        for row, col 
        in state.board.block_coords
    )


def get_empty_row_count(state):
    return min(row for row, col in state.board.block_coords)


def get_concealed_block_utility(state):
    total_block_count = (state.board.num_rows * state.board.num_cols)
    return (
        WEIGHT_CONCEALED_BLOCK_UTILITY *
        (total_block_count - get_concealed_block_count(state)) / total_block_count
    )


def get_empty_row_utility(state):
    return WEIGHT_EMPTY_ROW_UTILITY * get_empty_row_count(state) / state.board.num_rows


def get_concealed_block_and_empty_row_utility(state):
    return get_concealed_block_utility(state) + get_empty_row_utility(state)