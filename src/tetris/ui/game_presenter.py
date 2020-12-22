import threading
from dataclasses import dataclass

from rx.subject import Subject

from tetris.model.task import TetrisMoveTimer
from tetris.model.game import create_initial_state


@dataclass
class GamePresenter:
    player: ""
    max_turn_duration: int
    unconfirmed_state_subject: "" = Subject()
    state_subject: "" = Subject()

    def run_game(self):

        def subscribe_to_move(state):
            move = None
            timer = TetrisMoveTimer(self.max_turn_duration)

            def set_move(new_move):
                nonlocal move
                if new_move and new_move != move:
                    move = new_move
                    self.unconfirmed_state_subject.on_next(state.play_move(move))

            def play_move():
                nonlocal state
                timer.end()
                if move:
                    state = state.play_move(move)
                    self.state_subject.on_next(state)
                    subscribe_to_move(state)

            threading.Thread(target=timer.start, daemon=True).start()
            self.player.get_move_obs(state, timer).subscribe(
                on_next=set_move, on_completed=play_move,
            )

        subscribe_to_move(create_initial_state())