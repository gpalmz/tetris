from dataclasses import dataclass

from common.model.task import Task, TaskState
from tetris.model.game import State


# this is a fake timer
# fight me
@dataclass
class TetrisMoveTask:
    time: int

    @property
    def time_remaining(self):
        t = self.time
        if t > 0:
            self.time -= 1
        return t


@dataclass
class TetrisTaskState(TaskState):
    """Adapter for the tetris game state for MCTS."""
    state: State

    @property
    def possible_actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))