from abc import ABC, abstractmethod
from dataclasses import dataclass


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, task):
        pass


# TODO: store a countdown timer, set it running on separate thread when the
# task is started. player loses if it doesn't provide a move in time.
@dataclass
class MoveTimer:
    @property
    def time_remaining(self):
        return 1

    def start(self):
        pass