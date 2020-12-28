from dataclasses import dataclass

import rx

from tetris.model.strategy import select_move_smart
from tetris.model.task import TetrisTaskState
from tetris.model.gameplay.common.player import Player


@dataclass
class SimplePlayer(Player):
    """A Tetris player that uses hardcoded logic."""
    select_move: "" = select_move_smart

    def get_move_obs(self, game_state, timer):
        task_state = TetrisTaskState(game_state)
        move = self.select_move(task_state, task_state.possible_actions)
        return rx.just(move) if move is not None else rx.empty()
