from dataclasses import dataclass

import pygame
from rx.subject import ReplaySubject

from tetris.model.game import Move
from tetris.model.gameplay.common.player import Player
from tetris.model.strategy import select_move_random


def _transition_move(old_move, new_move, state):
    return new_move if new_move in state.possible_moves else old_move


def _move_left(move, state):
    return _transition_move(move, Move(move.col - 1, move.orientation), state)


def _move_right(move, state):
    return _transition_move(move, Move(move.col + 1, move.orientation), state)


def _rotate(move, state):
    return _transition_move(move, Move(move.col, move.orientation.rotated_90_ccw()), state)


@dataclass
class InteractivePlayer(Player):
    key_event_obs: "Observable[pygame.event]"
    turn_disposable: "Disposable" = None

    def get_move_obs(self, state, timer):
        if self.turn_disposable is not None:
            self.turn_disposable.dispose()

        move_subject = ReplaySubject()

        if state.possible_moves:
            move = None

            def set_move(new_move):
                nonlocal move

                move = new_move
                move_subject.on_next(move)

            def on_next_event(event):
                if event.key == pygame.K_LEFT:
                    set_move(_move_left(move, state))
                elif event.key == pygame.K_RIGHT:
                    set_move(_move_right(move, state))
                elif event.key == pygame.K_UP:
                    set_move(_rotate(move, state))
                elif event.key == pygame.K_SPACE:
                    move_subject.on_completed()
            
            set_move(select_move_random(state, state.possible_moves))
            self.turn_disposable = self.key_event_obs.subscribe(on_next_event)
        else:
            move_subject.on_completed()

        return move_subject