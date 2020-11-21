import numpy as np
from sklearn.metrics import make_scorer
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVR

from tetris.model.game import create_initial_state
from tetris.model.strategy import select_move


RANGE_WEIGHT_CONCEALED_SPACE_UTILITY = np.arange(0, 300, 1)
RANGE_WEIGHT_EMPTY_ROW_UTILITY = np.arange(0, 10, 0.01)
RANGE_WEIGHT_ROW_SUM_UTILITY = np.arange(0, 1, 0.000001)


def get_turns_alive_count(
    weight_concealed_space_utility,
    weight_empty_row_utility,
    weight_row_sum_utility,
):
    state = create_initial_state()
    move_count = 0

    while True:
        move = select_move(
            state,
            weight_concealed_space_utility=weight_concealed_space_utility,
            weight_empty_row_utility=weight_empty_row_utility,
            weight_row_sum_utility=weight_row_sum_utility,
        )
        if move:
            state = state.play_move()
            move_count += 1
        else:
            break

    return move_count


svr = GridSearchCV(
    estimator=SVR(),  # TODO
    scoring=get_turns_alive_count,
    param_grid=dict(
        weight_concealed_space_utility=RANGE_WEIGHT_CONCEALED_SPACE_UTILITY,
        weight_empty_row_utility=RANGE_WEIGHT_EMPTY_ROW_UTILITY,
        weight_row_sum_utility=RANGE_WEIGHT_ROW_SUM_UTILITY,
    ),
)
