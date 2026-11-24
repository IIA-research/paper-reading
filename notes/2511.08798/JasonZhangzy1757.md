---
name: "Jason"
---

1) **They built a benchmark, ClarifyBench.** Tool-calling tasks in five domains (booking flights, ordering food and the like). The requests are written to miss parameters on purpose, and there is a simulated user who holds the real intent: when the agent asks a question, it answers; when the agent gives a tool call, the request is over. What is scored is whether the parameters of the final call are complete and correct; the average number of questions asked is also reported.

2) No training. First, an LLM reads the user's request and the tool list and writes several tool calls that might need to be run. Parameters that can be settled from the request are filled in; those that cannot are marked "unknown". This is like intent recognition: it turns "what the user wants me to do" into several concrete candidates. Then **it computes how certain each candidate is now.** For each unknown parameter in a candidate, it looks at how many possible values it has; the more possible values, the less certain the candidate (for the unfilled parameters, "1 / number of values" of each is multiplied together. A parameter with two choices gives a factor of 0.5; a free-text parameter gives a factor close to 0); a candidate with all parameters filled is the most certain, so it is run, and this turn ends.

**If it is not certain enough, it decides which question to ask.** The LLM writes 5 questions, each aimed at one or more unknown parameters. Two numbers are computed for each question: a) Gain: suppose the user answers and all the parameters this question aims at become settled; how much more certain the most certain candidate becomes than now. Purpose: find which parameter, when asked, settles things the most. By this rule, questions about the parameter with the most possible values have the highest gain. The paper calls it EVPI. b) Cost: how many times the parameters this question aims at have been asked before; subtract 0.5 for each time. Score = gain − cost.

If the top score is below 0.1 × the current highest candidate probability, it does not ask and runs the call; otherwise it asks the top-scoring question. When the user answers, the answer is turned into limits on the possible values of the parameters, and it goes back to step 1.

When is at the very start; after asking, it keeps executing and does not ask again.

- Data: self-built ClarifyBench (multi-domain tool calling based on BFCL-v3, with requests missing parameters on purpose); there is also a separate training experiment on When2Call (decide whether to call a tool, ask a follow-up, or say it cannot be done).
- Baselines: prompting agents (ReAct with an ask-question tool, ReAct given the parameter descriptions); from this field: ProCoT, Active Task Disambiguation; plus their own heuristic version (ask whenever a parameter is unknown).
