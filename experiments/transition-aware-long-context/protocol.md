# Protocol: Transition-Guided Context Modulation (TGCM)

Status note: under the unified 2026-06-26 research plan, TGCM is a second-stage enhancement module after the N1 label-uncertainty protocol, not the default first-paper title.

## Research Question

在 EEG 睡眠分期中，使用转期概率动态调制上下文尺度，是否比固定短/中/长上下文或单纯转期辅助任务更能改善阶段转换边界，同时保持常规五分类性能？

## Core Method

提出 **Transition-Guided Context Modulation (TGCM)**。

模型由五部分组成：

1. **Epoch encoder**：从每个 30 秒 EEG epoch 提取局部表征。
2. **Multi-scale context branches**：并行构建 short / mid / long 上下文表示。
3. **Transition head**：预测当前 epoch 是否位于真实阶段转换窗口附近。
4. **Context gate**：根据转期概率和 epoch 表征动态融合不同上下文尺度。
5. **Stage classifier**：输出 W/N1/N2/N3/REM 五分类结果。

主创新是第 4 部分：转期概率不是最终任务，而是上下文调制信号。

## Hypotheses

- H1: 固定上下文模型会在稳定片段和转期片段使用同一上下文策略，导致边界延迟或过度平滑。
- H2: TGCM 能在稳定区提高 short-context gate，在转期区提高 mid/long-context gate，从而改善 transition-window macro-F1。
- H3: TGCM 相比 only-transition-head baseline 更有效，说明收益来自上下文调制，而不只是辅助监督。
- H4: stable consistency 只在非转期片段施加时能降低 fragmentation；若无差别平滑，会损害 boundary recall。

## Dataset Plan

第一阶段：

- Sleep-EDF Expanded；
- subject-independent split；
- 单通道 Fpz-Cz；
- 标签统一为 W/N1/N2/N3/REM；
- 默认 30 秒 epoch。

第二阶段：

- ISRUC 或 MASS；
- 复用相同 preprocessing、split 原则和 metrics；
- 只作为外部验证，不用于第一阶段选超参。

SHHS 只作为增强验证，不作为第一版必要条件。

## Model Variants

Baselines:

- B0: single-epoch CNN/TCN classifier。
- B1: fixed short-context model，约 5 分钟上下文。
- B2: fixed mid-context model，约 30 分钟上下文。
- B3: fixed long-context model，约 90 分钟上下文。
- B4: transition auxiliary baseline，仅加 transition head，不做 context gate。

Proposed:

- M0: TGCM full model。

Ablations:

- A1: TGCM w/o context gate，使用固定平均或拼接融合。
- A2: TGCM w/o transition supervision，gate 不使用显式边界标签。
- A3: TGCM w/o gate regularization。
- A4: TGCM w/o stable consistency。
- A5: TGCM short-only / mid-only / long-only branch。

## Training Objectives

总损失：

```text
L = L_stage + lambda_B L_boundary + lambda_G L_gate + lambda_C L_consistency
```

- `L_stage`：stage CE 或 class-balanced CE。
- `L_boundary`：由 hypnogram 自动生成转期窗口标签，监督 transition head。
- `L_gate`：稳定区鼓励 short-context 权重，转期区避免 gate 退化到单一 short context。
- `L_consistency`：仅在非转期稳定片段约束相邻预测分布一致。

默认转期窗口：

```text
b_t = 1 if exists boundary tau where |t - tau| <= 2
```

其中 boundary 为 `y_t != y_{t-1}`。

## Metrics

常规指标：

- accuracy；
- macro-F1；
- Cohen's kappa；
- per-stage F1。

主证据指标：

- transition-window macro-F1；
- W-N1-N2 transition F1；
- N2-N3 transition F1；
- NREM-REM transition F1；
- boundary delay；
- transition precision/recall；
- fragmentation error；
- transition calibration；
- stable vs transition gate-weight distribution。

主结论必须来自 TGCM 对转期指标和 gate 行为的联合改善，不能只依赖 overall accuracy。

## Acceptance Criteria

- TGCM 相比 B1/B2/B3 至少在一个核心转期指标上改善，并且常规 macro-F1/kappa 不明显退化。
- TGCM 相比 B4 有额外收益，证明不是 transition auxiliary task 本身带来的全部效果。
- gate 可视化显示稳定区和转期区存在可解释差异。
- stable consistency 不应显著增加 boundary delay；若增加，需要作为负结果记录。
- 所有结果使用 subject-independent split。

## First Experiment Order

1. 实现 transition label generation 与 transition-centered metrics。
2. 复现 B0/B1/B2，确认数据和常规指标合理。
3. 加入 B4 only-transition-head baseline。
4. 实现 TGCM full model 的 short/mid/long context branches 与 context gate。
5. 跑 A1/A2/A3/A4 消融。
6. 扩展到 B3 long context 与 A5 branch-only 消融。
7. 若 Sleep-EDF 结果支持假设，再迁移到 ISRUC 或 MASS。

## Paper Claim Boundary

本文不声称提出最强 sleep staging backbone，也不主打更长上下文或新评价协议。核心声明是：

> 转期机制可以作为上下文调制信号，使模型在稳定片段和阶段转换片段采用不同上下文策略，从而改善 hypnogram 边界质量。
