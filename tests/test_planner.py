# tests/test_planner.py
from restoration_graph import ACTIONS, START, GOAL, available_actions, apply_action
from planner import bfs_search

def is_valid_plan(plan, actions=ACTIONS):
    """A plan is valid if every action's prerequisites are satisfied by
    the actions before it, and every required action appears exactly once."""
    completed = set()
    for action in plan:
        if action in completed:
            return False          # duplicate action
        if not actions[action]["requires"].issubset(completed):
            return False          # prerequisite violated
        completed.add(action)
    return completed == set(actions.keys())


def test_finds_a_valid_plan():
    plan = bfs_search(START, GOAL, available_actions, apply_action)
    assert plan is not None
    assert is_valid_plan(plan)


def test_trivial_already_done():
    # start == goal: the plan should be empty, not None, not a crash
    plan = bfs_search(GOAL, GOAL, available_actions, apply_action)
    assert plan == []


def test_plan_has_no_duplicate_actions():
    plan = bfs_search(START, GOAL, available_actions, apply_action)
    assert len(plan) == len(set(plan))


def test_no_solution_returns_none():
    # a requires b and b requires a, but neither can ever become available,
    # so the goal is unreachable.
    bad_actions = {
        "a": {"requires": {"b"}, "cost": 1},
        "b": {"requires": {"a"}, "cost": 1},
    }

    def available(state):
        return [a for a, info in bad_actions.items()
                if a not in state and info["requires"].issubset(state)]

    def apply(state, action):
        return state | {action}

    result = bfs_search(frozenset(), frozenset(bad_actions.keys()), available, apply)
    assert result is None


def test_large_action_set_terminates():
    # 20 actions chained in a straight line: action i requires action i-1.
    big_actions = {
        f"a{i}": {"requires": {f"a{i - 1}"} if i else set(), "cost": 1}
        for i in range(20)
    }

    def available(state):
        return [a for a, info in big_actions.items()
                if a not in state and info["requires"].issubset(state)]

    def apply(state, action):
        return state | {action}

    plan = bfs_search(frozenset(), frozenset(big_actions.keys()), available, apply)
    assert plan is not None
    assert is_valid_plan(plan, actions=big_actions)