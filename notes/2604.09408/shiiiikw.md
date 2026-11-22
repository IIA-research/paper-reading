---
name: "Kevin"
---

HiL-Bench研究agent在执行任务时，能否发现无法靠现有信息解决的缺口（blocker），提出有针对性的问题。它由LLM判断问题是否命中隐藏的blocker登记表，命中后返回预设答案，再衡量有效提问比例和信息缺口覆盖率。此外，文章对Qwen3-32B进行强化学习，训练奖励 = 0.3 × 解决新blocker的有效提问次数-0.1×无关或重复提问次数+已解决blocker数/总blocker数。 benchmark基于SWE-Bench Pro的软件修复任务和BIRD的SQL任务，每个任务设置3—5个信息缺失、需求歧义或信息矛盾的blocker，通过修改需求、代码或数据库相关信息，将关键答案从agent可见环境中移除，使agent需要在探索过程中发现缺口并询问。baseline包括GPT-5.3-Codex、GPT-5.4、Gemini 3.1 Pro和Claude Opus 4.6四个base，设置No Tool、Full Information和With Tool三种baseline。
