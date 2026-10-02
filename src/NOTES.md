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