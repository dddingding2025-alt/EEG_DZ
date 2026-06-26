# 方向1专题汇报：面向 N1 标签不确定性的 EEG 睡眠分期

日期：2026-06-26  
范围：EEG/含 EEG PSG 自动睡眠分期；核心聚焦 N1、阶段相邻软标签、转期不确定性。  
状态：已按 N1 标签不确定性主线修订；未下载数据，未训练模型。

2026-06-26 统一规划更新：本报告仍是第一篇文章的主线依据。TGCM 自适应上下文方法作为第二阶段增强模块，用于验证边界不确定样本是否也需要不同上下文尺度；它不替代 N1 标签不确定性主线。

## 0. 结论先行

当前方向应从“标签不确定性 + 跨数据集泛化”修订为：

> 通过阶段相邻软标签与转期不确定性建模提升 N1 睡眠阶段识别。

这个修订是必要的。`Domain shift / 跨数据集泛化` 是任何自动睡眠分期系统都会遇到的独立鲁棒性问题，不是 N1 标签不确定性的组成部分。把二者绑成同一个核心机制会导致论文主问题发散：一边要解释 N1 为什么难，一边又要解决不同设备、导联、人群、评分中心之间的分布变化，实验因果关系会变得不清楚。

因此，第一篇文章的主贡献应只回答一个问题：

> N1 的识别困难是否可以通过显式建模标签不确定性、睡眠阶段相邻性和转期边界来改善，而不是只靠 class weight、focal loss 或换模型结构？

跨数据集实验仍然有价值，但定位改为补充鲁棒性验证：当 within-dataset subject-independent 设置证明方法有效后，再检查它在 ISRUC/MASS/SHHS 等外部数据上的稳定性。

## 1. N1 难题的机制拆分

N1 识别困难不能笼统归因于“模型不够强”。至少要拆成四类机制：

| 机制 | 具体表现 | 典型方法 | 对本方向的定位 |
|---|---|---|---|
| Class imbalance | N1 样本少，模型偏向 W/N2 | class weight、focal loss、balanced sampler、GAN 增强 | 必须做强基线，但不是主创新 |
| Label uncertainty | N1/W/N2 边界存在人工评分分歧 | soft label、multi-rater consensus、teacher soft labels | 本方向主问题 |
| Transition dependence | N1 多发生在 W->N1、N1->N2 转期附近 | temporal context、transition detection、transition-aware loss | 本方向核心机制之一 |
| Domain shift | 换设备、导联、人群或评分中心后性能下降 | DG、DA、TTA、source selection | 后续鲁棒性验证，不放进标题主贡献 |

关键判断：N1 的困难来自“少”和“模糊”的叠加。类别不均衡解释了为什么模型不愿预测 N1；标签不确定性解释了为什么即使提高 N1 权重，也可能只是把 W/N2 边界推歪，导致过预测 N1 或校准恶化。

## 2. 现有研究怎么做

### 2.1 类别不均衡路线

代表工作：

- MSDAN：明确指出多数单通道 EEG 方法在 N1 上不能满足诊断需求，用多尺度卷积和双注意力增强 N1 表征，在 Sleep-EDF 系列上报告 N1 F1 约 52%-54%。
- SleepEGAN：用 GAN 生成少数类样本，并结合 ensemble 缓解类别不均衡和个体异质性。
- Context-Aware Temporal Modeling：把 N1 作为重点，使用多尺度时间编码、层级序列学习、class-weighted loss 和数据增强，在 Sleep-EDF 上报告较高 N1 F1。

局限：

- 这条路线主要解决“样本少”，不直接回答“同一个 30 秒 epoch 本身是否接近 W/N1/N2 边界”。
- 如果 N1 标签本身不确定，简单提高 N1 权重会让模型更用力拟合单一人工标签，可能提升 recall 但降低 precision 或校准。
- GAN/增强类方法需要证明生成样本不是复制伪模式，并且不会把边界样本变成更强的噪声源。

### 2.2 上下文与转期路线

代表工作：

