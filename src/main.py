from tetris.model.game import create_initial_board
from tetris.model.mcts import TetrisMctsPlayer
from tetris.ui.game import GameDisplay, pygame_session
from tetris.model.hyperparameters import parameter_search
import click


@click.command()
@click.option("--param-search", is_flag=True, help="Whether to run hyperparameter optimization.")
@click.option("--param-search-iter", default=20, help="Number of iterations of random hyperparameter search; larger values will return more accurate yet slower results.")
@click.option("--param-search-samples", default=50, help="Number of samples tried per each hyperparameter set; larger values will return more accurate yet slower results. Must be greater than 5.")
@click.option("--max-playout-depth", default=1000, help="Max playout depth.")
@click.option("--turn_duration", default=1000, help="Duration of each turn in seconds.")
def demo_game(param_search, param_search_iter, param_search_samples, max_playout_depth, turn_duration):

    if param_search:
        parameter_search(param_search_iter, param_search_samples)

    ## TODO: set hyperparameters
    with pygame_session():
        GameDisplay(
            create_initial_board(), 
            TetrisMctsPlayer(max_playout_depth=max_playout_depth), 
            turn_duration_sec=turn_duration,
        ).play_game()

if __name__ == '__main__':
    demo_game()