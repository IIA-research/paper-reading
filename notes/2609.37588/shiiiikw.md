---
name: "Kevin"
---

Rational Clarification studies whether an agent facing an ambiguous request should ask a question first or act and let the user correct it. Its training-free method, REVOIR, has an LLM list plausible user intents, estimate their probabilities, generate candidate questions, and simulate how a user with each intent would reply. It compares the expected task payoff and communication cost of asking before acting with those of acting immediately. When users can correct an answer, it also accounts for the payoff of revising it after a correction.

The benchmarks are CondAmbigQA and ADAPT. For CondAmbigQA, the authors remove the Wikipedia retrieval material and give the simulated user the true intent. In one setting, answering ends the interaction. In the other, the user can correct the answer. ADAPT uses household tasks with hidden user preferences. REVOIR asks its questions before executing the full plan.

The main experiments use Llama-3.1-8B/70B and GPT-5.4-mini directly. Question-answering baselines include Direct Answer, which never asks, and ReAct, which decides whether to ask or answer as it reasons. SC-BoN-ReAct votes across multiple samples, REIGN selects questions by information gain, and Entropy Thresholding uses intent entropy to decide whether to keep asking. The authors also compare ReflectionDPO-ReAct and Oracle-ReAct, which has access to the target answer. ReflectionDPO-ReAct requires separate training of an 8B model using improved questions or answers generated with access to the reference answer and paired with the model's original responses. ADAPT comparisons also include Always-Ask, Reflection-DPO, and STaR-GATE.
