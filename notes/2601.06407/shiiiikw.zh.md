---
name: "Kevin"
---

VOI研究的是让 agent 在提问前估计“这一提问能让最终决策改善多少”，只有这一问带来的价值值得用户付出的沟通成本时才会提问。这里衡量价值的方法是：净信息价值=E(问完后最佳决策的收益)-当前决策的收益-提问成本。benchmark是基于现有benchmark进行的改造，比如动物版 20 Questions用是／否问题，从100个候选动物中猜出目标，医疗诊断版 20 Questions根据医患对话信息，通过询问从15个候选疾病中判断疾病，Ambiguous WebShop删除原始指令中的部分属性，如颜色、尺寸、品牌，制造歧义，再允许 agent 询问缺失信息。baseline是四种通信控制策略，No-Question、Fixed-Round、Adaptive Prompting、Confidence Thresholding。
