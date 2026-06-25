# 转期感知长上下文 EEG 睡眠分期：第二轮深入汇报

日期：2026-06-25  
目标：判断“转期感知的长上下文睡眠分期”是否适合作为第一篇文章，并把研究点细化到可实验验证。

## 1. 结论先行

这个方向适合作为第一篇文章，但需要控制叙事重点。

不建议把文章写成“我们提出一个更长上下文 Transformer”。这条线已经有 SleepTransformer、SeqSleepNet/L-SeqSleepNet、S4Sleep、Mamba、NeuroLingua 等大量工作。更稳妥的文章定位是：

> **把睡眠分期从普通 epoch-level 分类，重新聚焦到 transition-centered evaluation：哪些阶段转换真正需要上下文，什么样的轻量序列约束能减少边界错误。**

这个定位的好处是：实现成本低、实验故事清晰、能绕开“纯模型结构创新不足”的问题，也能把 N1 难识别、转期不确定性、hypnogram 碎片化这些领域痛点串起来。

## 2. 现在大家是怎么做的

### 2.1 经典序列建模：CNN 提特征，RNN/Transformer 学上下文

DeepSleepNet、SeqSleepNet、IITNet、XSleepNet 这类工作把睡眠分期从单 epoch 分类推进到 sequence-to-sequence。典型逻辑是：

- 先用 CNN、滤波器或频谱编码提取每个 30 秒 epoch 的局部特征；
- 再用 BiLSTM、RNN、Transformer 或 attention 学习相邻 epoch 关系；
- 最后仍按每个 epoch 的 W/N1/N2/N3/REM 标签计算 accuracy、macro-F1、kappa。

这条线证明了上下文有价值。IITNet 报告短上下文已经能明显提升 N1、REM 等阶段，但上下文长度超过几个 epoch 后收益变小。这对我们很关键：**上下文不是越长越好，第一篇文章应该验证“转期需要多长上下文”。**

### 2.2 转期显式建模：代表是 TransSleep，但空间还没被吃完

TransSleep 是最直接的近邻工作。它把 transitioning epochs 和 confusing stages 作为关键问题，设计了：

- multi-scale feature extractor；
- stage-confusion estimator；
- context encoder；
- stage-transition detection 辅助任务。

它说明“转期感知”不是空白点。但它仍主要用常规 sleep staging 指标讲结果，缺少系统的 transition-window 指标、boundary delay、hypnogram fragmentation 等评测。我们的切入点不是重复它的辅助任务，而是建立更明确的边界评估和轻量正则框架。

### 2.3 Whole-cycle 长上下文：L-SeqSleepNet 是强近邻

L-SeqSleepNet 从睡眠约 90 分钟周期出发，做 whole-cycle long sequence modeling。它在多个数据库和不同 EEG setup 上验证，并报告对 N2 主导问题和低性能被试的鲁棒性改善。

它给我们两个启发：

- 90 分钟 whole-cycle 是合理实验条件，不是随便定的长度；
- 如果只说“睡眠有周期，所以我们用 90 分钟上下文”，创新性已经不够。

因此我们的实验应把 90 分钟作为一个对照长度，而不是唯一贡献。

### 2.4 S4/Mamba 等长序列模型：高效，但不自动等于更有用

S4Sleep 系列工作系统探索了 encoder-predictor 设计空间，并用 structured state space model 做序列建模。后续 “Assessing the importance of long-range correlations” 进一步测试把输入拉长到数百 epoch，结论是单纯增加上下文没有明显收益。

这对我们的选题是约束，也是机会。文章不能假设“长上下文必然更好”。更有价值的问题是：

- W-N1-N2 边界需要几分钟上下文？
- N2-N3 边界是否主要由局部慢波决定？
- NREM-REM 转换是否需要更长的睡眠周期信息？
- 超长上下文是否只改善少数被试或特定转期？

### 2.5 高分辨率和连续睡眠表征：说明 30 秒标签本身有问题

AnySleep 指出 30 秒 epoch 是传统 PSG 评分习惯，并不是生理上的自然边界，且模型可以做 adjustable temporal resolution。Continuous sleep depth 工作则说明睡眠深度可能更像连续变量，而不是硬切成五类。

这为我们提供了理论动机：转期窗口不是简单“难样本”，而是离散标签对连续生理状态的粗切分。第一版实验仍可使用 30 秒 hypnogram，但评测必须承认边界附近标签更不稳定。

## 3. 现有工作的主要问题

### 问题 1：评测目标和临床痛点不匹配

