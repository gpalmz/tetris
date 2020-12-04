import random
from dataclasses import dataclass
from typing import Callable, List, Optional

import rx

from common.model.mcts import TaskNode
from common.model.task import create_select_action_by_utility
from tetris.model.task import TetrisTaskState
from tetris.model.gameplay import Player
from tetris.model.strategy import select_move_random, select_move_smart


@dataclass
class TetrisTaskNode(TaskNode):
    select_move: Callable[[TetrisTaskState, Optional[List["Action"]]], "Action"] = select_move_random

    def expand(self):
        # TODO: will there ever be a null action here? If so, this will error
        # random to avoid getting stuck with the worst move when playout policy ties
        action = select_move_random(self.state, self.unexplored_actions)
        child = TetrisTaskNode(
            self.state.perform_action(action), parent=self, select_move=self.select_move,
        )
        self.action_to_child[action] = child
        return child

    def simulate(self, max_playout_depth=None):
        state = self.state

        i = 0
        while True:
            possible_actions = state.possible_actions
            if not possible_actions or (max_playout_depth is not None and i >= max_playout_depth):
                break
            state = state.perform_action(self.select_move(state, possible_actions))
            i += 1

        print("playout depth:", i)

        return i


@dataclass
class TetrisMctsPlayer(Player):
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