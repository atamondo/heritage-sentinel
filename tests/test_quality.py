import hashlib, json, os, subprocess, sys, tempfile
import pytest
import make_data
from quality import load, classify, run, batch_drift
from report_model import ReportModel, calibrate
from validate import validate

REF = load("data/reference.jsonl")
MODEL = ReportModel(REF)
THRESHOLD = calibrate(MODEL, REF, 0.02)

def by_id(path):
    return {r["id"]: r for r in load(path)}

A = by_id("data/incoming_a.jsonl")

def test_reference_data_passes_the_logic_gate():
    # Your "trusted" data must itself obey the Lab 4 rules.
    assert all(validate(r)[0] for r in REF)

def test_calibration_flags_about_two_percent_of_reference():
    flagged = sum(MODEL.log_likelihood(r) < THRESHOLD for r in REF)
    assert 7 <= flagged <= 9          # 2% of 400 = 8, allow +/-1 for percentile conventions

@pytest.mark.parametrize("rid", ["a-odd1", "a-odd2", "a-odd3"])
def test_logic_valid_but_improbable_is_quarantined(rid):
    assert validate(A[rid])[0]                       # Lab 4 alone would accept it
    verdict, detail = classify(A[rid], MODEL, THRESHOLD)
    assert verdict == "quarantine" and "improbable" in detail[0]

@pytest.mark.parametrize("rid", ["a-bad1", "a-bad2"])
def test_impossible_is_rejected_not_quarantined(rid):
    verdict, _ = classify(A[rid], MODEL, THRESHOLD)
    assert verdict == "reject"

def test_unseen_combination_scores_finite():
    ll = MODEL.log_likelihood(A["a-odd1"])           # stone + corrosion never occurs in reference
    assert ll == ll and ll > -100                    # not NaN, not -inf

def test_without_smoothing_unseen_combination_blows_up():
    raw = ReportModel(REF, alpha=0.0)                 # no smoothing
    with pytest.raises(ValueError):                   # math.log(0) -> "math domain error"
        raw.log_likelihood(A["a-odd1"])               # stone + corrosion never occurs in REF

def test_batch_a_summary():
    res = run("data/incoming_a.jsonl")
    assert res["summary"] == {"accept": 100, "quarantine": 3, "reject": 2}
    assert res["drift"]["material_mix"][2] is False

def test_drifted_batch_passes_every_record_check_but_fails_the_batch_check():
    res = run("data/incoming_b.jsonl")
    # (1) every report is individually fine: nothing rejected, nothing quarantined
    assert res["summary"] == {"accept": 100}
    # (2) yet the batch-level check fires
    stat, crit, drifted = res["drift"]["material_mix"]
    assert drifted is True
    assert stat > crit

def test_heldout_quarantine_rate_is_near_target():
    below = total = 0
    for seed in range(100, 120):
        for r in make_data.make_batch(seed, 100, "h", make_data.MATERIAL_P):
            total += 1
            below += MODEL.log_likelihood(r) < THRESHOLD
    assert total == 2000
    rate = below / total
    assert 0.005 <= rate <= 0.04

def test_clean_batches_rarely_raise_drift_alarms():
    alarms = sum(
        batch_drift(make_data.make_batch(s, 100, "c", make_data.MATERIAL_P), MODEL)["material_mix"][2]
        for s in range(100, 150))
    assert alarms <= 1

def test_data_generation_is_deterministic():
    def digests(directory):
        out = {}
        for name in sorted(os.listdir(directory)):
            with open(os.path.join(directory, name), "rb") as f:
                out[name] = hashlib.sha256(f.read()).hexdigest()
        return out

    results = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([sys.executable, "tools/make_data.py", d], check=True)
            results.append(digests(d))
    assert results[0]                                 # something was actually written
    assert results[0] == results[1]

def test_pipeline_output_is_reproducible_across_processes():
    runs = [subprocess.run([sys.executable, "src/quality.py", "data/incoming_a.jsonl",
                            os.devnull], capture_output=True, text=True, check=True).stdout
            for _ in range(2)]
    assert runs[0] == runs[1]

# Part E - Lab 5
def test_severity_drift_fires_when_only_severity_shifts():
    batch = make_data.make_batch(100, 100, "s", make_data.MATERIAL_P)
    rare = min(MODEL.p_severity_mix, key=MODEL.p_severity_mix.get)   # least common severity
    drifted = [dict(r, severity=rare) if i < 60 else r for i, r in enumerate(batch)]
    res = batch_drift(drifted, MODEL)
    assert res["severity_mix"][2] is True      # severity check fires
    assert res["material_mix"][2] is False     # materials untouched, so only severity drifted


def test_severity_check_stays_quiet_on_clean_batches():
    alarms = sum(
        batch_drift(make_data.make_batch(s, 100, "c", make_data.MATERIAL_P), MODEL)["severity_mix"][2]
        for s in range(100, 150))
    assert alarms <= 1