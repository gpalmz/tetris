import random
from dataclasses import dataclass

from common.model.mcts import Task, TaskState, TaskNode, mcts
from tetris.model.game import State


# TODO: store a countdown timer, set it running when the task is started
@dataclass
class TetrisMoveTask(Task):
    @property
    def time_remaining(self):
        return 1

    def start(self):
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


@dataclass
class TetrisTaskNode(TaskNode):
    @property
    def success_count(self):
        pass

    @property
    def failure_count(self):
        pass

    def select_leaf(self):
        pass

    def expand(self):
        pass

    def simulate(self):
        # explore playouts stemming from the current state
        pass

    def back_propagate(self, result):
        pass


@dataclass
class TetrisMctsPlayer:
    def get_move(self, task, state):
        return mcts(task, TetrisTaskState(state), TetrisTaskNode)
