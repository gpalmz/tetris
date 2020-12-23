import threading
from dataclasses import dataclass

from rx.subject import Subject, ReplaySubject
from rx.operators import subscribe_on, observe_on

from tetris.model.task import TetrisMoveTimer
from tetris.model.game import create_initial_state


@dataclass
class GameConductor:
    player: ""
    max_turn_duration: int
    unconfirmed_state_subject: "" = Subject()
    state_subject: "" = ReplaySubject()
    move_time_remaining_subject: "" = Subject()
    subscribe_on: "" = None
    observe_on: "" = None

    def run_game(self):
        # TODO: maybe use a replay subject and pass out an initial state
        turn_disposable = None

        def subscribe_to_move(state):
            nonlocal turn_disposable

            move = None
            # TODO: make timer observable, subscribe to it, if 0, play move
            timer = TetrisMoveTimer(self.max_turn_duration)

            def set_move(new_move):
                nonlocal move

                if new_move and new_move != move:
                    move = new_move
                    self.unconfirmed_state_subject.on_next((state, move))

            def play_move():
                nonlocal state

                if turn_disposable is not None:
                    turn_disposable.dispose()
                timer.end()

                if move:
                    state = state.play_move(move)
                    self.state_subject.on_next(state)
                    subscribe_to_move(state)
                else:
                    self.state_subject.on_completed()

            threading.Thread(target=timer.start, daemon=True).start()
            move_obs = self.player.get_move_obs(state, timer)

            if self.subscribe_on is not None:
                move_obs = move_obs.pipe(subscribe_on(self.subscribe_on))
            if self.observe_on is not None:
                move_obs = move_obs.pipe(observe_on(self.observe_on))
            
            turn_disposable = move_obs.subscribe(on_next=set_move, on_completed=play_move)

        # TODO: pass initial state with score of 0, empty board, no prospective move
        subscribe_to_move(create_initial_state())