import json, random
import pytest
import validate as validate_module
from logic import forward_chain, explain
from report_rules import CLAUSES
from validate import validate, to_facts

def load(path="data/reports.jsonl"):
    with open(path) as f:
        return {r["id"]: r for r in map(json.loads, f)}

REPORTS = load()

def test_chain_derives_transitively():
    known, _ = forward_chain({"a"}, [(frozenset({"a"}), "b"), (frozenset({"b"}), "c")])
    assert known == {"a", "b", "c"}

def test_cycle_terminates():
    # a -> b and b -> a. Once both are known, a pass adds nothing and the
    # loop must exit. A wrong loop condition hangs here instead of failing.
    clauses = [(frozenset({"a"}), "b"), (frozenset({"b"}), "a")]
    known, why = forward_chain({"a"}, clauses)
    assert known == {"a", "b"}
    assert why["a"] is None                 # "a" was given, never derived
    assert why["b"] == frozenset({"a"})

def test_clause_order_irrelevant():
    facts = to_facts(REPORTS["r9"])
    expected, _ = forward_chain(facts, CLAUSES)
    for seed in range(20):
        shuffled = CLAUSES[:]
        random.Random(seed).shuffle(shuffled)
        got, _ = forward_chain(facts, shuffled)
        assert got == expected

@pytest.mark.parametrize("rid", ["r1", "r3", "r5", "r7"])
def test_valid_reports_accepted(rid):
    ok, reasons, _ = validate(REPORTS[rid])
    assert ok and reasons == []

@pytest.mark.parametrize("rid,reason", [
    ("r2", "invalid:structural_risk_marked_minor"),
    ("r4", "invalid:rot_on_inorganic"),
    ("r6", "invalid:corrosion_on_organic"),
    ("r8", "invalid:none_but_damaged"),
])
def test_each_rule_fires_alone(rid, reason):
    ok, reasons, _ = validate(REPORTS[rid])
    assert not ok and reasons == [reason]

def test_multiple_violations_all_reported():
    # r9 has rot on stone AND crack + loose_base marked minor.
    ok, reasons, _ = validate(REPORTS["r9"])
    expected = [
        "invalid:rot_on_inorganic",
        "invalid:structural_risk_marked_minor",
    ]
    assert not ok
    assert reasons == expected              # both present, no extras
    assert reasons == sorted(reasons)       # and in sorted order

@pytest.mark.parametrize("rid,frag", [("r10", "missing field"), ("r11", "unknown material")])
def test_schema_errors_are_not_logic_errors(rid, frag):
    ok, reasons, proofs = validate(REPORTS[rid])
    assert not ok and reasons[0].startswith("schema:") and frag in reasons[0] and proofs == {}

def test_proofs_bottom_out_in_given_facts():
    ok, reasons, proofs = validate(REPORTS["r2"])
    assert not ok
    lines = proofs["invalid:structural_risk_marked_minor"]
    assert lines[0].endswith("because:")    # the root is a derived conclusion
    leaves = [ln for ln in lines if "because" not in ln]
    assert len(leaves) >= 1
    assert all("(given)" in ln for ln in leaves)

def test_deleting_a_rule_is_caught():
    # Part 1: with the rot_on_inorganic rule removed, r4 is WRONGLY accepted.
    target = "invalid:rot_on_inorganic"
    original = validate_module.CLAUSES
    reduced = [c for c in original if c[1] != target]
    assert len(reduced) < len(original)     # the rule really was removed
    try:
        validate_module.CLAUSES = reduced
        ok, reasons, _ = validate(REPORTS["r4"])
        assert ok and reasons == []         # the bug the rule exists to catch
    finally:
        validate_module.CLAUSES = original

    # Part 2: rules restored, r4 is rejected again. This is exactly what
    # test_each_rule_fires_alone[r4] asserts, so that test would fail
    # if the rule were ever deleted.
    ok, reasons, _ = validate(REPORTS["r4"])
    assert not ok and reasons == [target]

# part E: own rules tests
MY_RULES = [
    ("r12", "invalid:loose_base_on_textile"),
    ("r15", "invalid:fiber_failure_marked_minor"),
]
 
@pytest.mark.parametrize("rid,reason", MY_RULES)
def test_my_rules_fire_alone(rid, reason):
    ok, reasons, _ = validate(REPORTS[rid])
    assert not ok and reasons == [reason]
 
@pytest.mark.parametrize("rid", [
    "r13",  # loose_base_on_textile near-miss: same damage, but stone has a base
    "r14",  # loose_base_on_textile near-miss: textile, but fading is not loose_base
    "r16",  # fiber_failure_marked_minor near-miss: rot + crack in wood, but major
    "r17",  # fiber_failure_marked_minor near-miss: minor wood, but no rot
])
def test_my_rules_near_misses_accepted(rid):
    ok, reasons, _ = validate(REPORTS[rid])
    assert ok and reasons == []
 
@pytest.mark.parametrize("rid,reason", MY_RULES)
def test_deleting_my_rule_is_caught(rid, reason):
    original = validate_module.CLAUSES
    reduced = [c for c in original if c[1] != reason]
    assert len(reduced) < len(original)
    try:
        validate_module.CLAUSES = reduced
        ok, reasons, _ = validate(REPORTS[rid])
        assert ok and reasons == []         # wrongly accepted without the rule
    finally:
        validate_module.CLAUSES = original
    ok, reasons, _ = validate(REPORTS[rid])
    assert not ok and reasons == [reason]