- DeepSleepNet、SeqSleepNet、SleepTransformer 等把前后 epoch 作为序列输入，利用睡眠阶段转换规律改善预测。
- TransSleep 专门提出 stage-confusion estimator 和 stage-transition detection 辅助任务，用于处理 confusing stages 和 transitioning epochs。
- L-SeqSleepNet、S4Sleep、Mamba/长上下文工作说明整夜结构和长程依赖有价值，但也有研究显示单纯拉长上下文不一定稳定提升。

局限：

- 大多数工作把转期当成序列建模或辅助任务问题，没有把“转期 epoch 的标签应更软、更不确定”作为训练目标核心。
- 如果只是引入长上下文，模型可能学到更强的阶段先验，但仍然用 one-hot 标签强迫边界 epoch 归入单一类别。
- 对 N1 来说，最关键的不是无限长上下文，而是 W-N1-N2 局部边界和转期窗口。

### 2.3 不确定性与多评分员路线

代表工作：

- Dreem Open Datasets 提供 DOD-H 和 DOD-O，多名睡眠技师对同一记录评分，强调自动分期不能只和单一人工标签比较。
- Multi-Scored Sleep Databases / LSSC 使用 soft-consensus distribution 与 label smoothing，把多评分员信息注入训练，目标是保留评分员间分歧。
- DeepSleepNet-Lite 用 MC dropout 估计模型不确定性，并通过拒绝低置信样本提高剩余样本性能。
- SleepTransformer 把 attention 解释和预测熵作为不确定性分析工具。

局限：

- 多评分员数据并不总能覆盖主数据集，如 Sleep-EDF 和 ISRUC 通常只有单一标签。
- LSSC 证明了 soft-consensus 有价值，但没有围绕 N1 的 W-N1-N2 阶段相邻结构设计专门先验。
- DeepSleepNet-Lite 和 SleepTransformer 偏向识别不确定样本或解释模型输出，不等同于训练时显式改善 N1 边界。

### 2.4 Soft label 与 label distribution 路线

通用机器学习和医学标注研究已经反复说明：当类别边界模糊或专家存在分歧时，soft labels 往往比 hard labels 更适合表达监督信号。相关工作包括 soft labels from annotators、inter-rater uncertainty calibration、medical label fusion 等。

对睡眠分期的转化不能直接套普通 label smoothing。普通 label smoothing 会把概率均匀分给所有非真类；但睡眠阶段有明确相邻结构：

- W 与 N1 相邻；
- N1 与 W/N2 相邻；
- N2 与 N1/N3 相邻；
- N3 主要与 N2 相邻；
- REM 与 W/N1 有 EEG-only 混淆风险，但不是 N1 主线。

因此本方向的关键不是“使用 smoothing”，而是“把 AASM 阶段相邻性和转期边界不确定性写进 soft target”。

### 2.5 其他领域类似研究

医学图像分割、病理诊断、放射影像等任务常有多专家标注不一致。其经验对本方向有三点启发：

1. 多专家分布本身是信息，不应过早压成单一 hard label。
2. 校准比单纯 accuracy 更重要；模型如果对边界样本过度自信，临床使用风险更高。
3. soft label 或 label fusion 方法必须与任务结构结合，否则容易变成无差别正则化。

这些经验支持本方向的方法论，但睡眠分期需要自己的结构化版本：阶段相邻矩阵、转期窗口、hypnogram 边界分析。

## 3. 我们可以做的方案

### Baseline group

所有方法固定同一个轻量 backbone，建议先用 compact CNN/TCN 或小型 Transformer。第一阶段不追求架构创新，重点验证训练目标。

必须比较：

- hard-label cross entropy；
- class-weighted cross entropy；
- focal loss；
- balanced sampler；
- uniform label smoothing。

其中 `class-weighted CE` 和 `focal loss` 是为了证明收益不只是类别不均衡补偿；`uniform label smoothing` 是为了证明收益来自阶段结构，而不是泛泛正则化。

### Method A: Stage-Adjacent Soft Label

把 one-hot 标签替换成符合睡眠阶段邻接关系的 soft label。

建议第一版使用可解释的固定矩阵，而不是复杂可学习矩阵：

| 原标签 | soft target 设计 |
|---|---|
| W | 主概率给 W，小概率给 N1 |
| N1 | 主概率给 N1，小概率给 W 和 N2 |
| N2 | 主概率给 N2，小概率给 N1 和 N3 |
| N3 | 主概率给 N3，小概率给 N2 |
| REM | 第一版保持接近 hard label；仅在误差分析中观察 REM-W/N1 混淆 |

