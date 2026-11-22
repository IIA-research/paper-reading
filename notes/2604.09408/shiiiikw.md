---
name: "Kevin"
---

HiL-Bench tests whether an agent can recognize a blocker it cannot resolve with the information available and ask a question that addresses it. An LLM judge checks each question against a hidden list of blockers. If a question matches, the agent receives a predefined answer. The benchmark measures both the fraction of questions that address a blocker and the fraction of blockers the agent uncovers.

The tasks come from SWE-Bench Pro (software repair) and BIRD (SQL). Each task contains three to five blockers involving missing information, ambiguous requirements, or conflicting information. The authors modify the requirements, code, or database information to remove key answers from the agent's environment, so it has to discover the gap as it works. They evaluate GPT-5.3-Codex, GPT-5.4, Gemini 3.1 Pro, and Claude Opus 4.6 under three conditions called No Tool, Full Information, and With Tool. They also train Qwen3-32B with reinforcement learning. The reward is 0.3 times the number of effective questions that resolve a new blocker, minus 0.1 times the number of irrelevant or repeated questions, plus the fraction of blockers resolved.
