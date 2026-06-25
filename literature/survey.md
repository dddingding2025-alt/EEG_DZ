# EEG 睡眠分期文献索引（第一轮）

检索日期：2026-06-25  
时间窗：2021-06-25 至 2026-06-25  
主线：人类 EEG 或含 EEG 的 PSG 自动睡眠分期，五分类 W/N1/N2/N3/REM 优先。  

说明：

- `Core` 表示本轮已写精读卡片或纳入核心分析。
- `Scan` 表示纳入趋势判断，但不作为主要证据。
- `Anchor` 表示计划指定的关键种子。SleepTransformer 是 2021-05 预印本，严格说略早于五年窗口，但因其代表 Transformer 与不确定性路线，保留为背景锚点，不计入“近五年 30 篇”数量。
- 多数 2025-2026 条目仍是 arXiv 预印本，后续写论文前需二次核验出版状态。

## 1. 核心数据源

| 数据源 | 类型 | 价值 | 链接 |
|---|---|---|---|
| Sleep-EDF Expanded | PSG/EEG, PhysioNet | 单通道 EEG 睡眠分期最常见基准，适合入门复现，但不宜作为唯一证据 | https://physionet.org/content/sleep-edfx/1.0.0/ |
| SHHS | 大规模 PSG, NSRR | 外部泛化和大样本验证价值高，访问需申请 | https://sleepdata.org/datasets/shhs |
| MESA Sleep | 多族裔社区 PSG, NSRR | 年龄、人群差异和心血管相关下游分析 | https://sleepdata.org/datasets/mesa |
| MASS | PSG/EEG | 经典多通道睡眠分期基准，常与 Sleep-EDF/ISRUC 联合用于泛化 | http://massdb.herokuapp.com/en/ |
| ISRUC-Sleep | PSG/EEG | 常用于跨数据集和多通道模型 | https://sleeptight.isr.uc.pt/ |
| CAP Sleep Database | PSG/EEG, PhysioNet | 含睡眠微结构和病理睡眠背景，适合鲁棒性研究 | https://physionet.org/content/capslpdb/1.0.0/ |
| DOD-H / Dreem Open Datasets | 头带 EEG | 可穿戴和居家监测价值高，常用于设备迁移问题 | https://dreem.github.io/dreem-learning-open/ |

## 2. 已筛选论文与预印本

