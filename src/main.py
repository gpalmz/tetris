from tetris.model.game import create_initial_board
from tetris.model.mcts import TetrisMctsPlayer
from tetris.ui.game import GameDisplay, pygame_session


def demo_game_ui():
    with pygame_session():
        GameDisplay(
            create_initial_board(), 
            TetrisMctsPlayer(max_playout_depth=1000), 
            turn_duration_sec=1000,
        ).play_game()


demo_game_ui()

# from tetris.model.hyperparameters import param_search

# param_search()