多数论文优化 overall accuracy、macro-F1、kappa。它们可以证明模型整体不错，但回答不了：

- 模型是否把阶段转换提前或滞后了？
- 模型是否把一段稳定 N2 切成很多碎片？
- 模型是否把短觉醒抹平了？
- 模型是否在 W-N1-N2 这种关键入睡边界上改善？

这些问题对 hypnogram 质量更直接，但常规指标不敏感。

### 问题 2：上下文长度比较不系统

已有工作常选择某个上下文长度，然后报告性能。少数工作比较长度，但仍主要看总体指标。真正应该比较的是：

- 单 epoch 是否足够区分 N2-N3？
- 5 分钟上下文是否足够改善 N1？
- 30 分钟上下文是否帮助 NREM-REM？
- 90 分钟 whole-cycle 是否只在 REM 周期或异常被试上有效？

如果不按转期类型拆开看，很容易得出“长上下文没用”或“长上下文有用”的粗糙结论。

### 问题 3：序列平滑可能制造新的错误

很多 sequence model 或 post-processing 会让 hypnogram 更平滑。平滑能减少孤立误判，但也可能：

- 抹掉真实短觉醒；
- 延迟阶段转换；
- 降低 N1 召回；
- 把模型错误伪装成更稳定的 hypnogram。

所以 sequence regularization 不能无差别施加，必须 boundary-aware。

### 问题 4：N1 难题和转期难题没有被统一处理

N1 难识别不是单纯类别不均衡。它本质上是清醒到睡眠的过渡阶段，人工标注也更不稳定。把 N1 当作普通少数类，只靠 class weighting 或 SMOTE，可能改善有限。

更合理的处理方式是把 N1 放在 W-N1-N2 转换链条里分析：模型到底是把 N1 判成 W，还是直接跳到 N2？这种错误是否发生在真实边界附近？

## 4. 我们可以怎么入手

### 入手点 A：建立 transition-centered evaluation protocol

这是最低成本、最稳的贡献。定义一套只依赖 hypnogram 标签和模型概率输出的转期指标：

- **transition-window macro-F1**：只在真实边界前后 k 个 epoch 内计算 macro-F1。
- **per-transition F1**：分别看 W-N1、N1-N2、N2-N3、N2-REM、REM-W 等常见转换。
- **boundary delay**：真实边界和最近预测边界的偏移，单位为 epoch。
- **transition precision/recall**：把 `label_t != label_{t-1}` 当作边界检测事件。
- **noncanonical transition rate**：预测序列中训练集低频跳变的比例。注意不要绝对称 illegal，因为病理睡眠可能出现非常规跳变。
- **fragmentation error**：预测每小时转移次数与真实 hypnogram 的差异。
- **transition calibration**：用相邻 epoch 概率分布估计 change probability，评估 Brier/ECE。

这套指标不需要额外人工标注，能快速落地。

### 入手点 B：比较“上下文长度 × 转期类型”

固定一个轻量 backbone，比较：

- 30 秒单 epoch；
- 5 分钟上下文，约 10 个 epoch；
- 30 分钟上下文，约 60 个 epoch；
- 90 分钟 whole-cycle，约 180 个 epoch；
- 整夜上下文。

不要只看总体指标。要按转期类型拆开看：

- W/N1/N2 入睡链；
- N2/N3 深睡边界；
- N2/REM 或 NREM/REM 周期边界；
- REM/W 或夜间觉醒边界。

预期可能出现的结果是：短上下文对 N1 最有效；N2-N3 更依赖局部慢波；90 分钟上下文可能只对 REM 周期有用；整夜上下文可能收益不稳定。

### 入手点 C：轻量 transition-aware regularization

推荐先做三类方法，保持实现简单：

1. **Transition-aware sample weighting**  
   对真实转期前后 k 个 epoch 加权，权重随距离边界衰减。它直接优化转期窗口，不改变模型结构。

2. **Boundary-aware consistency loss**  
   对非转期稳定片段约束相邻预测分布一致；对转期窗口不施加平滑，避免抹掉真实边界。

3. **Transition prior / CRF-style penalty**  
   用训练 hypnogram 估计 transition matrix，对低概率跳变施加软惩罚，或在推理时做 Viterbi/CRF decoding。注意惩罚不能太强，否则会降低短觉醒召回。

可选第 4 类是 transition detection auxiliary head，但 TransSleep 已经做过，最好作为 ablation 或辅助，不作为唯一创新。

## 5. 推荐第一篇文章故事线

暂定题目方向：

