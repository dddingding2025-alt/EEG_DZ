# DeepSleepNet-Lite: A Simplified Automatic Sleep Stage Scoring Model with Uncertainty Estimates

- 年份/状态：2021，arXiv。
- 链接：https://arxiv.org/abs/2108.10600
- 任务：单通道 EEG 睡眠分期，同时估计模型预测不确定性。
- 贡献：用 Monte Carlo dropout 识别 uncertain epochs，并展示拒绝不确定样本后整体指标提升。
- 对方向1的价值：证明 uncertainty 不只是可视化，而可以作为“是否交给人工复核”的操作变量。
- 局限：主要在 Sleep-EDF 上验证；没有直接解决跨数据集 N1 泛化。

