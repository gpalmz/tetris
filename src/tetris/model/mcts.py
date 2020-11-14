from dataclasses import dataclass

from common.model.mcts import TaskState
from tetris.model.game import State


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