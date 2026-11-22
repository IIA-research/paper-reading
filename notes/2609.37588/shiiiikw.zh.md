---
name: "Kevin"
---

Rational Clarification研究agent面对含糊请求时，应该先提问，还是先行动再接受用户纠正。它提出无需训练的REVOIR，让LLM列出可能的用户意图并估计概率，生成候选问题，模拟各个意图下的用户回复，再比较“问完再行动”和“立即行动”的预期任务收益与沟通成本；允许用户纠正时，还计算先回答、收到纠正后再修改的收益。benchmark使用CondAmbigQA和ADAPT：前者取消Wikipedia检索材料，由模拟用户掌握真实意图，分别设置回答即结束和允许用户纠正两种情况；后者使用带隐藏用户偏好的家庭任务，让REVOIR先问完问题，再执行完整计划。主要直接运行Llama-3.1-8B/70B和GPT-5.4-mini，问答baseline包括不提问的Direct Answer、边推理边决定问或答的ReAct、多次采样投票的SC-BoN-ReAct、按信息增益选问题的REIGN、按意图熵判断是否继续问的Entropy Thresholding、ReflectionDPO-ReAct，以及已知目标答案的Oracle-ReAct。ReflectionDPO-ReAct另外训练8B模型，用标准答案生成改进后的提问或回答，与模型原回复配对。ADAPT还比较Always-Ask、Reflection-DPO和STaR-GATE等方法。
