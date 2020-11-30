from tetris.model.game import create_initial_board
from tetris.model.mcts import TetrisMctsPlayer
from tetris.ui.game import GameDisplay, pygame_session
from tetris.model.hyperparameters import parameter_search
from tetris.model.strategy import SimplePlayer
import click


@click.command()
@click.option("--param-search", is_flag=True, help="Whether to run hyperparameter optimization.")
@click.option("--param-search-iter", default=20, help="Number of iterations of random hyperparameter search; larger values will return more accurate yet slower results.")
@click.option("--param-search-samples", default=50, help="Number of samples tried per each hyperparameter set; larger values will return more accurate yet slower results. Must be greater than 5.")
@click.option("--max-playout-depth", default=1000, help="Max playout depth.")
@click.option("--turn-duration", default=1000, help="Duration of each turn in seconds.")
@click.option("--interactive-player", is_flag=True, help="run with interactive player rather than have mcts simulated.")
def demo_game(param_search, param_search_iter, param_search_samples, max_playout_depth, turn_duration, interactive_player):

    player = SimplePlayer()
    if not interactive_player:
        player = TetrisMctsPlayer(max_playout_depth=max_playout_depth)

    if param_search:
        best_params, _ = parameter_search(param_search_iter, param_search_samples)
        player = TetrisMctsPlayer(
            lambda moves: select_move(
                state,
                weight_row_sum_utility=best_params['weight_row_sum_utility'],
                weight_empty_row_utility=best_params['weight_empty_row_utility'],
                weight_concealed_space_utility=best_params['weight_concealed_space_utility']
            ))

    with pygame_session():
        GameDisplay(
            create_initial_board(), 
            player,
            turn_duration_sec=turn_duration,
        ).play_game()

if __name__ == '__main__':
    demo_game()