需要做的消融：

- smoothing 强度：例如 `epsilon = 0.05 / 0.10 / 0.15`；
- N1-only smoothing vs all-stage adjacent smoothing；
- adjacent smoothing vs uniform smoothing。

### Method B: Transition-Uncertainty Weighting

定义 transition-window：

- 当前 epoch 与前后任一 epoch 标签不同，则当前 epoch 为 transition epoch；
- 或以边界为中心，取前后 `k=1/2/3` 个 epoch 作为 transition-window。

训练策略：

- 对 transition-window 使用更强的 stage-adjacent smoothing；
- 或降低 hard-label CE 权重，避免模型过拟合单一人工标签；
- 或引入一个辅助 uncertainty head，预测该 epoch 是否靠近阶段边界。

注意：转期样本不一定要更高权重。更高权重会让模型更用力拟合不确定标签，可能适得其反。本方向更合理的说法是“降低边界样本的 hard-label 置信度”。

### Method C: Soft-Consensus / Teacher Soft Labels

如果有多评分员标签，优先使用真实评分分布；如果主数据集没有多评分员标签，则用 teacher ensemble 作为代理。

可执行版本：

- 在训练集上做 K-fold baseline；
- 对每个 epoch 收集多个 teacher 的概率输出；
- 以 teacher entropy 或 disagreement 衡量不确定性；
- 高不确定样本使用 teacher soft target 或更强 adjacent smoothing。

定位：

- C 不作为第一版硬依赖，因为多评分员数据获取和接入成本更高。
- C 可作为增强实验，用来验证人工设定的 stage-adjacent smoothing 是否接近真实评分分歧。

### Method D: Hybrid A+B

第一篇文章主方法建议采用 A+B：

> Stage-adjacent soft labels for all epochs + stronger transition softening for W-N1/N1-N2 boundary epochs.

这个组合足够聚焦：它不依赖大模型，不依赖多评分员主数据，也不把跨数据集泛化硬塞进主贡献。若结果成立，论文论点会清楚：N1 的提升来自对边界标签不确定性的显式建模。

## 4. 实验 PLAN

### 4.1 数据设置

第一阶段：

- Sleep-EDF：最小可复现起点；
- ISRUC：第二数据集复现实验。

暂不把 MASS/SHHS 设为第一阶段必需项。它们适合作为后续扩展验证，不应阻塞第一版实验。

评测设置：

- 主设置：subject-independent within-dataset evaluation；
- 复现实验：Sleep-EDF 和 ISRUC 分别独立跑同一协议；
- 补充鲁棒性：Sleep-EDF -> ISRUC、ISRUC -> Sleep-EDF，仅作为 robustness check，不作为主论文标题。

### 4.2 模型设置

backbone 固定，建议二选一：

- 轻量 CNN/TCN：实现简单，便于突出 loss/label 贡献；
- 小型 Transformer：便于与 SleepTransformer/TransSleep 叙事对齐，但要控制参数量。

输入：

- 第一版建议 EEG-only 或单通道 EEG，避免多模态把 N1 问题混成 EOG/EMG 问题；
- 如使用 ISRUC 多通道，需固定一个可与 Sleep-EDF 对齐的 EEG 通道或做通道选择实验。

### 4.3 实验矩阵

| 组别 | 方法 | 目的 |
|---|---|---|
| B0 | hard CE | 最基础 baseline |
| B1 | class-weighted CE | 排除纯类别不均衡解释 |
| B2 | focal loss | 排除 hard-example mining 解释 |
| B3 | balanced sampler | 排除采样策略解释 |
| B4 | uniform label smoothing | 排除普通正则化解释 |
| A | stage-adjacent soft label | 验证阶段相邻结构 |
| B | transition uncertainty weighting | 验证转期边界不确定性 |
| D | A+B hybrid | 第一版主方法 |
| C | teacher/multi-rater soft label | 增强实验或第二阶段 |

### 4.4 指标

主指标：

