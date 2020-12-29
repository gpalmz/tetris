from dataclasses import dataclass

from rx.subject import Subject, ReplaySubject, BehaviorSubject
from rx.disposable import CompositeDisposable
from rx import operators as op

from tetris.model.gameplay.common.timer import create_countdown_obs, create_timer
from tetris.model.gameplay.common.game_state import GameState
from tetris.model.board import create_initial_board_state


@dataclass
class GameConductor:
    player: ""
    max_turn_duration: int
    scheduler: ""
    board_state_init: "" = create_initial_board_state()
    move_subject: "" = BehaviorSubject(None)
    turn_time_remaining_subject: "" = BehaviorSubject(None)

    def _run_game(self, game_state):
        move = None

        def set_move(new_move):
            nonlocal move

            if new_move is not None and new_move != move:
                move = new_move
                self.move_subject.on_next((game_state, move, False))

        def play_move():
            nonlocal move

            turn_disposable.dispose()

            if move:
                self.move_subject.on_next((game_state, move, True))
                new_game_state = game_state.play_move(move)
                move = None
                self._run_game(new_game_state)
            else:
                self.turn_time_remaining_subject.on_completed()
                self.move_subject.on_completed()

        countdown_obs = create_countdown_obs(self.max_turn_duration, scheduler=self.scheduler).pipe(
            op.observe_on(self.scheduler),
            op.subscribe_on(self.scheduler),
        )

        timer = create_timer(countdown_obs, self.max_turn_duration)

        turn_disposable = CompositeDisposable(
            self.player.get_move_obs(game_state, timer).pipe(
                op.observe_on(self.scheduler),
                op.subscribe_on(self.scheduler),
            ).subscribe(
                on_next=set_move, 
                on_completed=play_move,
            ),
            countdown_obs.subscribe(
                on_next=self.turn_time_remaining_subject.on_next,
                on_completed=play_move,
            ),
            timer.run(),
        )

    def run_game(self):
        self._run_game(GameState(self.board_state_init, 0))
