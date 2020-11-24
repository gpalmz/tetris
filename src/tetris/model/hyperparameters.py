import numpy as np
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, RegressorMixin

from tetris.model.game import create_initial_state
from tetris.model.strategy import select_move


RANGE_WEIGHT_CONCEALED_SPACE_UTILITY = np.arange(0, 500, 1)
RANGE_WEIGHT_EMPTY_ROW_UTILITY = np.arange(0, 20, 0.01)
RANGE_WEIGHT_ROW_SUM_UTILITY = np.arange(0, 0.01, 0.00001)

def get_turns_alive_count(
    weight_concealed_space_utility,
    weight_empty_row_utility,
    weight_row_sum_utility,
):
    state = create_initial_state()
    move_count = 0

    while True:
        try:
            move = list(select_move(
                state,
                weight_concealed_space_utility=weight_concealed_space_utility,
                weight_empty_row_utility=weight_empty_row_utility,
                weight_row_sum_utility=weight_row_sum_utility,
            ))[-1]

            if move:
                state = state.play_move(move)
                move_count += 1
            else:
                break
        except ValueError as e:
            break
    print(weight_concealed_space_utility, weight_empty_row_utility, weight_row_sum_utility, move_count)
    return move_count

class GameClassifier(BaseEstimator, RegressorMixin):  

    def __init__(self, weight_concealed_space_utility=0, weight_empty_row_utility=0, weight_row_sum_utility=0):
        self.weight_concealed_space_utility = weight_concealed_space_utility
        self.weight_empty_row_utility = weight_empty_row_utility
        self.weight_row_sum_utility = weight_row_sum_utility
        self.score_ = 0


    def fit(self, X, y=None):
        score = get_turns_alive_count(self.weight_concealed_space_utility, self.weight_empty_row_utility, self.weight_row_sum_utility)
        self.score_ = score
        return self

    def predict(self, X, y=None):
        return([self.score_ for x in X])

    def score(self, X, y=None):
        return(sum(self.predict(X))) 


def param_search(n_iter=20, concealed_util=RANGE_WEIGHT_CONCEALED_SPACE_UTILITY, empty_util=RANGE_WEIGHT_EMPTY_ROW_UTILITY, row_sum_util=RANGE_WEIGHT_ROW_SUM_UTILITY):
    gs = RandomizedSearchCV(
        GameClassifier(),
        dict(
            weight_concealed_space_utility=concealed_util,
            weight_empty_row_utility=empty_util,
            weight_row_sum_utility=row_sum_util,
        ),
        n_iter=n_iter,
    )

    gs.fit([1 for i in range(50)], y=[1 for i in range(50)])
    print(gs.best_params_)
    print(gs.best_score_)
    return gs.best_params_, gs.best_score_