- N1 F1；
- N1 precision / recall；
- macro-F1；
- Cohen's kappa；
- expected calibration error (ECE)；
- W<->N1、N1<->N2 混淆。

专项指标：

- transition-window N1 F1；
- stable-vs-transition performance gap；
- N1 overprediction rate；
- N1 predicted proportion vs true proportion；
- boundary-adjacent ECE。

这些指标能避免一个常见假象：模型只是更多预测 N1，导致 N1 recall 上升但 precision、macro-F1 或校准变差。

### 4.5 成功标准

相对 hard CE、class-weighted CE、focal loss：

- N1 F1 或 transition-window N1 F1 稳定提升；
- macro-F1 和 kappa 不明显下降；
- ECE 不恶化，最好改善；
- N1 overprediction rate 不显著升高；
- W<->N1、N1<->N2 混淆结构更合理。

## 5. 可验证假设

### H1：阶段相邻 soft label 优于 hard CE 和 uniform smoothing

预期结果：

- N1 F1 提升；
- ECE 降低；
- N1 recall 提升同时 precision 不明显下降。

失败解释：

- 如果只提升 recall 但 precision 大幅下降，说明 smoothing 太强或 N1 概率分配过高；
- 如果 uniform smoothing 同样有效，说明收益可能来自正则化而非阶段相邻结构，需要调整实验论点。

### H2：转期不确定性建模优先改善 transition-window N1

预期结果：

- transition-window N1 F1 上升；
- stable epoch 性能基本保持；
- boundary-adjacent ECE 改善。

失败解释：

- 如果稳定样本下降明显，说明 transition-window 定义过宽或降权过强；
- 如果转期不改善，说明仅用标签变化定义 transition 太粗，需要 teacher entropy 或多评分员分布。

### H3：teacher/multi-rater soft labels 是固定相邻 smoothing 的上界或校准器

预期结果：

- 在有多评分员或 teacher ensemble 时，soft-consensus 优于固定矩阵；
- 固定 stage-adjacent smoothing 接近 soft-consensus 的低成本代理。

失败解释：

- 如果 teacher soft labels 不优，可能 teacher 继承了 hard-label bias；
- 如果多评分员分布与相邻矩阵差异很大，需要重新估计阶段相邻先验。

## 6. 论文定位

建议标题方向：

> Uncertainty-Aware Stage-Adjacent Soft Labels for Improving N1 Sleep Stage Recognition from EEG

中文主线：

> 面向 N1 标签不确定性的阶段相邻软标签与转期边界建模。

本文不主张解决所有跨数据集泛化问题，而是主张：

1. N1 的困难不能只用类别不均衡解释；
2. N1 的 W-N1-N2 边界具有结构性标签不确定性；
3. 显式把这种不确定性纳入训练目标，可以比 hard label 和普通不均衡处理更稳定地改善 N1。

## 7. 下一步执行顺序

1. 写数据统计脚本：每个数据集的阶段比例、N1 占比、转期比例、W-N1/N1-N2 边界数量。
2. 写指标脚本：N1 F1、transition-window N1 F1、ECE、N1 overprediction rate、相邻混淆矩阵。
3. 跑 Sleep-EDF hard CE / class-weighted CE / focal loss。
4. 加 uniform smoothing 与 stage-adjacent smoothing。
5. 加 transition-window smoothing / weighting。
6. 在 ISRUC 复现同一协议。
7. 最后再做 Sleep-EDF <-> ISRUC 外部鲁棒性检查。

## 8. 关键参考

- Dreem Open Datasets: https://arxiv.org/abs/1911.03221
- Multi-Scored Sleep Databases / LSSC: https://arxiv.org/abs/2207.01910
- DeepSleepNet-Lite: https://arxiv.org/abs/2108.10600
- SleepTransformer: https://arxiv.org/abs/2105.11043
- TransSleep: https://arxiv.org/abs/2203.12590
- MSDAN: https://arxiv.org/abs/2107.08442
- SleepEGAN: https://arxiv.org/abs/2307.05362
- Context-Aware Temporal Modeling: https://arxiv.org/abs/2512.22976
- Soft labels from annotators: https://arxiv.org/abs/2207.00810
- Inter-rater uncertainty in medical labels: https://arxiv.org/abs/2202.07550
