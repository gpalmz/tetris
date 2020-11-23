import copy
import math
from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractproperty
from typing import Optional, Dict

from common.util.iter import max_by


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

    # TODO: rename to possible_actions?
    @abstractproperty
    def actions(self):
        pass

    @abstractmethod
    def perform_action(self, action):
        pass


@dataclass
class TaskNode(ABC):
    state: TaskState
    # The number of playouts going through this node.
    playout_count: int = 0
    # The sum of the utilities of playouts going through this node.
    playout_utility_sum: float = 0
    parent: Optional['TaskNode'] = None
    action_to_child: Dict['Action', 'TaskNode'] = {}  # TODO: add action type?

    @property
    def children(self):
        return self.action_to_child.values()

    @property
    def explored_actions(self):
        return self.action_to_child.keys()

    def select(self, get_value):
        # if we don't have a child for every possible action, select this node
        if not len(self.explored_actions) == len(self.state.actions):
            return self
        else:
            return max_by(self.children, get=get_value).select(get_value)

    def back_propagate(self, result):
        self.playout_count += 1
        self.playout_utility_sum += result

        if self.parent:
            self.parent.back_propagate(result)

    @abstractmethod
    def expand(self):
        """Add a child node."""
        pass

    @abstractmethod
    def simulate(self):
        """Run a semi-random playout from the current state, returning a number
        indicating how successful the playout was.

        Do not store the resulting playout tree."""
        pass


# TODO: fuck around with this
UCB_C = math.sqrt(2)


def get_selection_value_ucb(node: TaskNode):
    n = node.playout_count
    u = node.playout_utility_sum
    # TODO: is this the correct handling when no parent?
    parent_n = node.parent.playout_count if node.parent else 0
    return u / n + UCB_C * math.sqrt(math.log(parent_n) / n)


def mcts(task, tree, get_node_selection_value=get_selection_value_ucb):
    """Run the Monte Carlo Tree Search algorithm to determine the best action 
    at a given state.

    :param get_node_selection_value: A function used to determine the value 
    of a node in the selection phase of the algorithm."""

    while task.time_remaining:
        child = tree.select(get_node_selection_value).expand()
        child.back_propagate(child.simulate())

        # at each iteration we yield the best action so far
        yield max_by(tree.child_by_action.items(), get=lambda e: e[1].playout_count)[0]
