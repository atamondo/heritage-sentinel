import subprocess, sys
from csp import backtracking_search
from restoration_csp import VARIABLES, DOMAINS, build_constraints
from test_planner import is_valid_plan

def solve(seed=0, cap=4, all_solutions=False):
    return backtracking_search(VARIABLES, DOMAINS, build_constraints(tranche_cap=cap),
                               seed=seed, all_solutions=all_solutions)

def to_plan(assignment):
    return sorted(assignment, key=assignment.get)

def test_solution_is_valid():
    plan = to_plan(solve()[0])
    assert is_valid_plan(plan, tranche_cap=4)

def test_same_seed_same_plan():
    assert solve(seed=7) == solve(seed=7)

def test_solution_counts():
    expected = {4: 5, 3: 1, 2: 0}
    for cap, count in expected.items():
        assert len(solve(cap=cap, all_solutions=True)) == count, f"cap={cap}"

def test_old_oracle_gap_is_closed():
    bad = ["stabilize_base", "seal_crack", "clean_surface", "restore_pigment"]
    assert not is_valid_plan(bad, tranche_cap=4)

def test_reproducible_across_processes():
    cmd = [sys.executable, "src/main_csp.py"]
    out1 = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    out2 = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    assert out1 == out2