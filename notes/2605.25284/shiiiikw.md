---
name: "Kevin"
---

Knowing but Not Showing研究LLM能否识别问题中的歧义，以及这种识别是否会转化为主动澄清。它让同一模型分别直接回答问题和显式判断歧义，一次让模型回答，另一次问它“这道题有没有歧义？”然后让另一个LLM检查第一次的回答，记录模型有没有给答案、有没有说“无法回答”、有没有向用户追问。benchmark使用AmbigQA已有的歧义问题、无歧义问题和消歧改写，分别在提供和不提供Wikipedia检索段落时评估。主实验包括GPT-4.1、GPT-4o、GPT-4、GPT-3.5-Turbo、GPT-4o-mini、GPT-4.1-mini、Claude-3.5-Sonnet、Claude-3.5-Haiku和Qwen2.5-7B/14B共10个base，比较Question Answering、Ambiguity Judgment两种设置及有无检索上下文的条件。结果表明有时即使llm知道存在歧义，但是并不会转化为发问。
