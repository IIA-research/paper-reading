---
name: "Kevin"
---

Value of Information (VOI) asks how much a question is likely to improve an agent's final decision. The agent asks only when the expected improvement justifies the user's communication cost. The net value of a question is the expected payoff of the best decision after receiving an answer, minus the payoff of the current decision, minus the cost of asking.

The authors adapt existing benchmarks to test this idea. In the animal version of 20 Questions, the agent asks yes-or-no questions to identify a target among 100 animals. In the medical version, it uses information gathered through a doctor-patient dialogue to identify one of 15 possible diseases. In Ambiguous WebShop, the authors remove attributes such as color, size, or brand from the original shopping instruction, then let the agent ask for the missing details. The four baseline policies for deciding when to ask are No-Question, Fixed-Round, Adaptive Prompting, and Confidence Thresholding.
