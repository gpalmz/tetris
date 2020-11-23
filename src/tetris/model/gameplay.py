from abc import ABC, abstractmethod
from dataclasses import dataclass


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, task):
        pass


# TODO: store a real countdown timer, set it running on separate thread when 
# the task is started. player loses if it doesn't provide a move in time.
@dataclass
class MoveTimer:
    time: int

    @property
    def time_remaining(self):
        t = self.time
        if t > 0:
            self.time -= 1
        return t

    def start(self):
        pass