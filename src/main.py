import click

from tetris.model.game import create_initial_board
from tetris.model.mcts import TetrisMctsPlayer, select_random_move
from tetris.ui.game import GameDisplay, pygame_session
from tetris.model.hyperparameters import parameter_search
from tetris.model.strategy import SimplePlayer, select_move


@click.command()
@click.option("--player-type", type=click.Choice(["interactive", "simple", "mcts"]), default="interactive", help="The type of player to use; interactive lets you play.")
@click.option("--max-turn-duration", default=1000, help="Maximum duration of each turn in seconds.")
@click.option("--mcts-playout-policy", type=click.Choice(["random", "smart"]), default="smart", help="The manner of selecting moves during MCTS playout.")
@click.option("--mcts-playout-depth", default=1000, help="Max playout depth.")
@click.option("--tune-hyperparam", is_flag=True, help="Whether to run hyperparameter optimization.")
@click.option("--tune-hyperparam-iter", default=20, help="Number of iterations of random hyperparameter search; larger values will return more accurate yet slower results.")
@click.option("--tune-hyperparam-samples", default=50, help="Number of samples tried per each hyperparameter set; larger values will return more accurate yet slower results. Must be greater than 5.")
def demo_game(player_type, max_turn_duration, mcts_playout_policy, mcts_playout_depth, tune_hyperparam, tune_hyperparam_iter, tune_hyperparam_samples):
    with pygame_session():
        if player_type == "interactive":
            player = SimplePlayer()  # TODO: create interactive player
        elif player_type == "simple":
            player = SimplePlayer()
        else:
            if mcts_playout_policy == "random":
                player_select_move = select_random_move
            else:
                if tune_hyperparam:
                    best_params, _ = parameter_search(
                        tune_hyperparam_iter, tune_hyperparam_samples,
                    )
                    player_select_move = lambda state: select_move(
                        state,
                        weight_row_sum_utility=best_params["weight_row_sum_utility"],
                        weight_empty_row_utility=best_params["weight_empty_row_utility"],
                        weight_concealed_space_utility=best_params["weight_concealed_space_utility"],
                    )
                else:
                    player_select_move = select_move
            player = TetrisMctsPlayer(
                select_move=player_select_move, max_playout_depth=mcts_playout_depth,
            )

        GameDisplay(
            create_initial_board(), 
            player,
            turn_duration_sec=max_turn_duration,
        ).play_game()


if __name__ == "__main__":
    demo_game()