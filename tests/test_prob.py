import pytest
from prob import fit_categorical, fit_conditional, chi_square, percentile

def test_categorical_sums_to_one():
    p = fit_categorical(["a", "a", "b"], ["a", "b", "c"])
    assert sum(p.values()) == pytest.approx(1.0)

def test_unseen_value_gets_nonzero_probability():
    p = fit_categorical(["a", "a", "b"], ["a", "b", "c"])
    assert p["c"] > 0

def test_smoothing_formula():
    # 3 observations, domain of 3, alpha=1  ->  (count + 1) / (3 + 3)
    p = fit_categorical(["a", "a", "b"], ["a", "b", "c"], alpha=1.0)
    assert p["a"] == pytest.approx(3 / 6) and p["b"] == pytest.approx(2 / 6) and p["c"] == pytest.approx(1 / 6)

def test_conditional_rows_each_sum_to_one():
    pairs = [("x", "u"), ("x", "u"), ("x", "v"), ("y", "v")]
    cpt = fit_conditional(pairs, ["x", "y", "z"], ["u", "v"])
    for parent, row in cpt.items():
        assert sum(row.values()) == pytest.approx(1.0)
    # "z" never appears in the data: with only smoothing, its row is uniform
    assert cpt["z"] == {"u": pytest.approx(0.5), "v": pytest.approx(0.5)}

def test_parent_never_seen_still_has_a_distribution():
    cpt = fit_conditional([("x", True)], ["x", "z"], [True, False])
    assert cpt["z"] == {True: 0.5, False: 0.5}

def test_chi_square_zero_when_observed_matches_expected():
    assert chi_square({"a": 50, "b": 50}, {"a": .5, "b": .5}) == pytest.approx(0.0)

def test_chi_square_known_value():
    # n = 100, expected = 50 each.
    # a: (60-50)^2 / 50 = 100/50 = 2
    # b: (40-50)^2 / 50 = 100/50 = 2
    # total = 4
    assert chi_square({"a": 60, "b": 40}, {"a": .5, "b": .5}) == pytest.approx(4.0)

def test_chi_square_missing_category_counts_as_zero():
    # observed has no "b" at all; expected 50 -> contributes (0-50)^2/50 = 50
    assert chi_square({"a": 100}, {"a": .5, "b": .5}) == pytest.approx(50 + 50)

def test_percentile_nearest_rank():
    # values 1..100, q = 0.02: index = floor(0.02 * 100) = 2 (int(2.0) == 2)
    # sorted list is [1, 2, ..., 100], so ordered[2] == 3
    assert percentile(list(range(1, 101)), 0.02) == 3