| # | 年份 | 状态 | 论文/方向 | 关键词 | 链接 |
|---:|---:|---|---|---|---|
| 1 | 2021 | Anchor | SleepTransformer: Automatic Sleep Staging with Interpretability and Uncertainty Quantification | Transformer, uncertainty | https://arxiv.org/abs/2105.11043 |
| 2 | 2021 | Core | Automatic Sleep Staging of EEG Signals: Recent Development, Challenges, and Future Directions | review, challenges | https://arxiv.org/abs/2111.08446 |
| 3 | 2021 | Core | Self-supervised Contrastive Learning for EEG-based Sleep Staging | contrastive SSL | https://arxiv.org/abs/2109.07839 |
| 4 | 2021 | Core | ContraWR: Contrast With the World Representation | large-scale SSL | https://arxiv.org/abs/2110.15278 |
| 5 | 2022 | Scan | NCH Sleep DataBank | large clinical PSG dataset | https://arxiv.org/abs/2102.13295 |
| 6 | 2023 | Scan | Latent Alignment with Deep Set EEG Decoders | EEG transfer learning | https://arxiv.org/abs/2311.17968 |
| 7 | 2023 | Core | Dual-stream time-frequency contrastive pretext tasks for sleep stage classification | SSL, time-frequency | https://arxiv.org/abs/2312.09623 |
| 8 | 2024 | Core | Multi-Channel Multi-Domain Knowledge Distillation for Sleep Staging with Single-Channel EEG | distillation, single-channel | https://arxiv.org/abs/2401.03430 |
| 9 | 2024 | Core | LightSleepNet: Personalized Portable Sleep Staging System Based on Single-Channel EEG | lightweight, personalization | https://arxiv.org/abs/2401.13194 |
| 10 | 2024 | Core | Assessing the Importance of Long-Range Correlations for Deep-Learning-Based Sleep Staging | long context, S4Sleep | https://arxiv.org/abs/2402.17779 |
| 11 | 2024 | Core | Data-Efficient Sleep Staging with Synthetic Time Series Pretraining | synthetic pretraining | https://arxiv.org/abs/2403.08592 |
| 12 | 2024 | Core | SleepDG: Less Is More for Domain Generalizable Sleep Staging | domain generalization | https://arxiv.org/abs/2401.05363 |
| 13 | 2024 | Core | Generative Pretrained Model for Sleep Stage Classification With Arbitrary Sensor Input | arbitrary sensors | https://arxiv.org/abs/2408.15253 |
| 14 | 2024 | Scan | Brant-X: Unified Physiological Signal Alignment Framework | EEG to other physiology | https://arxiv.org/abs/2409.00122 |
| 15 | 2024 | Scan | Automatic Classification of Sleep Stages from EEG Using Riemannian Metrics and Transformer Networks | SPD, Transformer | https://arxiv.org/abs/2410.19819 |
| 16 | 2024 | Core | SPDIM: Source-Free Unsupervised Conditional and Label Shift Adaptation in EEG | source-free adaptation | https://arxiv.org/abs/2411.07249 |
| 17 | 2024 | Core | BiT-MamSleep: Bidirectional Temporal Mamba for EEG Sleep Staging | Mamba, class imbalance | https://arxiv.org/abs/2411.01589 |
| 18 | 2025 | Core | SelectiveFinetuning: Enhancing Transfer Learning in Sleep Staging | domain alignment | https://arxiv.org/abs/2501.03764 |
| 19 | 2025 | Core | sDREAMER: Self-distilled Mixture-of-Modality-Experts Transformer | multimodal, self-distillation | https://arxiv.org/abs/2501.16329 |
| 20 | 2025 | Core | Retrieving Filter Spectra in CNN for Explainable Sleep Stage Classification | explainability | https://arxiv.org/abs/2502.06478 |
| 21 | 2025 | Scan | MC2SleepNet: Multi-modal Cross-masking with Contrastive Learning | contrastive, multimodal | https://arxiv.org/abs/2502.17470 |
| 22 | 2025 | Scan | Toward Foundational Model for Sleep Analysis Using Hybrid SSL | PSG foundation model | https://arxiv.org/abs/2502.17481 |
| 23 | 2025 | Core | Tokenizing Single-Channel EEG with Time-Frequency Motif Learning | tokenization, foundation adapters | https://arxiv.org/abs/2502.16060 |
| 24 | 2025 | Scan | PhysioOmni: Robust Multimodal Physiological Foundation Models with Missing Modalities | arbitrary modalities | https://arxiv.org/abs/2504.19596 |
| 25 | 2025 | Core | Multi-Channel Differential Transformer for Cross-Domain Sleep Stage Classification | domain generalization | https://arxiv.org/abs/2508.15215 |
| 26 | 2025 | Core | StableSleep: Source-Free Test-Time Adaptation for Sleep Staging | deployment, TTA | https://arxiv.org/abs/2509.02982 |
| 27 | 2025 | Core | Systematic Evaluation of SSL for Label-Efficient Sleep Staging with Wearable EEG | wearable EEG SSL | https://arxiv.org/abs/2510.07960 |
| 28 | 2025 | Core | REVE: A Foundation Model for EEG | large EEG foundation | https://arxiv.org/abs/2510.21585 |
| 29 | 2025 | Scan | NAPS: Attention-Based Fusion of Heterogeneous Physiological Signals | multimodal fusion | https://arxiv.org/abs/2511.03488 |
| 30 | 2025 | Scan | Resource Efficient Sleep Staging via Multi-Level Masking and Prompt Learning | low-resource sensing | https://arxiv.org/abs/2511.06785 |
| 31 | 2025 | Scan | NeuroLingua: Language-Inspired Hierarchical EEG/EOG Sleep Stage Classification | hierarchical modeling | https://arxiv.org/abs/2511.09773 |
| 32 | 2025 | Core | AnySleep: Channel-Agnostic Sleep Staging in Multi-Center Cohorts | any EEG/EOG, multicenter | https://arxiv.org/abs/2512.14461 |
| 33 | 2026 | Core | Fully-Automated Sleep Staging in Parkinson's Disease and iRBD | clinical generalization | https://arxiv.org/abs/2602.09793 |
| 34 | 2026 | Scan | NeuroSleep: Event-Driven Single-Channel EEG Sleep Staging | edge, neuromorphic | https://arxiv.org/abs/2602.15888 |
| 35 | 2026 | Core | Towards Multi-Source Domain Generalization for Sleep Staging with Noisy Labels / FF-TRUST | noisy labels, domain shift | https://arxiv.org/abs/2604.10009 |
| 36 | 2026 | Core | STDA-Net: Spectrogram-Based Domain Adaptation for Cross-Dataset Sleep Stage Classification | cross-dataset DA | https://arxiv.org/abs/2605.06736 |
| 37 | 2026 | Core | Next-Token Prediction Learns Generalisable Representations of Sleep Physiology / Hypnos | sleep foundation model | https://arxiv.org/abs/2606.09605 |

## 3. 第一轮归纳

1. **传统深度模型仍是强基线**：CNN 提取局部波形/频带特征，RNN/TCN/Transformer 建模睡眠周期和相邻 epoch 依赖。新模型若只在 Sleep-EDF 内部提升小数点，研究价值有限。
2. **泛化是主战场**：跨数据集、跨通道、跨设备、跨年龄和病理人群比同数据集随机划分更接近真实应用。
3. **标签本身不稳定**：N1、转期 epoch、觉醒片段和人工评分分歧使 hard label 学习天然受限。
4. **基础模型正在进入 EEG 睡眠分期**：REVE、Hypnos、AnySleep、PhysioOmni 等说明大规模预训练/多中心训练已经成为重要方向，但严格外部验证、计算成本和适配策略仍是问题。
5. **可穿戴场景的关键在系统鲁棒性**：伪迹、通道缺失、低信噪比、设备差异和不确定性提示比单纯 accuracy 更关键。
