import random
from dataclasses import dataclass

from common.util.iter import max_by
from common.model.mcts import Task, TaskState, TaskNode, mcts
from tetris.model.strategy import get_complex_utility
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


def get_utility_by_move(state, get_utility):
    return [(move, get_utility(state.play_move(move))) for move in state.possible_moves]


def select_move(state):
    # for now just return the best move, later maybe we'll work in probability
    utility_by_move = get_utility_by_move(state, get_complex_utility)
    return max_by(utility_by_move, lambda item: item[1])[0] if utility_by_move else None


@dataclass
class TetrisMctsPlayer:
    def get_move(self, task, state):
        return mcts(task, TetrisTaskState(state), TetrisTaskNode)
