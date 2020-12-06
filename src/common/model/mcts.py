import math
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional, Dict

from common.model.task import Task, TaskState

# TODO: fuck around with this
UCT_C = math.sqrt(2)


def get_selection_value_uct(node: "TaskNode"):
    n = node.playout_count
    u = node.playout_utility_sum
    # TODO: is this the correct handling when no parent?
    parent_n = node.parent.playout_count if node.parent else 0
    return u / n + UCT_C * math.sqrt(math.log(parent_n) / n)


@dataclass
class TaskNode(ABC):
    state: TaskState
    # The number of playouts going through this node.
    playout_count: int = 0
    # The sum of the utilities of playouts going through this node.
    playout_utility_sum: float = 0
    parent: Optional["TaskNode"] = None
    action_to_child: Dict["Action", "TaskNode"] = field(default_factory=lambda: {})

    @property
    def children(self):
        return self.action_to_child.values()

    @property
    def possible_actions(self):
        return self.state.possible_actions

    @property
    def explored_actions(self):
        return self.action_to_child.keys()

    @property
    def unexplored_actions(self):
        explored_actions = set(self.explored_actions)
        return [a for a in self.possible_actions if a not in explored_actions]

    def select(self, get_value):
        # if we don't have a child for every possible action, select this node
        if not self.possible_actions or len(self.explored_actions) < len(self.possible_actions):
            return self
        else:
            return max(self.children, key=get_value).select(get_value)

    def back_propagate(self, playout_utility):
        self.playout_count += 1
        self.playout_utility_sum += playout_utility

        if self.parent:
            self.parent.back_propagate(playout_utility)

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

    def mcts(
        self,
        task: Task, 
        get_node_selection_value=get_selection_value_uct,
        max_playout_depth=None,
    ):
        """Run the Monte Carlo Tree Search algorithm to determine the best action 
        at a given state.

        :param get_node_selection_value: A function used to determine the value 
        of a node in the selection phase of the algorithm."""

        while task.time_remaining:
            selected_node = self.select(get_node_selection_value)
            if not selected_node.possible_actions:
                # impossible to expand a terminal node; no possible actions
                break
            else:
                child = selected_node.expand()
                child.back_propagate(child.simulate(max_playout_depth=max_playout_depth))
                # at each iteration we yield the best action so far
                yield max(self.action_to_child.items(), key=lambda e: e[1].playout_count)[0]
