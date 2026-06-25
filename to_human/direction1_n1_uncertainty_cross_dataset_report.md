# 方向1专题汇报：N1标签不确定性与跨数据集泛化

日期：2026-06-25  
范围：EEG/含 EEG PSG 自动睡眠分期；重点为 N1、转期、标签不确定性和跨数据集泛化。  
本轮不下载数据、不训练模型；目标是把研究问题收敛成可执行实验方案。

## 1. “跨数据集泛化”到底是什么意思

跨数据集泛化不是一个模型名称，而是一种评测设置。核心问题是：

> 模型在一个或几个数据集上训练后，能否在另一个从未见过的数据集上保持性能？

常见设置如下：

| 设置 | 示例 | 能说明什么 | 风险 |
|---|---|---|---|
| within-dataset | Sleep-EDF 训练，Sleep-EDF 测试 | 模型是否能拟合同一数据集分布 | 容易高估真实应用能力 |
| cross-subject | Sleep-EDF 部分被试训练，其他被试测试 | 是否泛化到新被试 | 仍共享设备、导联、评分协议 |
| cross-dataset | Sleep-EDF 训练，ISRUC/MASS/SHHS 测试 | 是否泛化到新中心、新设备、新人群 | 难度高，更接近真实部署 |
| leave-one-dataset-out | Sleep-EDF+ISRUC 训练，MASS 测试，并轮换 | 多源训练对未知目标域的泛化 | 需要统一预处理和标签映射 |

睡眠分期里，跨数据集比同数据集更关键，原因是不同数据集在导联、采样率、滤波、设备、人群、疾病构成、评分员和预处理规则上都可能不同。模型如果只在 Sleep-EDF 内部拿高 accuracy，可能学到的是 Sleep-EDF 的数据风格，而不是稳定的睡眠生理规律。

SleepDG 把这个问题正式定义为 generalizable sleep staging，并在多个公开数据集上做 domain generalization；STDA-Net、SleepDIFFormer、FF-TRUST 进一步把跨数据集问题扩展到 domain adaptation、异构 EEG/EOG 和 noisy labels。

## 2. N1为什么难：五层原因图谱

### 2.1 生理层：N1 是过渡态，不是稳定态

N1 是从清醒进入睡眠的浅睡过渡期。它的 EEG 特征通常是 alpha 减少、theta 增加、低幅混合频率增强，但这些变化是连续的，不像 N2 的 sleep spindle/K-complex 或 N3 的慢波那样有强判据。

这导致一个关键事实：**N1 本身就不适合被当成边界清晰的硬类别**。30 秒 epoch 里可能前半段还像 W，后半段才像 N1；也可能 N1 快速进入 N2。

### 2.2 标注层：N1 与转期 epoch 的人工一致性低

睡眠分期通常用单一人工标签训练模型，但人工评分员之间并非完全一致。Dreem Open Datasets 提供 DOD-H/DOD-O 多评分员数据，每条记录由 5 位睡眠技师评分，并指出传统自动分期研究经常只和单一人工标签比较，这会掩盖标签不确定性。

N1、短暂觉醒、W-N1-N2 边界最容易出现分歧。对模型来说，这类样本被强制训练成 one-hot label，会产生两个问题：

- 模型学到过度自信的边界；
- 对外部数据集评分习惯变化非常敏感。

### 2.3 数据层：N1 样本少，类别不均衡严重

N2 通常占比最大，N1 占比小。普通 cross entropy 会偏向多数类，模型把 N1 预测成 W 或 N2 仍然能保持不错的 overall accuracy。

这解释了为什么很多论文总体 accuracy 很高，但 N1 F1 仍然低。SleepEGAN、BiT-MamSleep、Context-aware N1 temporal modeling 等工作都把 class imbalance 作为 N1 的重要原因之一。

### 2.4 模型层：单 epoch 模型缺少转期上下文

人类评分员通常会参考前后 epoch。模型如果只看 30 秒片段，很难判断它是短暂觉醒、N1 开始、N2 前奏，还是 REM/W 的 EEG-only 混淆。

SleepTransformer、DeepSleepNet-Lite、Context-aware temporal modeling、AnySleep 等方向都说明上下文是必要的。但单纯把上下文加长不一定足够；S4Sleep 长程相关分析提醒我们，关键不只是“看得更长”，而是要对转期边界建模。

### 2.5 评测层：常规指标掩盖 N1 问题

如果只看 accuracy，N1 错误会被 N2 多数类掩盖。更合理的评测必须包含：

- N1 F1；
- W↔N1、N1↔N2 混淆；
- transition-window F1；
- macro-F1；
- calibration / ECE；
- cross-dataset N1 F1。

## 3. 三类问题必须分开

方向1的关键是不能把所有问题都归结为“模型不够强”。至少要区分三类机制：

| 机制 | 表现 | 典型解决方案 | 局限 |
|---|---|---|---|
| Class imbalance | N1 样本少，模型偏向 N2/W | class weight、focal loss、SMOTE/GAN、balanced sampler | 只解决数量，不解决标签模糊 |
| Label uncertainty | 人工评分分歧，转期标签本身不稳定 | soft label、multi-rater consensus、uncertainty loss、reject option | 需要不确定性来源或代理规则 |
| Domain shift | 换数据集/设备/人群后性能下降 | domain alignment、DG、TTA、source selection、SSL/pretraining | 可能牺牲源域性能，且和 label shift 纠缠 |

