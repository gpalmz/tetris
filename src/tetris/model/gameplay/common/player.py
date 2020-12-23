from abc import ABC, abstractmethod


class Player(ABC):
    @abstractmethod
    def get_move_obs(self, state, timer):
        pass