Q: If you swapped the problem file, did the planner need to change? Why or why not?

A: The planner did not need to change at all. The planner's only job is to take the data
given (not strictly analyze it) and append it to the list as long as state == goal. 
It never observes the cost of the action, so it is not cost effective. It would only
need to change if there were specific requirements where state == goal if it satisfied
a given requirement.

Q: What did test_no_solution_returns_none catch that you didn't expect?

A: It didn't catch anything unexpected as "bfs_search" already returned "None" correctly on 
an unreachable goal.