from dataclasses import dataclass

from common.model.task import Task, TaskState
from tetris.model.gameplay.common.game_state import GameState
from tetris.model.gameplay.common.timer import Timer


@dataclass
class TetrisMoveTask(Task):
    """Adapter for the tetris move timer for the Task interface."""
    timer: Timer

    @property
    def time_remaining(self):
        return self.timer.time_remaining_sec


@dataclass
class TetrisTaskState(TaskState):
    """Adapter for the tetris game state for the TaskState interface."""
    # TODO: rename to game_state
    state: GameState

    @property
    def possible_actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))