真正有研究价值的点在三者交叉处：**N1 少样本 + N1 标签不确定 + 外部数据集分布变化**。这也是为什么普通 hard-label CE 在外部数据集上容易崩。

## 4. 现有方法矩阵

| 路线 | 代表工作 | 解决什么 | 对方向1的启发 |
|---|---|---|---|
| 多尺度特征/注意力 | MSDAN | N1 特征弱、局部波形多样 | 可作为结构增强 baseline，但不足以证明跨域 |
| 类别不均衡增强 | SleepEGAN | N1 少样本 | 要和 label uncertainty 区分，不能只做数据增强 |
| 不确定性估计 | DeepSleepNet-Lite, SleepTransformer | 识别低置信 epoch | 可用于拒识、样本降权、teacher soft labels |
| 多评分员/共识标签 | Dreem Open Datasets | 人工标签分歧 | 支持 soft label 和 uncertainty-aware evaluation |
| 上下文建模 | SleepTransformer, Context-aware N1 modeling, AnySleep | 转期依赖和序列结构 | 需要单独评估转期窗口 |
| 域泛化 | SleepDG, SleepDIFFormer | 未见数据集泛化 | 推荐采用 leave-one-dataset-out |
| 测试时适配 | StableSleep, SPDIM | 部署后目标域漂移 | 可作为外部数据集适配对照 |
| 噪声标签 + 域泛化 | FF-TRUST | domain shift 和 noisy labels 共存 | 最接近本方向的竞争基线 |
| 可穿戴 SSL | Wearable EEG SSL evaluation | 少标签、居家 EEG | 可作为未来扩展，不是第一版核心 |
| 基础模型评测 | REVE, Hypnos, EEG FM evaluation | 大规模预训练迁移 | 适合后续比较 adapter，不建议第一版从零训练 |

## 5. 其他阶段是否有类似问题

### REM：类似 N1 的边界和模态依赖问题

REM 的 EEG 可能和 W/N1 接近，真正区分 REM 往往需要 EOG 和 EMG。EEG-only 模型容易把 REM 与 W/N1 混淆。PD/iRBD 等疾病还会改变 REM 相关生理表现，使普通模型泛化变差。

可尝试方案：

- 多模态 EEG+EOG/EMG；
- REM-specific uncertainty；
- 疾病人群 fine-tuning；
- confidence threshold 保留高置信 REM，用于临床指标计算。

### W：短暂觉醒和伪迹问题

W 在整夜睡眠中并不总是稳定清醒，可能是短暂觉醒、闭眼清醒或运动伪迹。模型容易把低质量 EEG 或短暂觉醒误判成 N1/REM。

可尝试方案：

- 信号质量检测；
- wake intrusion 专项评估；
- abstention / reject option；
- 转期上下文建模。

### N2：多数类掩盖问题

N2 样本多，整体看起来容易，但它和 N1/N3 的边界很关键。模型偏向 N2 会抬高 accuracy，但损害 N1/N3。

可尝试方案：

- 分阶段混淆矩阵；
- N1↔N2 和 N2↔N3 边界专项指标；
- spindle/K-complex 证据对齐。

### N3：年龄和疾病域偏移问题

N3 的慢波判据更强，但老年人、神经疾病、药物影响下慢波幅度和结构会变。跨年龄/跨疾病时，N3 也可能出现域偏移。

可尝试方案：

- 年龄/疾病分层评估；
- 频域归一化；
- domain adaptation；
- 慢波证据解释。

## 6. 实验蓝图

### 6.1 数据组合

默认最小组合：

- Sleep-EDF：入门和复现方便；
- ISRUC：多通道、多类公开 PSG，适合跨数据集测试；
- MASS 或 SHHS：作为扩展外部验证。

如果只做两数据集，建议：

- Train Sleep-EDF → Test ISRUC；
- Train ISRUC → Test Sleep-EDF；
- 每个数据集内部做 subject-independent split。

如果做三数据集，建议：

- Train Sleep-EDF + ISRUC → Test MASS/SHHS；
- Train Sleep-EDF + MASS/SHHS → Test ISRUC；
- Train ISRUC + MASS/SHHS → Test Sleep-EDF。

### 6.2 基线

必须包括：

- hard-label cross entropy；
- class-weighted cross entropy；
- focal loss；
- balanced sampler；
- 小型 CNN/TCN 或 compact Transformer。

推荐模型不要太复杂。第一版目标是验证训练目标和评测协议，而不是追求架构 SOTA。

### 6.3 拟提出方法

**方法 A：阶段相邻 label smoothing**

把 one-hot 标签替换为符合阶段邻接关系的 soft label。例如：

- N1：主概率给 N1，少量概率分给 W 和 N2；
- N2：主概率给 N2，少量概率分给 N1 和 N3；
- N3：主概率给 N3，少量概率分给 N2；
- REM：主概率给 REM，少量概率分给 W/N1，用于处理 EEG-only 混淆。

