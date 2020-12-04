from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

import rx

from tetris.model.task import TetrisTaskState
from tetris.model.strategy import select_move_smart, select_move_random
from tetris.model.mcts import TetrisTaskNode


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, timer):
        pass


@dataclass
class SimplePlayer(Player):
    """A Tetris player that uses hardcoded logic."""

    def get_move_obs(self, state, timer):
        return rx.of(select_move_smart(TetrisTaskState(state), state.possible_moves))


# TODO: use TetrisMoveTask instead of timer
@dataclass
class MctsPlayer(Player):
    select_move: Callable[[TetrisTaskState, Optional[List["Action"]]], "Action"] = select_move_random

    max_playout_depth: Optional[int] = None

    """A Tetris player that uses the Monte Carlo Tree Search algorithm."""

    def get_move_obs(self, state, timer):
        # TODO: can we reuse some subset of the previous tree given that we 
        # choose a move from it at each turn?
        return rx.from_iterable(
            TetrisTaskNode(TetrisTaskState(state), select_move=self.select_move).mcts(
                timer, max_playout_depth=self.max_playout_depth
            )
        )