> **When Does Context Help? Transition-Centered Evaluation and Lightweight Sequence Regularization for EEG Sleep Staging**

中文表述：

> **上下文什么时候真的有用？面向睡眠阶段转换的 EEG 睡眠分期评测与轻量序列正则化**

文章主线：

1. 现有 EEG 睡眠分期普遍使用上下文，但主要按普通 epoch-level 指标评价。
2. 这些指标掩盖了临床上更关键的 hypnogram 边界错误、碎片化和转期延迟。
3. 我们提出 transition-centered evaluation protocol，系统分析不同上下文长度对不同转期类型的影响。
4. 我们提出轻量 transition-aware regularization，在固定 backbone 下减少边界错误。
5. 如果超长上下文无明显收益，这不是失败，而是结论：睡眠分期需要“合适上下文”，不是“无限长上下文”。

## 6. 最小可行实验协议

### 数据

第一阶段只用 Sleep-EDF Expanded 快速跑通。建议用 Fpz-Cz 作为主通道，Pz-Oz 做补充。划分必须 subject-independent。

第二阶段加入 ISRUC 或 MASS 做外部验证。SHHS 数据价值高，但申请和处理成本更大，不作为第一轮必需。

### Baseline

- B0：single-epoch CNN/TCN。
- B1：5 分钟上下文模型。
- B2：30 分钟上下文模型。
- B3：90 分钟 whole-cycle 模型。
- B4：整夜上下文模型。

第一轮只需要 B0/B1/B2 + M1/M3，就能判断方向是否有信号。

### 方法

- M1：transition-aware sample weighting。
- M2：transition prior / CRF-style penalty。
- M3：boundary-aware consistency loss。
- M4：transition detection auxiliary head。

推荐执行顺序：

1. 先实现转期指标。
2. 跑 B0/B1/B2。
3. 加 M1，看 transition-window macro-F1 和 N1 是否提升。
4. 加 M3，看 fragmentation error 是否下降且 boundary delay 不恶化。
5. 若有效，再做 M2/M4 和 B3/B4。

### 指标

常规指标保留：accuracy、macro-F1、kappa、per-stage F1。

主指标改为：

- transition-window macro-F1；
- W-N1-N2 transition F1；
- N2-N3 transition F1；
- NREM-REM transition F1；
- boundary delay；
- fragmentation error；
- transition calibration。

主结论必须来自这些指标，不能只说 overall accuracy 涨了 0.3%。

## 7. 风险判断

### 风险 1：创新性中等

上下文建模和 transition auxiliary task 都有人做过。解决方式：贡献放在评测协议、转期类型分析和轻量正则，不主张模型结构 SOTA。

### 风险 2：长上下文收益不显著

这不是致命风险。可以转成负结果贡献：不是所有转期都需要长上下文；短/中上下文可能已足够；超长上下文可能只增加成本。

### 风险 3：序列正则损害短觉醒

这正是文章可分析的点。需要同时报告 fragmentation error、boundary delay 和 wake/REM 边界召回，避免只追求平滑 hypnogram。

### 风险 4：Sleep-EDF 规模偏小

第一阶段用 Sleep-EDF 打样可以，但文章正式版至少应加入 ISRUC 或 MASS。否则结论容易被认为是小数据集调参。

## 8. 下一步建议

我建议下一步进入小规模实验准备，而不是继续泛读：

1. 实现 hypnogram transition metrics。
2. 下载/整理 Sleep-EDF。
3. 复现一个轻量 CNN/TCN baseline。
4. 先跑 B0/B1/B2，验证“上下文长度 × 转期类型”的初始图。
5. 如果 transition-window 指标出现清晰差异，再加入 M1/M3。

第一张关键图应该是：

> 不同上下文长度在不同转期类型上的 transition-window macro-F1 / boundary delay 对比。

如果这张图有结构性差异，这篇文章就有可写性。

## 9. 参考入口

- SleepTransformer: https://arxiv.org/abs/2105.11043
- TransSleep: https://arxiv.org/abs/2203.12590
- ProductGraphSleepNet: https://arxiv.org/abs/2212.04881
- L-SeqSleepNet: https://arxiv.org/abs/2301.03441
- Continuous sleep depth: https://arxiv.org/abs/2301.06755
- S4Sleep: https://arxiv.org/abs/2310.06715
- Long-range correlations analysis: https://arxiv.org/abs/2402.17779
- NeuroLingua: https://arxiv.org/abs/2511.09773
- AnySleep: https://arxiv.org/abs/2512.14461
- Context-aware temporal modeling: https://arxiv.org/abs/2512.22976
