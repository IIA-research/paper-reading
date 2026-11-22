---
name: "Han Bao"
---

Benchmark paper.

No user is involved, but asking the user also counts as abstention. At each step the agent has three choices: act, answer, or abstain.

Three settings: WebShop (feasible and infeasible requests; infeasible ones are of two kinds: the target product is not in the environment, or the request itself is flawed), Terminal-Bench (feasible; false premise or self-contradiction; unclear intent; missing necessary conditions), and AbstentionBench.

Timely abstention rate (AbsRec@K): among the items where the agent should abstain, the fraction where it abstains within K steps after the earliest step at which abstention could be justified.
