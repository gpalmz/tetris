from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

import pygame
import rx
from rx.subject import ReplaySubject

from tetris.model.task import TetrisTaskState
from tetris.model.strategy import select_move_smart, select_move_random, get_complex_utility
from tetris.model.mcts import TetrisTaskNode
from tetris.model.game import Move, PieceOrientation


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, timer):
        pass


@dataclass
class SimplePlayer(Player):
    """A Tetris player that uses hardcoded logic."""

    def get_move_obs(self, state, timer):
        return rx.from_iterable(
            filter(None, [select_move_smart(TetrisTaskState(state), state.possible_moves)])
        )


@dataclass
class MctsPlayer(Player):
    """A Tetris player that uses the Monte Carlo Tree Search algorithm."""
    select_move: Callable[[TetrisTaskState, List["Action"]], "Action"] = select_move_random
    get_utility: Callable[[TetrisTaskState], float] = get_complex_utility
    max_playout_depth: Optional[int] = None

    def get_move_obs(self, state, timer):
        return rx.from_iterable(
            TetrisTaskNode(
                TetrisTaskState(state), 
                select_move=self.select_move,
                get_utility=self.get_utility,
            ).mcts(
                timer, max_playout_depth=self.max_playout_depth
            )
        )


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