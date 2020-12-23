from dataclasses import dataclass
from typing import Callable, List, Optional

import rx

from tetris.model.mcts import TetrisTaskNode
from tetris.model.strategy import select_move_random, get_complex_utility
from tetris.model.task import TetrisTaskState
from tetris.model.gameplay.common.player import Player


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
 