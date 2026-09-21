# toy.py — problem definition only.
# planner.py must not know anything specific to this file.

ACTIONS = {
    "apples": {"requires": set(), "cost": 2},
    "apple_pie": {"requires": {"apples"}, "cost": 5},
    "gasoline": {"requires": set(), "cost": 6.67},
    "car": {"requires": {"gasoline"}, "cost": 10},
}

GOAL = frozenset(ACTIONS.keys())
START = frozenset()

def available_actions(state):
    """Actions whose prerequisites are satisfied and not already done."""
    return [a for a, info in ACTIONS.items()
            if a not in state and info["requires"].issubset(state)]

def apply_action(state, action):
    return state | {action}