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

