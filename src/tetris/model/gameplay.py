from abc import ABC, abstractmethod
from dataclasses import dataclass


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, task):
        pass


# surprise!!! this is a fake timer
# fight me
@dataclass
class MoveTimer:
    time: int

    @property
    def time_remaining(self):
        t = self.time
        if t > 0:
            self.time -= 1
        return t
