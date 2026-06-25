# 转期感知长上下文睡眠分期专题文献表

检索日期：2026-06-25  
主题：temporal context、whole-cycle modeling、transition-aware sleep staging、hypnogram dynamics、high-resolution staging。  

## 核心结论

- 现有工作普遍承认上下文有用，但大多仍按 epoch-level accuracy、macro-F1、kappa 汇报。
- 直接把“转期”作为训练对象的代表工作是 TransSleep；直接把“整周期上下文”作为核心的代表工作是 L-SeqSleepNet。
- S4Sleep 及其长相关性分析给出重要反例：模型具备长程建模能力，不代表把上下文拉长到数百 epoch 就一定提升。
- 30 秒 epoch 是临床评分习惯和工程折中，不是自然生理边界；AnySleep 等工作已经开始转向 sub-30-second / high-resolution scoring。

## 文献表

| # | 年份 | 论文 | 上下文/转期做法 | 数据集 | 指标 | 代码 |
|---:|---:|---|---|---|---|---|
| 1 | 2017 | DeepSleepNet | CNN + BiLSTM 自动学习阶段转移规则 | Sleep-EDF, MASS | Acc, MF1 | 需核验 |
| 2 | 2018 | SeqSleepNet | sequence-to-sequence 层级 RNN | MASS | Acc, MF1, kappa | 需核验 |
| 3 | 2019 | IITNet | sub-epoch + inter-epoch BiLSTM，比较 L=1..10 | Sleep-EDF, MASS, SHHS | Acc, MF1, kappa, per-stage F1 | 需核验 |
| 4 | 2020 | XSleepNet | multi-view sequence-to-sequence | 多个数据库 | Acc, MF1, kappa | 需核验 |
| 5 | 2021 | SleepTransformer | Transformer sequence-to-sequence，解释邻近 epoch 影响 | 多数据库 | Acc, MF1, kappa, uncertainty | 需核验 |
| 6 | 2022 | TransSleep | transition detection 辅助任务 + stage-confusion estimator | Sleep-EDF, MASS | Acc, MF1, kappa, ablation | 需核验 |
| 7 | 2022 | ProductGraphSleepNet | spatio-temporal graph + temporal aggregation 捕捉转移动态 | MASS, Sleep-EDF | Acc, F1, kappa | 需核验 |
| 8 | 2023 | L-SeqSleepNet | whole-cycle long sequence modeling，约 90 分钟周期 | 4 个数据库，多种 EEG setup | Acc, MF1, kappa, robustness | 有代码链接 |
| 9 | 2023 | Continuous Sleep Depth | 用连续 sleep depth 变量解释离散 hypnogram | EEG overnight data | clustering/separability | 不适用 |
| 10 | 2023 | S4Sleep | encoder-predictor 设计空间，S4 建模序列 | SHHS | Acc, MF1, kappa | 有代码链接 |
| 11 | 2024 | Long-range correlations analysis | 系统拉长 S4Sleep 输入，发现收益不显著 | sleep staging benchmark | Acc/MF1 相关 | 需核验 |
| 12 | 2024 | Product / Riemannian / SPD Transformer 线 | 用 covariance/time-series 结构建模序列 | 单/多数据集 | class-wise metrics | 需核验 |
| 13 | 2024 | NeuroNet | SSL + Mamba temporal context module | 3 个 PSG 数据集 | Acc, MF1, kappa | 需核验 |
| 14 | 2024 | BiT-MamSleep | 多尺度 CNN + Bidirectional Mamba | 4 个公开数据集 | Acc, MF1, kappa | 需核验 |
| 15 | 2025 | NeuroSleepNet | 主张仅依赖当前输入微事件，也达到接近 SOTA | Sleep-EDF, MESA, Physio2018, SHHS | Acc, MF1, kappa | 需核验 |
| 16 | 2025 | NeuroLingua | 3 秒 token + 7 epoch hierarchical Transformer | Sleep-EDF, ISRUC | Acc, MF1, kappa | 需核验 |
| 17 | 2025 | AnySleep | channel-agnostic + adjustable temporal resolution | 21 数据集，多中心 | 30s 和 sub-30s 评估 | 模型公开声明 |
| 18 | 2025 | Context-Aware Temporal Modeling | 多尺度特征 + 层级序列学习，强调 N1 | SleepEDF | Acc, macro-F1, N1 F1 | 需核验 |
| 19 | 2026 | STDA-Net | spectrogram + BiLSTM + DANN，跨数据集适配 | Sleep-EDF, SHHS | Acc, macro-F1 | 需核验 |
| 20 | 2026 | Hypnos | next-token sleep physiology foundation model | 大规模多模态 PSG | label-efficient staging | 需核验 |

## 对本项目的直接启发

1. **不要只比较上下文长度**：S4Sleep 长相关性分析已经提示上下文越长不一定越好。我们的实验必须回答“哪些转期需要上下文、哪些不需要”。
2. **转期要成为评测对象**：TransSleep 做了 transition detection 辅助任务，但常规论文仍缺少 transition-window macro-F1、boundary delay、fragmentation error 等主指标。
3. **方法要轻量**：第一篇文章应固定 backbone，加入 transition-aware loss/decoding/metrics，避免陷入大模型工程。
4. **高分辨率是远期扩展**：AnySleep 支持 sub-30-second 方向，但第一版可以先用 30 秒 hypnogram 标签定义转期窗口，不依赖额外标注。

