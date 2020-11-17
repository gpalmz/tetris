from tetris.model.game import create_initial_state, create_initial_board
from tetris.model.mcts import select_move
from tetris.model.strategy import (
    get_concealed_space_count,
    get_empty_row_count,
    get_row_sum,
    get_concealed_space_utility,
    get_empty_row_utility,
    get_row_sum_utility,
)
from tetris.ui.game import GameBoard


def demo_game_stdout():
    curr_state = create_initial_state()
    turn_count = 0
    while(True):
        move = select_move(curr_state)
        if move is None:
            break
        else:
            curr_state = curr_state.play_move(move)
            turn_count += 1
        
        print(curr_state.board)
        print("turn count", turn_count)
        print("concealed count", get_concealed_space_count(curr_state))
        print("empty row count", get_empty_row_count(curr_state))
        print("row sum", get_row_sum(curr_state))
        print("concealed utility", get_concealed_space_utility(curr_state))
        print("empty row utility", get_empty_row_utility(curr_state))
        print("row sum utility", get_row_sum_utility(curr_state))


def demo_game_ui():
    GameBoard(create_initial_board()).play_game()


# demo_game_stdout()
demo_game_ui()
