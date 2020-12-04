from dataclasses import dataclass

from common.model.task import Task, TaskState
from tetris.model.game import State
from tetris.model.gameplay import MoveTimer


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
    def possible_actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))