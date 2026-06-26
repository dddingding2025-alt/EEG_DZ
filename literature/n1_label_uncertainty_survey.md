# N1 标签不确定性专题文献报告

日期：2026-06-26  
用途：支撑“通过阶段相邻软标签与转期不确定性建模提升 N1 睡眠阶段识别”的选题与实验设计。  
范围：自动睡眠分期、N1 难题、多评分员/标签不确定性、soft label、转期建模和相关医学标签不确定性方法。

## 1. 研究定位

本方向不再把跨数据集泛化作为核心机制。跨数据集验证仍然保留，但只用于回答“方法是否鲁棒”；主问题是 N1 的标签边界是否应从 one-hot hard label 改为结构化不确定监督。

核心因果链：

1. N1 是 W 到 N2 的过渡阶段，生理边界连续。
2. N1 样本占比低，模型容易偏向 W/N2。
3. N1 与 W/N2 的人工评分一致性较低，单一 hard label 会放大评分员主观性。
4. 转期 epoch 的 30 秒窗口内可能混合多个阶段证据。
5. 因此，阶段相邻 soft label 与转期不确定性建模有明确任务结构依据。

## 2. 类别不均衡路线

| 工作 | 主要做法 | 与 N1 的关系 | 对本方向的启发 | 局限 |
|---|---|---|---|---|
| MSDAN, 2021 | 多尺度卷积 + dual attention + soft thresholding | 明确指出 N1 性能不足，并报告 N1 F1 提升 | N1 需要更强局部波形和注意力特征 | 仍是 hard-label 分类，未建模标签模糊 |
| SleepEGAN, 2023 | GAN 生成少数类样本 + ensemble | 直接针对 sleep stage class imbalance | 必须作为不均衡路线对照 | 生成更多 N1 不等于解决 N1/W/N2 边界不确定 |
| Context-Aware Temporal Modeling, 2025 | 多尺度时间编码、层级上下文、class-weighted loss、增强 | 专门强调 N1 识别改善 | 可作为 N1-focused baseline | 主要从表示学习和不均衡处理出发 |
| BiT-MamSleep, 2024 | Mamba 序列结构与不均衡处理 | 说明序列模型也关注少数类问题 | 可作为强模型背景 | 若只换结构，无法证明 label uncertainty 贡献 |

结论：类别不均衡是 N1 难题的一部分，但不能替代标签不确定性。实验必须包含 class-weighted CE、focal loss 和 balanced sampler，否则无法证明 soft label 的独立价值。

## 3. 转期与上下文路线

| 工作 | 主要做法 | 与 N1/转期的关系 | 对本方向的启发 | 局限 |
|---|---|---|---|---|
| DeepSleepNet | CNN + RNN 序列上下文 | 利用前后 epoch 评分线索 | 证明上下文是强基线 | hard label 训练仍然存在 |
| SleepTransformer, 2021 | Transformer + attention + uncertainty entropy | 同时提供上下文、解释和不确定性分析 | 可借鉴熵/ECE分析 | 不专门设计 N1 相邻 soft target |
| TransSleep, 2022 | stage-confusion estimator + stage-transition detection 辅助任务 | 直接针对 confusing transitioning epochs | 是最接近的转期建模近邻 | 转期用于辅助任务，而非标签软化主目标 |
| L-SeqSleepNet, 2023 | whole-cycle sequence modeling | 支撑更长睡眠周期上下文 | 可作为长上下文背景 | 主问题不是 N1 label uncertainty |
| S4Sleep / Long-range correlation, 2023-2024 | 状态空间和长程相关分析 | 检验长上下文是否必要 | 提醒不要简单认为越长越好 | 与标签不确定性关系间接 |

结论：上下文是必要背景，但本方向要避免写成“又一个序列模型”。创新点应是：在同样 backbone 和上下文长度下，改变 N1/转期样本的监督目标。

## 4. 多评分员与不确定性路线

| 工作 | 主要做法 | 关键证据 | 对本方向的启发 | 局限 |
|---|---|---|---|---|
| Dreem Open Datasets, 2019/2020 | DOD-H 与 DOD-O，每条记录由多名技师评分 | 自动分期常与单一人工标签比较，但人工一致性有限 | 多评分员分布可作为 N1 不确定性证据 | 数据是头带/特定设备，未必直接替代 Sleep-EDF/ISRUC |
| Multi-Scored Sleep Databases / LSSC, 2022/2023 | label smoothing + soft-consensus distribution | 利用多评分员信息训练模型，并改善与共识 hypnodensity 的一致性 | 直接支持 soft label 训练睡眠分期 | 没有围绕 W-N1-N2 边界做 N1-specific 设计 |
| DeepSleepNet-Lite, 2021 | MC dropout 估计模型不确定性，拒绝 uncertain instances | 不确定性可识别低置信样本，拒识后性能上升 | 可用于 teacher entropy 或不确定样本分析 | 主要是推理阶段拒识，不是训练目标设计 |
| SleepTransformer, 2021 | 预测熵与 attention 解释 | 提供模型不确定性和可解释性视角 | 可用于 calibration 与错误分析 | 不直接解决 N1 hard label 问题 |

