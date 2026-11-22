---
name: "Kevin"
---

Knowing but Not Showing asks whether an LLM that recognizes ambiguity will ask the user to clarify. The same model sees each question in two separate settings. In Question Answering, it responds directly. In Ambiguity Judgment, it is explicitly asked whether the question is ambiguous. A separate LLM checks the first response and records whether the model gave an answer, said it could not answer, or asked a follow-up question.

The benchmark uses ambiguous questions, unambiguous questions, and disambiguated rewrites from AmbigQA. Both settings are tested with and without retrieved Wikipedia passages. The ten models are GPT-4.1, GPT-4o, GPT-4, GPT-3.5-Turbo, GPT-4o-mini, GPT-4.1-mini, Claude-3.5-Sonnet, Claude-3.5-Haiku, Qwen2.5-7B, and Qwen2.5-14B. A model can identify a question as ambiguous when asked explicitly and still answer it directly when given the chance to ask for clarification.
