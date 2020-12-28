import functools

import numpy as np
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, RegressorMixin

from common.model.task import create_select_action_by_utility
from tetris.model.board import create_initial_board_state
from tetris.model.strategy import get_complex_utility
from tetris.model.task import TetrisTaskState

PARAM_DISTRIBUTIONS = dict(
    weight_concealed_space_utility=np.arange(0, 500, 1),
    weight_empty_row_utility=np.arange(0, 50, 0.1),
    weight_row_sum_utility=np.arange(0, 1, 0.001),
)


def get_game_turn_count(get_utility):
    """Play a game of Tetris using a state utility estimator function and 
    produce the number of turns the game lasted."""
    state = TetrisTaskState(create_initial_board_state())
    move_count = 0

    while True:
        # TODO: why is try/catch necessary?
        try:
            move = create_select_action_by_utility(get_utility)(
                state, state.possible_actions,
            )
            if move:
                state = state.perform_action(move)
                move_count += 1
            else:
                break
        except ValueError:
            break

    return move_count


class GameLengthEstimator(BaseEstimator, RegressorMixin):

    def __init__(
        self, 
        weight_concealed_space_utility=0, 
        weight_empty_row_utility=0, 
        weight_row_sum_utility=0,
    ):
        self.weight_concealed_space_utility = weight_concealed_space_utility
        self.weight_empty_row_utility = weight_empty_row_utility
        self.weight_row_sum_utility = weight_row_sum_utility
        self.score_ = 0

    def fit(self, X, y=None):
        self.score_ = get_game_turn_count(
            functools.partial(
                get_complex_utility,
                weight_concealed_space_utility=self.weight_concealed_space_utility, 
                weight_empty_row_utility=self.weight_empty_row_utility, 
                weight_row_sum_utility=self.weight_row_sum_utility,
            )
        )
        return self

    def predict(self, X, y=None):
        return [self.score_ for x in X]

    def score(self, X, y=None):
        return sum(self.predict(X))


# TODO: what do the magic numbers mean and how were they selected?
def tune_move_selector_params(n_iter=20, n_samples=50, param_distributions=PARAM_DISTRIBUTIONS):
    return RandomizedSearchCV(
        GameLengthEstimator(), param_distributions, n_iter=n_iter,
    ).fit(
        # TODO: remove duplicate
        tuple(1 for i in range(n_samples)), y=tuple(1 for i in range(n_samples)),
    ).best_params_
