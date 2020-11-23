import random
from dataclasses import dataclass
from functools import cached_property

import rx

from common.model.mcts import Task, TaskState, TaskNode, mcts
from tetris.model.game import State
from tetris.model.gameplay import Player, MoveTimer
from tetris.model.strategy import select_move

MAX_PLAYOUT_TURNS = 1000


@dataclass
class TetrisMoveTask(Task, MoveTimer):
    """A task for providing a move in a certain time frame"""
    # Task functionality inherited from MoveTimer
    pass


@dataclass
class TetrisTaskState(TaskState):
    """Adapter for the tetris game state for MCTS."""
    state: State

    @property
    def is_terminal(self):
        return not self.actions

    @cached_property
    def actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))


@dataclass
class TetrisTaskNode(TaskNode):

    def expand(self):
        explored_actions = set(self.explored_actions)
        # TODO: will there ever be a null action here? If so, this will error
        unexplored_actions = [a for a in self.state.actions if a not in explored_actions]
        action = list(select_move(unexplored_actions))[-1]
        child = TetrisTaskNode(self.state.perform_action(action), parent=self)
        self.child_by_action[action] = child
        return child

    def simulate(self):
        state = self.state

        for i in range(MAX_PLAYOUT_TURNS):
            if state.is_terminal:
                break
            state = state.perform_action(list(select_move(state.actions))[-1])

        # return the number of iterations as the value for the playout
        return i


@dataclass
class TetrisMctsPlayer(Player):
    """A Tetris player that uses the Monte Carlo Tree Search algorithm."""

    def get_move_obs(self, state, timer):
        return rx.from_iterable(mcts(timer, TetrisTaskNode(TetrisTaskState(state))))
