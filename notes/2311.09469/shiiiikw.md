---
name: "Kevin"
---

Clarify When Necessary研究提问次数有限时，LLM应该优先澄清哪些请求，重点识别“不问会答错、问清后能够答对”的情况。它提出无需训练的Intent-Sim：让模型先生成一个澄清问题，再模拟10个可能的用户回复，用另一个模型把意思相同的回复归组，根据各组的比例计算熵，优先询问存在多种可能意图的请求。benchmark使用AmbigQA问答、AmbiEnt自然语言推断和DiscourseMT英法翻译，利用已有标注确定用户意图，其中翻译任务去掉前文来制造歧义。正式评测时，使用GPT-3.5根据标注意图预生成的澄清问答，获得对应的答案后再完成任务。被测模型为GPT-3和Llama-2-Chat 7B/13B，baseline在相同提问预算下比较random select、answer Likelihood、让模型判断“这里是否需要追问”的Self-Ask，以及对多次直接回答归组计算熵的Sample Entropy，完全不澄清、全部澄清和直接提供消歧输入，结果表明Intent-Sim在多数设置下更能挑出澄清后会改善答案的请求。
