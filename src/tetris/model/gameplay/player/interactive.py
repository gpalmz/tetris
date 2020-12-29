from dataclasses import dataclass

import pygame
from rx.subject import ReplaySubject

from tetris.model.board import Move
from tetris.model.gameplay.common.player import Player
from tetris.model.strategy import select_move_random


def _move_left(board_state, move):
    new_move = Move(move.col - 1, move.orientation)
    return new_move if new_move in board_state.possible_moves else move


def _move_right(board_state, move):
    new_move = Move(move.col + 1, move.orientation)
    return new_move if new_move in board_state.possible_moves else move


def _rotate(board_state, move):
    new_move = Move(move.col, move.orientation.rotated_90_ccw())
    return new_move if new_move in board_state.possible_moves else move


def _constrain_right(board_state, move):
    board_width = board_state.board.col_count
    piece_width = board_state.get_piece_for_move(move).col_count
    if move.col + piece_width >= board_width:
        return Move(board_width - piece_width, move.orientation)
    else:
        return move


def _rotate(board_state, move):
    rotated_move = Move(move.col, move.orientation.rotated_90_ccw())
    if rotated_move in board_state.possible_moves:
        return rotated_move
    else:
        # sometimes rotating a piece pushes its right bound off the board.
        # for convenience, try shifting it left. if still invalid, return original move.
        # this only happens on the right side since pieces are anchored on the top left.
        constrained_rotated_move = _constrain_right(board_state, rotated_move)
        if constrained_rotated_move in board_state.possible_moves:
            return constrained_rotated_move
        else:
            return move


@dataclass
class InteractivePlayer(Player):
    key_event_obs: "Observable[pygame.event]"
    key_event_disposable: "" = None

    def get_move_obs(self, game_state, timer):
        if self.key_event_disposable is not None:
            self.key_event_disposable.dispose()

        # TODO: use behavior subject
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
                    set_move(_move_left(s, move))
                elif event.key == pygame.K_RIGHT:
                    set_move(_move_right(s, move))
                elif event.key == pygame.K_UP:
                    set_move(_rotate(s, move))
                elif event.key == pygame.K_SPACE:
                    move_subject.on_completed()
            
            set_move(select_move_random(s, s.possible_moves))
            self.key_event_disposable = self.key_event_obs.subscribe(on_next_event)
        else:
            move_subject.on_completed()

        return move_subject
