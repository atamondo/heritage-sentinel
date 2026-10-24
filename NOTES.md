Q: If you swapped the problem file, did the planner need to change? Why or why not?

A: The planner did not need to change at all. The planner's only job is to take the data
given (not strictly analyze it) and append it to the list as long as state == goal. 
It never observes the cost of the action, so it is not cost effective. It would only
need to change if there were specific requirements where state == goal if it satisfied
a given requirement.

Q: What did test_no_solution_returns_none catch that you didn't expect?

A: It didn't catch anything unexpected as "bfs_search" already returned "None" correctly on 
an unreachable goal.

Q: What did you see in the hidden-trap experiment, and why?

A: With VARIABLES = list(set(ACTIONS.keys())), running python src/main_csp.py with the same config
gave different plans on different runs. Python randomizes string hashing every time 
it starts, so a set of strings comes out in a different order each run thus changing the order of VARIABLES. 
The solver then tries variables in a different order, so it finds a different first solution. The seed only 
controls the solver's own randomness, not the order of the input. Inside one process the order never changes, 
which is why only the subprocess test can catch it.

Q: Your Lab 2 oracle was correct when you wrote it. What does its failure here tell you about tests over time?

A: A test is only correct for the requirements that existed when it was written. The Lab 2 oracle only checked 
prerequisites, so once the tranche rule was added, it kept accepting plans that were now invalid, and nothing 
warned me. Passing tests only mean the code matches the tests, so when requirements change, the tests need to 
be updated too.

Q: Why does the while loop always terminate? What quantity grows each pass, and what bounds it?

A: The while loop always terminates because each pass adds one new symbol to known, so known grows.
It's bounded by a finite set of symbols that appear as facts or clause conclusions, so it can only
grow a finite amount of times. This will eventually lead to a full pass adding nothing, changed stays false, 
and then the loop exits.

Q: Why does explain call sorted(premises)? 

A: It calls sorted(premises) becuase premises is a frozen set, and the set iteration order isn't guaranteed.
As a result, the output becomes stable and testable as the sorting makes the proof lines come out in a
determinable and repeatable order.

Disagreements with Self-Check:

- After comparing my guesses with the system, I had just about the same answers as it did except for one.
I believed that r11 was valid until the system reported back
that the marble material was unknown.

Q: Try to write a rule that rejects a report with severity major but no damage listed. Why can't you express it 
as a Horn clause? What would you have to add to the system, and what does it cost?

A: I can't write this as a Horn clause since the rule depends on something being absent (no damage_* fact).
Horn premises can only say what is present, and an empty damage list produces no facts. Writing severity_major alone 
fires on every major report, and any premise like no_damage never fires because nothing derives it.

To support it, I would add either negation as failure to logic.py as it is more complex, because rules must be evaluated in 
layers and clause order starts to matter, or a no_damage fact computed in to_facts, which is simple, but the negation then 
lives outside the knowledge base. I would take the second option here because it's small and keeps logic.py generic.

Q: Read the last five lines of incoming_a.jsonl and predict, for each one, whether it will be accepted, quarantined or rejected. 

A: Line 101: rejected, Line 102: accepted, Line 103: rejected, Line 104: rejected, Line 105: rejected
- After running tests, my predictions were off a bit. I correctly determined the last two reports but the first three were all quarantined.
Something to note about this part: I had to comment out the previous Lab's part E added rules. It messsed up two of the
reports instead of matching what was shown in the lab description.

2. Independence
The model treats crack and loose_base as independent given the material, but on a real object they are linked: a loose base puts stress on the object and tends to cause cracks. Because the model multiplies the two probabilities, it underestimates how often they appear together and overstates how surprising such an object is. The same applies to rot and crack in wood.

3. Parameters
The model has 35 free parameters: 4 for material, 25 for damage (5 types x 5 materials, 1 each), and 6 for severity (3 buckets x 2). With 400 reports that is about 11 reports per parameter, and each material gets about 80 reports to estimate its damage rates, which is enough. With 40 reports each material would have about 8, so many estimates would come mostly from the smoothing and not the data, and the 2% threshold would sit at the single lowest score, which is very noisy.

4. Smoothing
Without smoothing, any combination missing from the reference data gets probability 0, and log(0) raises an error. In production this happens when an inspector reports something that was never in the reference data, such as a stone object with corrosion, and the pipeline would crash on a perfectly valid report.

5. Calibration
The gap was small because the model is small (35 parameters) and the data is fairly large (400 reports), so it can't memorize its training data. The gap would be larger with a model with many more parameters or less data, because the reference reports would then score better than fresh ones and the threshold would be too lenient. This problem is called overfitting (the train/test generalization gap).

6. Quarantine versus reject
This system treats rare but true reports as suspicious: a real unusual find like a-odd3 is held back just because the model hasn't seen much like it, and the reporter has to prove it. If losing a rare discovery were worse than admitting a typo, I would lower the threshold (for example, a smaller q such as 0.005 instead of 0.02) so fewer reports are flagged. The price is that more real typos and bad entries would be accepted without review.

Additional P5 notes:

Why no record-level check can catch batch B:
Every report in batch B is individually ordinary, so both the logic gate and the likelihood threshold accept all 100. The problem is the proportions across the batch (the material mix has a chi-square of 155.24 against a critical value of 18.467), and a proportion is a property of the whole batch, not of any one report. This is the whole reason the batch-level check exists.

Why exactly 8 of 400 reference reports fall below the threshold: 
calibrate takes ordered[floor(0.02 x 400)], which is ordered[8], and indices 0 to 7 are strictly below it. So about 2% of normal reports are quarantined by design.

Why the held-out test uses a band (0.5% to 4%) and not exactly 2%: 
The rate is random, and the threshold itself is estimated from only 400 reports. The model was also fitted on those reports, so fresh data scores slightly worse and the rate lands a little above 2%.

Why a factorized model: 
A full joint table over material, damage subset and severity would need 479 free parameters, far too many for 400 reports. The factorization needs 35, at the cost of assuming independence (see answer 2).

Part E
Severity-drift check: 
|batch_drift now has a severity_mix key, which compares the batch's severity counts to the reference distribution fitted with fit_categorical. It uses df = 2 (three severities minus one) and a critical value of 13.816 at p = 0.001. One test shows it fires when only severity is shifted, and another shows it stays quiet on clean batches.

Own rules: 
I added loose_base_on_textile (a textile has no base to come loose) and fiber_failure_marked_minor (wood with rot and a crack can't be minor). These make Layer 1 reject some reports that the handout's rule base only quarantines or accepts, so the output differs from the handout's expected numbers. Something to note: When running tests, 
some of them may fail due to conflicts with the previous Lab P4. As mentioned earlier, I have commented out some of the previous Lab's code so the functionality only matters for the current Lab P5.

Self-check output: 
The self-check outputs matched the handout exactly before Part E. After adding the severity_mix key to drift, the printed output has one extra entry by design.