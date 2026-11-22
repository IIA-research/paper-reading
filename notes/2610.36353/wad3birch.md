---
name: "Han Bao"
---

When detecting whether a question is ambiguous, don't let the LLM rewrite the question, because by rewriting it the model has already picked one interpretation for you. Instead, make only small surface-level changes to the question that don't depend on understanding its meaning, and check whether the answers stay stable. The paper argues that LLMs quietly disambiguate while rewriting a question.

Concretely: for the same input, rewrite it with synonyms and check whether the model's answers across multiple runs agree.

*Translated from the author's Chinese note.*
