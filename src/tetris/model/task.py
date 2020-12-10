import time
from dataclasses import dataclass

from common.model.task import Task, TaskState
from tetris.model.game import State


@dataclass
class TetrisMoveTimer(Task):
    time: int

    # unfortunate that you have to use a computed property when implementing an abstract property
    # TODO: probably better to make this observable regardless
    @property
    def time_remaining(self):
        return self.time

    def start(self):
        while self.time:
            time.sleep(1)
            self.time -= 1
    
    def end(self):
        self.time = 0


@dataclass
class TetrisTaskState(TaskState):
    """Adapter for the tetris game state for MCTS."""
    state: State

    @property
    def possible_actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))