import copy
import math
from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractproperty
from typing import Optional


@dataclass
class Task(ABC):
    @abstractproperty
    def time_remaining(self):
        pass


@dataclass
class TaskState(ABC):
    @abstractproperty
    def is_terminal(self):
        pass

    @abstractproperty
    def actions(self):
        pass

    @abstractmethod
    def perform_action(self, action):
        pass


# TODO: fuck around with this
UCB_C = math.sqrt(2)


def get_value_ucb(node):
    u = node.playout_utility_sum
    n = node.playout_count
    # TODO: is this the correct handling when no parent?
    parent_n = node.parent.playout_count if node.parent else 0
    return u / n + UCB_C * math.sqrt(math.log(parent_n) / n)


@dataclass
class TaskNode(TaskState, ABC):
    state: TaskState
    parent: Optional['TaskNode']

    def is_terminal(self):
        return self.state.is_terminal

    def actions(self):
        return self.state.actions

    def perform_action(self, action):
        child = copy.deepcopy(self)
        child.state = self.state.perform_action(action)
        child.parent = self
        return child

    @abstractproperty
    def playout_utility_sum(self):
        """The sum of the utilities of playouts going through this node."""
        pass

    @abstractproperty
    def playout_count(self):
        """The number of playouts going through this node."""
        pass

    @abstractmethod
    def select_leaf(self):
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def simulate(self):
        # explore playouts stemming from the current state
        pass

    @abstractmethod
    def back_propagate(self, result):
        pass


def mcts(task, state, create_node):
    tree = create_node(state)

    while task.time_remaining:
        leaf = tree.select_leaf()
        child = leaf.expand()
        result = child.simulate()
        child.back_propagate(result)

    max_success_count = 0
    best_action = None
    for action in state.actions:
        success_count = state.perform_action(action).success_count
        if success_count > max_success_count:
            max_success_count = success_count
            best_action = action

    return best_action
