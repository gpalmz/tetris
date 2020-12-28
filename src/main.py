import click
from rx.subject import Subject

from common.util.concurrency import rx_background_scheduler
from tetris.model.strategy import select_move_random, select_move_smart, get_complex_utility
from tetris.model.gameplay.player.simple import SimplePlayer
from tetris.model.gameplay.player.mcts import MctsPlayer
from tetris.model.gameplay.player.interactive import InteractivePlayer
from tetris.model.gameplay.common.conductor import GameConductor
from tetris.ui.game import GameDisplay, pygame_session


@click.command()
@click.option("--player-type", type=click.Choice(["interactive", "simple", "mcts"]), default="interactive", help="The type of player to use; interactive lets you play.")
@click.option("--max-turn-duration", default=300, help="Maximum duration of each turn in seconds.")
@click.option("--mcts-playout-policy", type=click.Choice(["random", "smart"]), default="smart", help="The manner of selecting moves during MCTS playout.")
@click.option("--mcts-playout-depth", default=10, help="Max playout depth.")
def run_game(player_type, max_turn_duration, mcts_playout_policy, mcts_playout_depth):
    key_event_subject = Subject()

    if player_type == "interactive":
        player = InteractivePlayer(key_event_subject)
    elif player_type == "simple":
        player = SimplePlayer()
    else:
        if mcts_playout_policy == "random":
            select_move = select_move_random
        else:
            select_move = select_move_smart
        player = MctsPlayer(
            select_move=select_move, 
            get_utility=get_complex_utility,
            max_playout_depth=mcts_playout_depth,
        )

    with pygame_session():
        GameDisplay(
            GameConductor(
                player, 
                max_turn_duration,
                scheduler=rx_background_scheduler,
            ),
            key_event_subject=key_event_subject,
        ).run_game()


if __name__ == "__main__":
    run_game()