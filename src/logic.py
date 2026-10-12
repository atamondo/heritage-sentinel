# logic.py — generic forward-chaining inference. No heritage vocabulary allowed here.

def forward_chain(facts, clauses):
    """facts: iterable of symbols. clauses: list of (premises, conclusion),
    where premises is a frozenset of symbols.
    Returns (known, why): every symbol entailed by the KB, and for each one
    the premises that produced it (None if it was given as a fact)."""
    known = set(facts)
    why = {f: None for f in known}
    changed = True
    while changed:
        changed = False
        for premises, conclusion in clauses:
            if conclusion not in known and premises <= known:
                known.add(conclusion)
                why[conclusion] = premises
                changed = True
    return known, why


def explain(symbol, why, depth=0):
    """Return proof lines for `symbol`, indented by derivation depth."""
    pad = "  " * depth
    premises = why[symbol]
    if premises is None:
        return [f"{pad}{symbol}  (given)"]
    lines = [f"{pad}{symbol}  because:"]
    for p in sorted(premises):
        lines += explain(p, why, depth + 1)
    return lines