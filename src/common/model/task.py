import random
from dataclasses import dataclass
from abc import ABC, abstractproperty, abstractmethod

from common.util.iter import group


@dataclass
class Task(ABC):
    @abstractproperty
    def time_remaining(self):
        pass


@dataclass
class TaskState(ABC):
    @abstractproperty
    def possible_actions(self):
        pass

    @abstractmethod
    def perform_action(self, action):
        pass


def create_select_action_by_utility(get_utility):
    """Given a state utility estimator function, create a function that 
    selects the best move given a state and possible moves.
    
    If there is a tie, select one of the tied actions at random."""

    def select_move_by_utility(state, possible_actions):
        return random.choice(
            max(
                group(
                    [
                        (action, get_utility(state.perform_action(action)))
                        for action in possible_actions
                    ], 
                    get_key=lambda item: item[1],  # group actions by utility
                ).items(),
                key=lambda item: item[0],  # get the group with the best utility
            )[1]  # pick a random action from that group
        )[0] if possible_actions else None
    
    return select_move_by_utility