from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

import rx

from tetris.model.task import TetrisTaskState
from tetris.model.strategy import select_move_smart, select_move_random, get_complex_utility
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