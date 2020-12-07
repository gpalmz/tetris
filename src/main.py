import click
from rx.subject import Subject

from tetris.model.game import create_initial_board, create_initial_state
from tetris.model.strategy import select_move_random, select_move_smart, get_complex_utility
from tetris.model.gameplay import SimplePlayer, MctsPlayer, InteractivePlayer
from tetris.model.task import TetrisMoveTask
from tetris.ui.game import GameDisplay, pygame_session


def run_game_gui(player, max_turn_duration, key_event_subject):
    GameDisplay(
        create_initial_board(), 
        player,
        turn_duration_sec=max_turn_duration,
        key_event_subject=key_event_subject,
    ).play_game()


# mostly for debugging
def run_game_stdout(player, max_turn_duration):

    def subscribe_to_move(state):
        move = None

        def set_move(new_move):
            nonlocal move
            if new_move and new_move != move:
                print(state.play_move(new_move).board)
            move = new_move

        def play_move():
            nonlocal state
            if move:
                state = state.play_move(move)
                subscribe_to_move(state)

        player.get_move_obs(state, TetrisMoveTask(max_turn_duration)).subscribe(
            on_next=set_move, on_completed=play_move,
        )

    subscribe_to_move(create_initial_state())


@click.command("run")
@click.option("--interface", type=click.Choice(["gui", "stdout"]), default="gui", help="The type of user interface to run tetris in. Only the GUI supports interactive play.")
@click.option("--player-type", type=click.Choice(["interactive", "simple", "mcts"]), default="interactive", help="The type of player to use; interactive lets you play.")
@click.option("--max-turn-duration", default=1000, help="Maximum duration of each turn in seconds.")
@click.option("--mcts-playout-policy", type=click.Choice(["random", "smart"]), default="smart", help="The manner of selecting moves during MCTS playout.")
@click.option("--mcts-playout-depth", default=1000, help="Max playout depth.")
def run_game(interface, player_type, max_turn_duration, mcts_playout_policy, mcts_playout_depth):
    with pygame_session():
        key_event_subject = Subject()
        if player_type == "interactive":
            if interface != "gui":
                raise ValueError("Interactive play only supported in GUI.")
            else:
                player = InteractivePlayer(key_event_subject)
        elif player_type == "simple":
            player = SimplePlayer()
        else:
            if mcts_playout_policy == "random":
                player_select_move = select_move_random
            else:
                player_select_move = select_move_smart
            player = MctsPlayer(
                select_move=player_select_move, 
                get_utility=get_complex_utility,
                max_playout_depth=mcts_playout_depth,
            )

        if interface == "gui":
            run_game_gui(player, max_turn_duration, key_event_subject)
        else:
            run_game_stdout(player, max_turn_duration)


if __name__ == "__main__":
    run_game()