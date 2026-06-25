# Protocol: Transition-Aware Long-Context EEG Sleep Staging

## Research Question

在固定轻量 backbone 下，显式建模睡眠阶段转换和转期窗口，是否比单纯增加上下文长度更能改善 EEG 睡眠分期的边界表现？

## Hypotheses

- H1: 与单 epoch 或短上下文模型相比，中等上下文能改善 W-N1-N2、N2-N3、NREM-REM 等边界，但 90 分钟或整夜上下文不一定继续提升。
- H2: transition-aware sample weighting 能提升 transition-window macro-F1，尤其是 N1 和 W/N1/N2 相关窗口。
- H3: transition prior 或 CRF-style sequence penalty 能减少非典型跳变和 hypnogram fragmentation，但过强会抹平真实短觉醒。
- H4: sequence consistency loss 应只约束非转期片段；如果无差别平滑，会降低真实边界召回。

## Default Dataset Plan

1. 快速启动：Sleep-EDF Expanded，单通道 Fpz-Cz 或 Pz-Oz。
2. 外部验证：ISRUC-Sleep 或 MASS，取决于可获取性。
3. 增强验证：SHHS，只在访问和处理成本可控时加入。

## Baselines

- B0: Single-epoch CNN/TCN classifier。
- B1: Short-context model，约 5 分钟，即 10 个 30 秒 epoch。
- B2: Mid-context model，约 30 分钟，即 60 个 epoch。
- B3: Whole-cycle context，约 90 分钟，即 180 个 epoch。
- B4: Full-night context，整夜序列或 chunked full-night approximation。

## Methods to Add

- M1 transition-aware weighting: 对真实边界前后 k 个 epoch 加权，权重按距离边界衰减，并与 class balancing 叠加。
- M2 transition prior / CRF-style penalty: 从训练 hypnogram 估计 transition matrix，对预测序列中的低概率跳变施加软惩罚；推理时可选 Viterbi/CRF decoding。
- M3 boundary-aware consistency: 非转期片段约束相邻预测分布一致，转期窗口取消或反向降低平滑约束。
- M4 transition detection auxiliary head: 预测当前 epoch 是否位于转期窗口，用作辅助任务和 error analysis。

## Metrics

常规指标：

- accuracy
- macro-F1
- Cohen's kappa
- per-stage F1

转期中心指标：

- transition-window macro-F1: 在真实边界前后 k 个 epoch 的集合上计算 macro-F1。
- per-transition F1: 分别统计 W-N1/N1-N2/N2-N3/N2-REM/REM-W 等常见转换窗口。
- boundary delay: 每个真实边界匹配最近预测边界，记录偏移 epoch 数。
- transition recall/precision: 把 `label_t != label_{t-1}` 作为边界检测事件。
- noncanonical transition rate: 训练集中低频或无出现的预测跳变比例；报告时称 noncanonical，不绝对称 illegal。
- fragmentation error: 预测每小时转移次数与真实每小时转移次数的绝对/相对误差。
- transition calibration: 用相邻 epoch 概率分布计算 change probability，并对真实 change indicator 做 Brier/ECE。

所有转期指标均可由 hypnogram 标签序列和模型概率输出计算，不需要额外人工标注。

## Acceptance Criteria

- 主结论必须至少有一个 transition-centered metric 支持，不能只依赖 overall accuracy。
- 至少报告一个负结果维度：例如超长上下文无收益、过强平滑伤害短觉醒、某类转期不受上下文帮助。
- 所有实验使用 subject-independent split；若跨数据集，使用 leave-one-dataset-out 或 train-on-one-test-on-another。

## First Experiment Order

1. 实现 hypnogram transition metrics，并在真实标签上做 sanity check。
2. 复现 B0/B1/B2 三个上下文长度，不先做 B3/B4。
3. 加入 M1 sample weighting，检查 N1 与 transition-window macro-F1。
4. 加入 M3 consistency loss，检查是否降低 fragmentation error。
5. 若前两步有收益，再做 M2/M4 和 B3/B4。