结论：已有睡眠分期研究已经承认评分分歧与模型不确定性，但缺少一个 N1-centered 的训练目标设计。LSSC 是最直接方法论证据；我们的差异是把 soft target 从“多评分员共识”扩展为“阶段相邻先验 + 转期边界强不确定性”。

## 5. Soft label 与 label distribution 路线

| 工作/方向 | 核心观点 | 与本方向的连接 |
|---|---|---|
| Eliciting and Learning with Soft Labels from Every Annotator | soft labels 可改善泛化、鲁棒性和校准；个体标注者也能提供类别不确定性 | 支持不把人工标签压成 one-hot |
| Label distribution learning | 类别概率分布比单一类别更能表达模糊样本 | N1 epoch 可视作 W/N1/N2 概率分布 |
| Confidence penalty / label smoothing | 减少模型过度自信 | baseline 必须包含 uniform smoothing |
| Knowledge distillation / teacher soft labels | teacher 概率可作为软监督 | 可在无多评分员数据时生成代理 soft labels |

转化原则：

- 不使用无结构的 uniform smoothing 作为主方法。
- 用睡眠阶段相邻矩阵定义 soft target。
- 对 N1 与 W/N2 边界使用更强 smoothing。
- 用校准指标检查 soft target 是否真正降低过度自信。

## 6. 医学标签不确定性类比

医学图像和临床诊断任务中，多专家分歧很常见。Label fusion、SoftSeg、多专家平均、随机专家采样、STAPLE 等方法都试图保留或建模专家间分歧。其可迁移经验如下：

| 经验 | 对睡眠分期的对应 |
|---|---|
| 单一专家标签会把主观性转移给模型 | 单一睡眠技师评分会让模型拟合个人边界习惯 |
| soft label 能改善校准和不确定性表达 | N1/W/N2 边界应评估 ECE 和 boundary ECE |
| 多专家分歧应作为信号而非噪声丢弃 | DOD/LSSC 可用于验证 N1 soft target 设计 |
| 任务结构很重要 | 睡眠阶段有相邻顺序，不能直接套均匀 smoothing |

结论：医学标签不确定性支持本方向，但不能替代睡眠领域证据。论文中应把它作为方法论背景，而不是主要实验依据。

## 7. 现有研究缺口

1. N1-focused 工作多用结构增强、class weight 或数据增强，较少把 N1 标签模糊作为核心训练目标。
2. 转期建模工作多把边界作为辅助任务，较少改变转期 epoch 的标签置信度。
3. 多评分员工作证明 soft-consensus 有效，但尚未围绕 W-N1-N2 阶段相邻边界设计低成本代理方法。
4. 很多论文报告 macro-F1 或 overall accuracy，但缺少 transition-window N1 F1、N1 overprediction rate、boundary calibration。
5. 跨数据集泛化工作解决的是 domain shift，不应与 N1 label uncertainty 混为一个问题。

## 8. 推荐实验设计

主线：

- 固定 backbone。
- 固定 subject-independent split。
- 先在 Sleep-EDF 做完整 baseline。
- 在 ISRUC 独立复现。
- 最后才做 Sleep-EDF <-> ISRUC robustness check。

实验组：

- hard CE；
- class-weighted CE；
- focal loss；
- balanced sampler；
- uniform smoothing；
- stage-adjacent smoothing；
- transition-window smoothing/weighting；
- hybrid A+B；
- optional teacher/multi-rater soft labels。

指标：

- N1 F1；
- N1 precision/recall；
- macro-F1；
- kappa；
- ECE；
- W<->N1、N1<->N2 混淆；
- transition-window N1 F1；
- stable-vs-transition gap；
- N1 overprediction rate。

## 9. 关键参考

- Dreem Open Datasets: https://arxiv.org/abs/1911.03221
- Multi-Scored Sleep Databases / LSSC: https://arxiv.org/abs/2207.01910
- SleepTransformer: https://arxiv.org/abs/2105.11043
- DeepSleepNet-Lite: https://arxiv.org/abs/2108.10600
- MSDAN: https://arxiv.org/abs/2107.08442
- TransSleep: https://arxiv.org/abs/2203.12590
- SleepEGAN: https://arxiv.org/abs/2307.05362
- Context-Aware Temporal Modeling: https://arxiv.org/abs/2512.22976
- Soft labels from annotators: https://arxiv.org/abs/2207.00810
- Inter-rater uncertainty in medical labels: https://arxiv.org/abs/2202.07550
