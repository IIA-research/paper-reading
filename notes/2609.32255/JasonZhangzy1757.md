---
name: "Jason"
---

Same setting as IG-Clarifier (τ-bench customer service tasks), but the starting point is that missing information comes in two kinds: what the agent can look up itself, and what it must ask the user. So the goal is that before each step, the agent picks one of three: act directly, ask the user, or check the environment; if it picks one of the last two, it then writes that sentence.

There are five model instances in the paper, named here by what they do: task agent, decomposer, generator, simulated user, verifier. Except for the generator, which is Qwen3-1.7B and is trained, the other four are untrained Qwen3-8B, each with a different prompt. (Names in the paper: task agent, decomposer, query generator, user simulator, verifier)

**What the decomposer must judge** is: whether "what the user wants is not settled yet", or "what the user wants is already clear, but what to do next is still uncertain". It guesses the user's goal 5 times from the conversation so far, each time writing one sentence of "what the user wants to do"; the 5 guesses cannot see each other and cannot see the real goal. Under each guess, it writes 4 "next actions" (tool name plus parameters). The 20 actions are de-duplicated into a set of candidate actions.

Under each guess, a probability is computed for each action in the candidate set (teacher forcing), which gives 5 action distributions, one per guess. Two measures are computed. The first is "how much the 5 distributions differ" (different guesses lead to different actions, so this number is large, and the user's intent matters a lot.) The second is the average of "how spread out each distribution is by itself": when the guess is already fixed, the more uncertain it is which tool to call next and what parameters to fill in, the larger this number; the paper counts this as missing evidence on the environment side (order status, policy, calculation results). The paper calls these two numbers aleatoric uncertainty and epistemic uncertainty, and the fact card records them under these two names. First number above 0.25 → ask the user; if not, but the second number is above 0.20 → check the environment; if neither → act directly.

- Data: τ-bench (customer service: trained on retail; tested on retail and airline); also tested on τ³-bench without retraining.
- Baselines: heuristics (no intervention, a prompt that picks one of the three directly); from this field: IG-Clarifier, Ask-before-Plan, SAGE-Agent (ask the user), VerifiAgent (check the environment only), SABER (asks the user to confirm before changing state), all re-implemented on Qwen3-8B.
