from tetris.model.game import create_initial_state
from tetris.model.mcts import select_move
from tetris.model.strategy import (
    get_concealed_block_count, 
    get_empty_row_count,
    get_concealed_block_utility,
    get_empty_row_utility,
)


def demo_game():
    curr_state = create_initial_state()
    while(True):
        move = select_move(curr_state)
        if move is None:
            break
        else:
            curr_state = curr_state.play_move(move)
        print(curr_state.board)
        print(get_concealed_block_count(curr_state))
        print(get_empty_row_count(curr_state))
        print(get_concealed_block_utility(curr_state))
        print(get_empty_row_utility(curr_state))


demo_game()