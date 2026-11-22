---
name: "Kevin"
---

When to Stop Asking tests whether an LLM mistakes receiving more relevant information for having enough information to draw a conclusion. The authors generate incomplete cases from 15 clinical scoring systems. Each question presents two cases of similar length with the same number of missing items. The model must choose the case whose outcome can already be determined. In one case, the available facts establish the outcome, such as high or low risk. In the other, the outcome still depends on a missing fact.

The authors then add one relevant detail to one case. The other case stays the same, and the new detail does not change which outcome can be determined. A separate control adds irrelevant text in the same way to account for the change in length. The model sees the scoring system's name, the question, and the two cases, without the scoring rules. The authors compare GPT-5.5, Claude Opus 4.5, Qwen3.5-9B/27B, and Qwen3.6-35B-A3B on the original pairs and both modified versions, with reasoning disabled, enabled, or intensified. Adding relevant information makes models more likely to select a case that still lacks a decisive fact. Enabling reasoning reduces errors overall, although the bias can persist.