这不是医学真值，而是待验证的 inductive bias。需要和普通 label smoothing 对比。

**方法 B：转期感知 sample weighting**

定义 transition epoch：当前 epoch 标签与前一个或后一个 epoch 不同。训练时不要简单提高其权重，而是降低 hard-label 过拟合，例如：

- 对转期 epoch 使用更强 smoothing；
- 或降低其 loss 权重；
- 或单独输出 transition uncertainty。

**方法 C：teacher soft labels**

训练多个 baseline 或用 cross-validation teacher，对每个 epoch 生成 soft label。高分歧样本视为 uncertain。若有 multi-rater 数据，可用真实评分分布替代 teacher。

### 6.4 评测指标

主指标：

- macro-F1；
- Cohen's kappa；
- N1 F1；
- REM F1；
- transition-window F1；
- ECE / calibration error。

错误分析：

- W↔N1；
- N1↔N2；
- REM↔W/N1；
- 稳定 epoch vs 转期 epoch；
- within-dataset vs cross-dataset 性能差。

## 7. 三个可落地实验假设

### H1：阶段相邻 soft label 能提升外部数据集 N1 F1 和校准

**假设**：N1 的标签边界具有结构性不确定性。按阶段邻接关系做 soft label，比 hard-label CE 和普通 uniform label smoothing 更适合外部数据集。

**最小实验**：Sleep-EDF 训练，ISRUC 测试；模型用同一个小型 TCN/Transformer；比较 hard CE、uniform smoothing、stage-adjacent smoothing。

**预期结果**：cross-dataset N1 F1、macro-F1、ECE 改善；overall accuracy 可能不明显提升。

**失败解释**：如果 N1 性能不升，可能是目标数据集导联/预处理差异主导，而不是标签边界主导；需要加入 domain alignment 或统一预处理。

### H2：转期感知训练能改善 transition-window F1

**假设**：模型在稳定 epoch 上已经足够强，主要错误集中在转期附近。对转期 epoch 使用更强 smoothing 或 loss 降权，能减少过度自信错误。

**最小实验**：在 Sleep-EDF 内部 subject-independent split 先验证，再做 Sleep-EDF→ISRUC。按标签前后变化定义 transition-window。

**预期结果**：transition-window F1 和 calibration 改善，稳定 epoch 表现不显著下降。

**失败解释**：如果稳定 epoch 下降明显，说明降权策略太强；如果转期不升，说明 transition proxy 太粗，需要基于概率/teacher uncertainty 定义。

### H3：标签不确定性与多源域泛化要联合处理

**假设**：只做 domain alignment 会忽略不同数据集的评分习惯和 label noise；只做 label smoothing 又不能处理信号分布差异。两者联合才会在 leave-one-dataset-out 下稳定改善。

**最小实验**：Sleep-EDF + ISRUC 训练，MASS/SHHS 测试；比较 hard CE、多源 domain alignment、stage-adjacent smoothing、两者组合。

**预期结果**：组合方法在 macro-F1、N1 F1、REM F1 和 ECE 上最稳。

**失败解释**：如果组合无效，可能是源域之间差异太大或对齐损害阶段判别特征；需要做 source selection，如 SelectiveFinetuning 的思路。

## 8. 推荐下一步

下一步不要直接堆新模型。建议先做一个小型、可复现的实验协议：

1. 固定 Sleep-EDF + ISRUC。
2. 统一标签映射 W/N1/N2/N3/REM 和采样率。
3. 复现 hard CE、class-weighted CE、focal loss。
4. 加入 stage-adjacent smoothing 和 transition-aware smoothing。
5. 报告 N1 F1、REM F1、macro-F1、kappa、ECE、transition-window F1。

如果这一版能证明 “N1 的主要收益来自标签不确定性建模，而不只是类别重加权”，就具备进一步扩展到 MASS/SHHS 和多源 domain generalization 的价值。

## 9. 关键参考

- SleepDG / Generalizable Sleep Staging: https://arxiv.org/abs/2401.05363
- FF-TRUST / Noisy Labels + Multi-Source DG: https://arxiv.org/abs/2604.10009
- STDA-Net / Cross-Dataset DA: https://arxiv.org/abs/2605.06736
- SleepDIFFormer / Cross-Domain EEG/EOG: https://arxiv.org/abs/2508.15215
- Dreem Open Datasets / Multi-Scored Labels: https://arxiv.org/abs/1911.03221
- DeepSleepNet-Lite / Uncertainty: https://arxiv.org/abs/2108.10600
- SleepTransformer / Interpretability + Uncertainty: https://arxiv.org/abs/2105.11043
- MSDAN / N1 Attention: https://arxiv.org/abs/2107.08442
- SleepEGAN / Imbalance: https://arxiv.org/abs/2307.05362
- Context-Aware N1 Temporal Modeling: https://arxiv.org/abs/2512.22976
- StableSleep / Test-Time Adaptation: https://arxiv.org/abs/2509.02982
- Wearable EEG SSL Evaluation: https://arxiv.org/abs/2510.07960
