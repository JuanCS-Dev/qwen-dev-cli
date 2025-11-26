"""
planner/goap.py: Goal-Oriented Action Planning System.

Implements GOAP (Goal-Oriented Action Planning) using A* pathfinding.
Based on F.E.A.R. AI system by Jeff Orkin (2006).

Classes:
- WorldState: Current state of the environment
- GoalState: Desired end state
- Action: Atomic unit with preconditions and effects
- GOAPPlanner: A* planner for finding optimal action sequences
"""

from __future__ import annotations

import heapq
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class WorldState:
    """
    GOAP-inspired world state tracking.
    Represents the current state of the development environment.
    """
    facts: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, int] = field(default_factory=dict)

    def satisfies(self, goal: GoalState) -> bool:
        """Check if current state satisfies goal."""
        for key, value in goal.desired_facts.items():
            if key not in self.facts or self.facts[key] != value:
                return False
        return True

    def distance_to(self, goal: GoalState) -> float:
        """Calculate heuristic distance to goal (for A*)."""
        distance = 0.0
        for key, value in goal.desired_facts.items():
            if key not in self.facts:
                distance += 1.0
            elif self.facts[key] != value:
                distance += 0.5
        return distance

    def copy(self) -> WorldState:
        """Create a copy of this state."""
        return WorldState(
            facts=self.facts.copy(),
            resources=self.resources.copy()
        )


@dataclass
class GoalState:
    """Desired end state for GOAP planning."""
    name: str
    desired_facts: Dict[str, Any]
    priority: float = 1.0  # Weight for multi-goal scenarios


@dataclass
class Action:
    """
    GOAP Action with preconditions and effects.
    Atomic unit of work for an agent.
    """
    id: str
    agent_role: str
    description: str
    preconditions: Dict[str, Any]  # Required world state
    effects: Dict[str, Any]        # Changes to world state
    cost: float = 1.0              # For path optimization
    duration_estimate: str = "5m"

    def can_execute(self, state: WorldState) -> bool:
        """Check if preconditions are met."""
        for key, value in self.preconditions.items():
            if key not in state.facts or state.facts[key] != value:
                return False
        return True

    def apply(self, state: WorldState) -> WorldState:
        """Apply effects to world state, returns new state."""
        new_state = state.copy()
        new_state.facts.update(self.effects)
        return new_state


class GOAPPlanner:
    """
    Goal-Oriented Action Planner using A* pathfinding.
    Finds optimal sequence of actions to reach goal state.

    Based on F.E.A.R. AI system by Jeff Orkin (2006).

    Example:
        actions = [
            Action("read", "explorer", "Read file", {"file_known": False}, {"file_known": True}),
            Action("edit", "editor", "Edit file", {"file_known": True}, {"file_edited": True}),
        ]
        planner = GOAPPlanner(actions)

        initial = WorldState(facts={"file_known": False})
        goal = GoalState("edit_complete", {"file_edited": True})

        plan = planner.plan(initial, goal)
        # Returns: [Action("read"), Action("edit")]
    """

    def __init__(self, actions: List[Action]):
        self.actions = actions

    def plan(
        self,
        initial_state: WorldState,
        goal: GoalState,
        max_depth: int = 20
    ) -> Optional[List[Action]]:
        """
        Find optimal action sequence using A* algorithm.

        Args:
            initial_state: Starting world state
            goal: Desired goal state
            max_depth: Maximum search depth

        Returns:
            List of actions to execute, or None if no plan found
        """
        # Priority queue: (f_score, counter, g_score, state, path)
        # counter breaks ties for equal f_scores
        counter = 0
        frontier = [(0.0, counter, 0.0, initial_state, [])]
        explored: Set[str] = set()

        while frontier:
            f_score, _, g_score, current_state, path = heapq.heappop(frontier)

            # Check if we've reached the goal
            if current_state.satisfies(goal):
                return path

            # Depth limit
            if len(path) >= max_depth:
                continue

            # Skip if already explored
            state_hash = self._hash_state(current_state)
            if state_hash in explored:
                continue
            explored.add(state_hash)

            # Explore neighbors (applicable actions)
            for action in self.actions:
                if not action.can_execute(current_state):
                    continue

                # Apply action
                new_state = action.apply(current_state)
                new_path = path + [action]

                # Calculate scores
                new_g_score = g_score + action.cost
                h_score = new_state.distance_to(goal)
                new_f_score = new_g_score + h_score

                counter += 1
                heapq.heappush(
                    frontier,
                    (new_f_score, counter, new_g_score, new_state, new_path)
                )

        return None  # No plan found

    def _hash_state(self, state: WorldState) -> str:
        """Create hashable representation of state."""
        return json.dumps(state.facts, sort_keys=True)

    def get_applicable_actions(self, state: WorldState) -> List[Action]:
        """Get all actions that can be executed in current state."""
        return [a for a in self.actions if a.can_execute(state)]

    def validate_plan(self, plan: List[Action], initial_state: WorldState, goal: GoalState) -> bool:
        """Validate that a plan reaches the goal from initial state."""
        current = initial_state
        for action in plan:
            if not action.can_execute(current):
                return False
            current = action.apply(current)
        return current.satisfies(goal)
