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

## 4. 第二轮专题补充：转期感知长上下文

用户选择“转期感知长上下文睡眠分期”作为第一篇文章方向后，补充筛选了 20 篇 temporal context / transition-aware / whole-cycle / high-resolution staging 相关论文。详表见 `literature/transition_context_survey.md`。

2026-06-26 修订：该方向不再以“转期评测协议”作为主创新，而是收束为 **Transition-Guided Context Modulation (TGCM)**。核心差异是用转期概率动态调制 short/mid/long 上下文融合；转期指标和 gate 可视化用于验证机制有效。

新增重点条目：

| 年份 | 论文 | 价值 | 链接 |
|---:|---|---|---|
| 2022 | TransSleep | 直接使用 stage-transition detection 辅助任务，是转期感知最直接近邻 | https://arxiv.org/abs/2203.12590 |
| 2023 | L-SeqSleepNet | whole-cycle long sequence modeling，支撑 90 分钟上下文实验条件 | https://arxiv.org/abs/2301.03441 |
| 2023 | Continuous sleep depth | 提供“睡眠状态连续而非硬边界”的理论动机 | https://arxiv.org/abs/2301.06755 |
| 2023 | S4Sleep | 结构化状态空间模型，适合做强序列建模背景 | https://arxiv.org/abs/2310.06715 |
| 2024 | Long-range correlations analysis | 反例：单纯拉长上下文未必提升 | https://arxiv.org/abs/2402.17779 |
| 2025 | NeuroLingua | 3 秒 token + 7 epoch 层级上下文 | https://arxiv.org/abs/2511.09773 |
| 2025 | AnySleep | adjustable temporal resolution，说明 30 秒 epoch 不是自然边界 | https://arxiv.org/abs/2512.14461 |
| 2025 | Context-Aware Temporal Modeling | 强调 N1、局部-长程上下文和可解释性 | https://arxiv.org/abs/2512.22976 |

## 5. 方向1专题补充：N1标签不确定性、相邻软标签与转期不确定性

本节用于支撑 `to_human/direction1_n1_label_uncertainty_report.md` 和 `literature/n1_label_uncertainty_survey.md`。根据用户反馈，本方向不再把 domain shift / 跨数据集泛化作为核心机制；跨数据集只保留为后续 robustness check。主线改为：N1 的 class imbalance、label uncertainty、W-N1-N2 阶段相邻性和转期边界不确定性。

| # | 年份 | 类型 | 论文/资料 | 直接相关点 | 链接 |
|---:|---:|---|---|---|---|
| D1 | 2019 | Dataset/Anchor | Dreem Open Datasets: Multi-Scored Sleep Datasets | 5 位评分员、多评分员共识、人工一致性上限 | https://arxiv.org/abs/1911.03221 |
| D2 | 2021 | Method | DeepSleepNet-Lite with Uncertainty Estimates | MC dropout、uncertain epochs、拒识 | https://arxiv.org/abs/2108.10600 |
| D3 | 2021 | Method | SleepTransformer | Transformer、attention 解释、不确定性熵 | https://arxiv.org/abs/2105.11043 |
| D4 | 2021 | Method | MSDAN | 明确针对 N1 表现差，多尺度注意力 | https://arxiv.org/abs/2107.08442 |
| D5 | 2023 | Method | SleepEGAN | 少数类增强、class imbalance、ensemble | https://arxiv.org/abs/2307.05362 |
| D6 | 2024 | Robustness background | SleepDG / Generalizable Sleep Staging | 多数据集 domain generalization，作为后续鲁棒性背景 | https://arxiv.org/abs/2401.05363 |
| D7 | 2024 | Robustness background | SPDIM | source-free adaptation、label shift，作为后续部署背景 | https://arxiv.org/abs/2411.07249 |
| D8 | 2025 | Robustness background | SelectiveFinetuning | source selection、negative transfer，作为后续跨数据集背景 | https://arxiv.org/abs/2501.03764 |
| D9 | 2025 | Interpretability | Retrieving Filter Spectra in CNN | EEG 频带解释，检查是否学到合理证据 | https://arxiv.org/abs/2502.06478 |
| D10 | 2025 | Robustness background | SleepDIFFormer | heterogeneous EEG/EOG、跨域对齐，作为后续鲁棒性背景 | https://arxiv.org/abs/2508.15215 |
| D11 | 2025 | Uncertainty / TTA | StableSleep | source-free test-time adaptation、entropy gate，可借鉴 entropy gating | https://arxiv.org/abs/2509.02982 |
| D12 | 2025 | Wearable SSL | Systematic Evaluation of SSL for Wearable EEG | 少标签、可穿戴、跨数据集泛化，作为后续扩展 | https://arxiv.org/abs/2510.07960 |
| D13 | 2025 | N1 method | Context-Aware Temporal Modeling for Single-Channel EEG | N1 F1、上下文、class-weighted loss | https://arxiv.org/abs/2512.22976 |
| D14 | 2026 | Clinical transfer | Fully-Automated Sleep Staging in PD/iRBD | 疾病人群迁移、人工二次评分、REM 置信阈值 | https://arxiv.org/abs/2602.09793 |
| D15 | 2026 | Clinical gap | AI Generalisation Gap in Comorbid Sleep Disorder Staging | 病理人群泛化缺口、解释性错误分析 | https://arxiv.org/abs/2603.23582 |
| D16 | 2026 | Robustness background | FF-TRUST / NL-DGSS | noisy labels + multi-source domain generalization，说明 label noise 与 domain shift 可共存但不应混成同一主问题 | https://arxiv.org/abs/2604.10009 |
| D17 | 2026 | Robustness background | STDA-Net | Sleep-EDF 与 SHHS 跨数据集适配，作为后续 robustness baseline | https://arxiv.org/abs/2605.06736 |
| D18 | 2026 | FM eval | Multi-Dimensional EEG Foundation Model Evaluation | 低资源、少传感器、长上下文任务评测 | https://arxiv.org/abs/2605.28563 |
| D19 | 2026 | Sleep FM | Hypnos / Next-Token Prediction | 大规模 sleep foundation model、label efficiency | https://arxiv.org/abs/2606.09605 |

方向1的直接支撑线是 D1、D2、D3、D11 的不确定性建模，D4、D5、D13 的 N1 / class imbalance / temporal context 研究，以及 LSSC 多评分员 soft-consensus 方法。D6、D7、D8、D10、D16、D17 不再作为方向1直接竞争线，而是后续跨数据集鲁棒性背景。

## 6. 统一规划：转期不确定性引导的 N1 识别

2026-06-26 后，方向1与方向2不再作为两个并列论文主题推进，而是统一为“转期/边界不确定性引导的 N1 睡眠阶段识别”。第一篇文章主线是 N1 标签不确定性，TGCM 作为第二阶段增强模块。

统一规划的证据链如下：

- D1/LSSC/D2/D3 支撑标签不确定性、多评分员分歧和模型不确定性；
- D4/D5/D13 支撑 N1 难题和 class imbalance baseline 必要性；
- TransSleep/L-SeqSleepNet/S4Sleep/长相关性分析支撑上下文和转期建模背景；
- SleepDG/STDA-Net/FF-TRUST 等跨数据集工作只作为 robustness 背景，不作为主贡献。

后续实验应先验证 stage-adjacent soft label 与 transition-window uncertainty 是否改善 N1 F1、transition-window N1 F1 和校准；只有在该主假设成立或需要解释上下文需求时，再引入 TGCM。
