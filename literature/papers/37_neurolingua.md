# NeuroLingua: Language-Inspired Hierarchical Framework for EEG/EOG Sleep Stage Classification

- 年份/状态：2025，arXiv。
- 链接：https://arxiv.org/abs/2511.09773
- 任务：EEG/EOG 多模态睡眠分期。
- 方法：30 秒 epoch 切成 3 秒 token，使用 dual-level Transformer 建模局部和跨 epoch 上下文。
- 数据/指标：Sleep-EDF Expanded、ISRUC；报告 accuracy、macro-F1、kappa。
- 对本项目的价值：提供 hierarchical temporal modeling 的近邻实现；也说明 3-5 分钟上下文可作为强起点。
- 局限：没有把 transition-window 指标作为主评测。

