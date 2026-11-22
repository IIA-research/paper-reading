---
name: "Kevin"
---

When2Call studies when an LLM should call a tool, ask the user for a missing detail, or acknowledge that it cannot answer with the available tools and information. The authors adapt BFCL v2 Live for evaluation. They retain requests with valid tool calls, remove argument information from user requests to create cases that require clarification, and construct cases the available tools cannot solve. They apply the same approach to APIGen for training.

The authors use Reward-aware Preference Optimization (RPO). For two responses to the same request, the difference in their rewards determines how strongly training should favor the correct one. For example, if a user asks for company information without supplying a domain, the preferred response asks for the domain. The rejected response guesses Apple's domain and calls the tool. Training mixes these response-choice pairs in a 1:1 ratio with pairs that distinguish a valid tool call from one with missing or incorrect arguments. This trains both the decision to call and the choice of arguments.

Llama-3.1/3.2, Qwen2.5, xLAM, and GPT-4o/4o-mini/4-Turbo are evaluated without retraining on When2Call. For each Mistral-NeMo-Minitron model (4B and 8B), the authors compare three versions. The first uses supervised fine-tuning (SFT) on existing tool-use and general data. The second adds correct responses from When2Call to the SFT data. The third follows SFT with RPO on the paired responses. RPO strikes a better balance between deciding when to call and making valid calls than adding SFT examples alone.
