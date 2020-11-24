from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
import rx
import multiprocessing
from tetris.model.game import create_initial_state, create_initial_board
from tetris.model.strategy import (
    select_move,
    get_concealed_space_count,
    get_empty_row_count,
    get_row_sum,
    get_concealed_space_utility,
    get_empty_row_utility,
    get_row_sum_utility,
    SimplePlayer,
)
from tetris.model.mcts import TetrisMctsPlayer
from tetris.ui.game import GameDisplay, pygame_session


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
    with pygame_session():
        GameDisplay(create_initial_board(), TetrisMctsPlayer()).play_game()


from common.model.mcts import mcts
from tetris.model.mcts import TetrisTaskNode, TetrisTaskState
from tetris.model.gameplay import MoveTimer


def run_mcts():
    state = create_initial_state()
    timer = MoveTimer(100)
    for move in mcts(timer, TetrisTaskNode(TetrisTaskState(state))):
        print(move)


# demo_game_stdout()
demo_game_ui()
# run_mcts()
