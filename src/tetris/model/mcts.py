import random
from dataclasses import dataclass

from common.model.mcts import Task, TaskState, TaskNode, mcts
from tetris.model.game import State
from tetris.model.gameplay import Player, MoveTimer


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

    @property
    def actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        self.state.play_move(action)


# TODO: fill this out
@dataclass
class TetrisTaskNode(TaskNode):
    def playout_utility_sum(self):
        pass

    def playout_count(self):
        pass

    def select_leaf(self):
        pass

    def expand(self):
        pass

    def simulate(self):
        pass

    def back_propagate(self, result):
        pass


@dataclass
class TetrisMctsPlayer(Player):
    """A Tetris player that uses the Monte Carlo Tree Search algorithm."""

    def get_move(self, state, timer):
        return mcts(timer, TetrisTaskState(state), TetrisTaskNode)
