# prob.py — generic probability helpers. No heritage vocabulary allowed here.
from collections import Counter

def fit_categorical(observations, domain, alpha=1.0):
    """P(value) with add-alpha (Laplace) smoothing. Returns {value: prob}.
    Every value in `domain` gets nonzero probability, even if never observed."""
    counts = Counter(observations)
    denom = len(observations) + alpha * len(domain)
    return {v: (counts[v] + alpha) / denom for v in domain}


def fit_conditional(pairs, parent_domain, child_domain, alpha=1.0):
    """P(child | parent) from (parent, child) pairs. Returns {parent: {child: prob}}."""
    by_parent = {p: [] for p in parent_domain}
    for parent, child in pairs:
        by_parent[parent].append(child)
    return {p: fit_categorical(by_parent[p], child_domain, alpha) for p in parent_domain}


def chi_square(observed_counts, expected_probs):
    """Pearson chi-square statistic comparing observed counts to expected probabilities."""
    n = sum(observed_counts.values())
    stat = 0.0
    for k, p in expected_probs.items():
        expected = n * p
        observed = observed_counts.get(k, 0)
        stat += (observed - expected) ** 2 / expected
    return stat


def percentile(values, q):
    """Nearest-rank style: the value at index floor(q * n) of the sorted list."""
    ordered = sorted(values)
    return ordered[min(int(q * len(ordered)), len(ordered) - 1)]