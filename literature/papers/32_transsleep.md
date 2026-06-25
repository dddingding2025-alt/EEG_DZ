# TransSleep: Transitioning-aware Attention-based Deep Neural Network for Sleep Staging

- 年份/状态：2022，arXiv。
- 链接：https://arxiv.org/abs/2203.12590
- 任务：自动睡眠分期，重点处理 transitioning epochs 和易混阶段。
- 方法：multi-scale feature extractor、stage-confusion estimator、context encoder，并加入 stage-transition detection 辅助任务。
- 数据/指标：Sleep-EDF 与 MASS；报告常规分期指标和消融。
- 对本项目的价值：这是“转期感知”最直接的近邻工作。我们的差异应放在 transition-centered evaluation 和轻量 sequence regularization，而不是只复刻 transition auxiliary task。
- 局限：仍主要围绕常规 sleep staging 性能叙事，缺少系统的转期窗口指标和 boundary delay 分析。

