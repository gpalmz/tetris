import click

from tetris.model.game import create_initial_board, create_initial_state
from tetris.model.mcts import TetrisMctsPlayer
from tetris.model.hyperparameters import tune_move_selector
from tetris.model.strategy import select_move_random, select_move_smart, SimplePlayer
from tetris.model.gameplay import MoveTimer
from tetris.ui.game import GameDisplay, pygame_session


def run_game_gui(player, max_turn_duration):
    GameDisplay(
        create_initial_board(), 
        player,
        turn_duration_sec=max_turn_duration,
    ).play_game()


def run_game_stdout(player, max_turn_duration):

    def subscribe_to_move(state):
        move = None

        def set_move(new_move):
            nonlocal move
            if new_move and new_move != move:
                # TODO: make this fancier
                print(state.play_move(new_move).board)
            move = new_move

        def play_move():
            nonlocal state
            if move:
                state = state.play_move(move)
                subscribe_to_move(state)

        player.get_move_obs(state, MoveTimer(max_turn_duration)).subscribe(
            on_next=set_move, on_completed=play_move,
        )

    subscribe_to_move(create_initial_state())


@click.command()
@click.option("--interface", type=click.Choice(["gui", "stdout"]), default="gui", help="The type of user interface to run tetris in. Only the GUI supports interactive play.")
@click.option("--player-type", type=click.Choice(["interactive", "simple", "mcts"]), default="interactive", help="The type of player to use; interactive lets you play.")
@click.option("--max-turn-duration", default=1000, help="Maximum duration of each turn in seconds.")
@click.option("--mcts-playout-policy", type=click.Choice(["random", "smart"]), default="smart", help="The manner of selecting moves during MCTS playout.")
@click.option("--mcts-playout-depth", default=1000, help="Max playout depth.")
@click.option("--tune-hyperparam", is_flag=True, help="Whether to run hyperparameter optimization.")
@click.option("--tune-hyperparam-iter", default=20, help="Number of iterations of random hyperparameter search; larger values will return more accurate yet slower results.")
@click.option("--tune-hyperparam-samples", default=50, help="Number of samples tried per each hyperparameter set; larger values will return more accurate yet slower results. Must be greater than 5.")
def demo_game(interface, player_type, max_turn_duration, mcts_playout_policy, mcts_playout_depth, tune_hyperparam, tune_hyperparam_iter, tune_hyperparam_samples):
    with pygame_session():
        if player_type == "interactive":
            if interface != "gui":
                raise ValueError("Interactive play only supported in GUI.")
            else:
                player = SimplePlayer()  # TODO: create interactive player
        elif player_type == "simple":
            player = SimplePlayer()
        else:
            if mcts_playout_policy == "random":
                player_select_move = select_move_random
            else:
                if tune_hyperparam:
                    player_select_move = tune_move_selector(
                        tune_hyperparam_iter, tune_hyperparam_samples,
                    )
                else:
                    player_select_move = select_move_smart
            player = TetrisMctsPlayer(
                select_move=player_select_move, max_playout_depth=mcts_playout_depth,
            )

        if interface == "gui":
            run_game_gui(player, max_turn_duration)
        else:
            run_game_stdout(player, max_turn_duration)


if __name__ == "__main__":
    demo_game()