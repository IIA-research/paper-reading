---
name: "Jason"
---

**when：在training阶段 通过predetermined手段（在这里是每次对话开始）通过rollout问或不问去积累GT，以此去学习一个控制器；然后在预测阶段依靠控制器打分。what：模版加根据task决定的属性词（也就是最容易被问到的问题），然后6个问题+不问做单选。**

具体而言，在训练阶段：一条任务进来，用户的问题之后紧接着选择候选话题，候选话题来自数据集自带的属性或冻结 LLM生成（这个task最有可能遗漏、最需要被问到的问题）。在这里（也就是task开始，用户问题之后）分 5 条rollout：2 条不问直接做，2 条问控制器最看好的一个话题z，1 条问另一个话题强制探索。每条跑到底拿终局分。"问 z 的平均分 − 不问的平均分"就是 z 的价值。这个数干两件事：当控制器的回归标签，当这条续写的优势去更新策略。每个任务在训练中只用一次。控制器接受问题的embedding所以对语义有所判断，一开始随机全 0，一开始按照embedding本能选，64 个任务后才开始有意见。控制器 是一个 冻结 4B 的模型 + 67 万参数的MLP，学的是"请求长这样、可以问的话题是这个，一般涨几分"。

在测试阶段：开头控制器给每个话题打分，最高分 > 0 就问，问完对话更新重新打分，直到剩余话题没有分数大于0的，让agent根据策略自己做完。

- 数据：UserGym（Travel、Turtle、Intention、Telepathy 四个和模拟用户交互的任务）、τ²-Bench（航空、零售、电信客服）、IN3（判断指令缺不缺信息）、AskBench（缺信息、错误前提的问答）。
- Baseline：提示词（Vanilla、ReAct、Reflexion、Proactive CoT、PRIME）；阈值 heuristic（CLAM、INTENT-SIM、VoI 改的阈值版）；信息增益训练（IG-Clarifier、InfoPO、IGPO）；SFT、GRPO；附录另比 ACT、CollabLLM。
