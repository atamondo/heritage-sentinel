# restoration_csp.py — problem definition only.
from restoration_graph import ACTIONS      # reuse the Lab 1 data

VARIABLES = list(ACTIONS.keys())           # a list, not a set. Remember this.
DOMAINS = {a: list(range(1, len(VARIABLES) + 1)) for a in VARIABLES}

def build_constraints(actions=ACTIONS, tranche_cap=4):
    constraints = []

    # 1. all-different
    for i, a in enumerate(VARIABLES):
        for b in VARIABLES[i + 1:]:
            constraints.append(((a, b), lambda x, y: x != y))

    # 2. prerequisites
    for action, info in actions.items():
        for req in info["requires"]:
            constraints.append(((req, action), lambda r, a: r < a))

    # 3. tranche rule
    scope = tuple(VARIABLES)
    costs = [actions[v]["cost"] for v in VARIABLES]

    def tranche_check(*slots):
        total = sum(c for c, s in zip(costs, slots) if s <= 2)
        return total <= tranche_cap

    constraints.append((scope, tranche_check))

    return constraints