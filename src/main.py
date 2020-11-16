from tetris.model.game import create_initial_board, create_initial_state
from tetris.model.mcts import select_move
from tetris.model.strategy import (
    get_concealed_space_count,
    get_empty_row_count,
    get_concealed_space_utility,
    get_empty_row_utility,
)
from tetris.ui.game import GameBoard


def demo_game_stdout():
    curr_state = create_initial_state()
    while(True):
        move = select_move(curr_state)
        if move is None:
            break
        else:
            curr_state = curr_state.play_move(move)[1]
        print(curr_state.board)
        print(get_concealed_space_count(curr_state))
        print(get_empty_row_count(curr_state))
        print(get_concealed_space_utility(curr_state))
        print(get_empty_row_utility(curr_state))


def demo_game_ui():
    GameBoard(create_initial_board()).play_game()


#demo_game_stdout()
demo_game_ui()
