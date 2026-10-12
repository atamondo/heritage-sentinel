import json, sys
from logic import forward_chain, explain
from report_rules import CLAUSES, MATERIALS, DAMAGE, SEVERITIES

def to_facts(report):
    """Schema check + conversion. Raises ValueError for malformed reports."""
    for key in ("id", "material", "damage", "severity"):
        if key not in report:
            raise ValueError(f"schema: missing field '{key}'")
    if report["material"] not in MATERIALS:
        raise ValueError(f"schema: unknown material '{report['material']}'")
    if report["severity"] not in SEVERITIES:
        raise ValueError(f"schema: unknown severity '{report['severity']}'")
    bad = [d for d in report["damage"] if d not in DAMAGE]
    if bad:
        raise ValueError(f"schema: unknown damage type(s) {bad}")
    return ({f"material_{report['material']}", f"severity_{report['severity']}"}
            | {f"damage_{d}" for d in report["damage"]})

def validate(report):
    """Return (ok, reasons, proofs)."""
    try:
        facts = to_facts(report)
    except ValueError as e:
        return False, [str(e)], {}
    known, why = forward_chain(facts, CLAUSES)
    reasons = sorted(s for s in known if s.startswith("invalid:"))
    proofs = {r: explain(r, why) for r in reasons}
    return (not reasons), reasons, proofs

def main(path="data/reports.jsonl", out="data/rejected.log.jsonl"):
    accepted, rejected = 0, 0
    with open(path) as f, open(out, "w") as log:
        for line in f:
            report = json.loads(line)
            ok, reasons, proofs = validate(report)
            if ok:
                accepted += 1
            else:
                rejected += 1
                log.write(json.dumps({"id": report.get("id"), "reasons": reasons,
                                      "proofs": proofs}) + "\n")
    print(f"accepted={accepted} rejected={rejected}")

if __name__ == "__main__":
    main(*sys.argv[1:])