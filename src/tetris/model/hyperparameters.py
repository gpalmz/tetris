import numpy as np
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, RegressorMixin

from common.model.task import create_select_action_by_utility
from tetris.model.game import create_initial_state
from tetris.model.strategy import get_complex_utility
from tetris.model.task import TetrisTaskState


RANGE_WEIGHT_CONCEALED_SPACE_UTILITY = np.arange(-100000, 0, 100)
RANGE_WEIGHT_EMPTY_ROW_UTILITY = np.arange(0, 500, 1)
RANGE_WEIGHT_ROW_SUM_UTILITY = np.arange(0, 0.01, 0.00001)


def create_get_utility_with_params(
    weight_concealed_space_utility,
    weight_empty_row_utility,
    weight_row_sum_utility,
):
    """Create a state utility estimator function that closes over the given 
    parameters."""
    return lambda state: get_complex_utility(
        state,
        weight_concealed_space_utility=weight_concealed_space_utility,
        weight_empty_row_utility=weight_empty_row_utility,
        weight_row_sum_utility=weight_row_sum_utility,
    )


def get_game_turn_count(get_utility):
    """Play a game of Tetris using a state utility estimator function and 
    produce the number of turns the game lasted."""
    state = TetrisTaskState(create_initial_state())
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
            create_get_utility_with_params(
                self.weight_concealed_space_utility, 
                self.weight_empty_row_utility, 
                self.weight_row_sum_utility,
            )
        )
        return self

    def predict(self, X, y=None):
        return [self.score_ for x in X]

    def score(self, X, y=None):
        return sum(self.predict(X))


# TODO: what do the magic numbers mean and how were they selected?
def tune_move_selector(
    n_iter=20, 
    n_samples=50, 
    concealed_util=RANGE_WEIGHT_CONCEALED_SPACE_UTILITY, 
    empty_util=RANGE_WEIGHT_EMPTY_ROW_UTILITY, 
    row_sum_util=RANGE_WEIGHT_ROW_SUM_UTILITY,
):
    """Produce a tuned game state utility estimator function."""
    return create_select_action_by_utility(
        create_get_utility_with_params(
            **RandomizedSearchCV(
                GameLengthEstimator(),
                dict(
                    weight_concealed_space_utility=concealed_util,
                    weight_empty_row_utility=empty_util,
                    weight_row_sum_utility=row_sum_util,
                ),
                n_iter=n_iter,
            ).fit(
                [1 for i in range(n_samples)], 
                y=[1 for i in range(n_samples)],
            ).best_params_
        )
    )
