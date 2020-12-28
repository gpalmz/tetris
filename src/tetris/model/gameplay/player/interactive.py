from dataclasses import dataclass

import pygame
from rx.subject import ReplaySubject

from tetris.model.board import Move
from tetris.model.gameplay.common.player import Player
from tetris.model.strategy import select_move_random


def _transition_move(old_move, new_move, board_state):
    return new_move if new_move in board_state.possible_moves else old_move


def _move_left(move, board_state):
    return _transition_move(move, Move(move.col - 1, move.orientation), board_state)


def _move_right(move, board_state):
    return _transition_move(move, Move(move.col + 1, move.orientation), board_state)


def _rotate(move, board_state):
    return _transition_move(move, Move(move.col, move.orientation.rotated_90_ccw()), board_state)


@dataclass
class InteractivePlayer(Player):
    key_event_obs: "Observable[pygame.event]"

    def get_move_obs(self, game_state, timer):
        # TODO: consider behavior subject
        move_subject = ReplaySubject()
        s = game_state

        if s.possible_moves:
            move = None

            def set_move(new_move):
                nonlocal move

                move = new_move
                move_subject.on_next(move)

            def on_next_event(event):
                if event.key == pygame.K_LEFT:
                    set_move(_move_left(move, s))
                elif event.key == pygame.K_RIGHT:
                    set_move(_move_right(move, s))
                elif event.key == pygame.K_UP:
                    set_move(_rotate(move, s))
                elif event.key == pygame.K_SPACE:
                    move_subject.on_completed()
            
            set_move(select_move_random(s, s.possible_moves))
            # TODO: dispose
            self.key_event_obs.subscribe(on_next_event)
        else:
            move_subject.on_completed()

        return move_subject
