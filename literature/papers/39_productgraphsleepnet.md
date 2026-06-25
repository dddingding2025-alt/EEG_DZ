# ProductGraphSleepNet: Spatio-Temporal Graph Learning for Sleep Staging

- 年份/状态：2022，arXiv。
- 链接：https://arxiv.org/abs/2212.04881
- 任务：多通道 PSG/EEG 睡眠分期。
- 方法：联合学习空间脑区图和相邻 epoch 时间图，捕捉 sleep stage transition dynamics。
- 数据/指标：MASS SS3 与 SleepEDF；报告 accuracy、F1、kappa。
- 对本项目的价值：说明相邻 epoch 转移动态可被图模型表达；适合作为“结构化转移建模”的相关工作。
- 局限：没有把边界偏移、碎片化、转期窗口表现作为核心输出。

