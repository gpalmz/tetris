from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
import rx
import multiprocessing
from time import sleep
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
        GameDisplay(create_initial_board(), SimplePlayer()).play_game()


# demo_game_stdout()
demo_game_ui()

exit()

def generate_moves(state, timer):
    for i in range(10):
        yield i
        sleep(1)


class Player:
    def get_move_obs(self, state, timer):
        return rx.from_iterable(generate_moves(state, timer))


def get_thread_pool_scheduler():
    return ThreadPoolScheduler(multiprocessing.cpu_count())


scheduler = get_thread_pool_scheduler()

p = Player()


moves = []

p.get_move_obs(None, None).pipe(
    ops.subscribe_on(scheduler)
).subscribe(
    on_next=lambda move: moves.append(move),
    on_completed=lambda: None,  # display move
)

for _ in range(10):
    print('hello')
    sleep(1)
