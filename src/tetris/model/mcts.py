import random
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, List

import rx

from common.model.mcts import Task, TaskState, TaskNode, mcts
from tetris.model.game import State
from tetris.model.gameplay import Player, MoveTimer
from tetris.model.strategy import select_move

MAX_PLAYOUT_TURNS = 100


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
        return not self.possible_actions

    @cached_property
    def possible_actions(self):
        return self.state.possible_moves

    def perform_action(self, action):
        return TetrisTaskState(self.state.play_move(action))


def select_random_move(state, possible_moves=None):
    if possible_moves is None:
        possible_moves = state.possible_moves

    return random.choice(possible_moves)


@dataclass
class TetrisTaskNode(TaskNode):
    select_move: Callable[[List["Action"]], "Action"] = select_random_move

    def expand(self):
        # TODO: will there ever be a null action here? If so, this will error
        # random to avoid getting stuck with the worst move when playout policy ties
        action = select_random_move(self.state.state, possible_moves=self.unexplored_actions)
        child = TetrisTaskNode(self.state.perform_action(action), parent=self)
        self.action_to_child[action] = child
        return child

    def simulate(self):
        state = self.state

        for i in range(MAX_PLAYOUT_TURNS):
            if state.is_terminal:
                break
            state = state.perform_action(self.select_move(state.state))

        return i


@dataclass
class TetrisMctsPlayer(Player):
    select_move: Callable[[List["Action"]], "Action"] = select_move

    """A Tetris player that uses the Monte Carlo Tree Search algorithm."""

    def get_move_obs(self, state, timer):
        # TODO: can we reuse some subset of the previous tree given that we 
        # choose a move from it at each turn?
        return rx.from_iterable(
            mcts(
                timer, 
                TetrisTaskNode(TetrisTaskState(state), select_move=self.select_move),
            )
        )
