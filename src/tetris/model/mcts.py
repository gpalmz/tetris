import random
from dataclasses import dataclass
from typing import Callable, List, Optional

from common.model.mcts import TaskNode
from tetris.model.task import TetrisTaskState
from tetris.model.strategy import select_move_random


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