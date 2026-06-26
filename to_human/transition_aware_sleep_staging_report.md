# TGCM：转期机制驱动的自适应上下文 EEG 睡眠分期

日期：2026-06-26
目标：把“转期感知长上下文”从实验评测型方向，重构为统一 N1 研究规划中的第二阶段自适应上下文增强模块。

2026-06-26 统一规划更新：TGCM 现在作为“转期不确定性引导的 N1 识别”的第二阶段增强模块，而不是第一篇文章的默认主标题。第一阶段先验证 N1 标签不确定性与阶段相邻 soft label。

## 1. 核心结论

当前方向应正式收束为：

> **Transition-Guided Context Modulation (TGCM)：用转期机制动态调节 EEG 睡眠分期中的上下文尺度。**

这比“比较不同上下文长度”或“增加转期评测指标”更适合作为第一篇方法论文。文章主张不再是“长上下文是否有用”，而是：

> 不同 epoch 对上下文的需求不同。稳定睡眠片段不需要强长上下文平滑；转期和标签不确定区域需要更多多尺度上下文来判断边界。

因此，本文应主打一个明确方法模块：模型先估计每个 epoch 的转期风险，再用该风险动态融合 short / mid / long 多尺度上下文表示。转期指标仍然重要，但它们是证明 TGCM 有效的证据，不是论文的主要创新点。

## 2. 与已有工作的边界

### 2.1 不能写成“更长上下文模型”

SleepTransformer、SeqSleepNet、L-SeqSleepNet、S4Sleep、Mamba/SSM 类模型已经证明上下文建模有价值。尤其 L-SeqSleepNet 已经把 90 分钟 whole-cycle 作为建模单位，S4Sleep 及长相关性分析也提示单纯拉长上下文并不稳定带来收益。

所以本文不能把贡献写成“我们用了更长上下文”。

### 2.2 不能只写成“转期辅助任务”

TransSleep 已经直接把 transitioning epochs 和 confusing stages 作为问题，使用 stage-confusion estimator 和 stage-transition detection 辅助任务。因此，如果我们只加一个 transition detection head，创新性不足。

我们的边界应是：

- TransSleep 用转期辅助任务增强上下文编码；
- TGCM 用转期概率作为控制信号，动态决定上下文尺度的融合方式；
- TGCM 的重点不是“检测转期”，而是“转期机制如何调制上下文依赖”。

### 2.3 评测协议是辅助贡献

transition-window macro-F1、boundary delay、fragmentation error 等指标仍保留，但不再作为第一贡献。它们用于回答：

- TGCM 是否真的改善转期窗口；
- TGCM 是否减少边界延迟；
- TGCM 是否避免固定长上下文带来的过度平滑；
- TGCM 的 gate 是否在稳定区偏短上下文、在转期区偏中长上下文。

## 3. 方法设计

### 3.1 输入与基础表示

输入为连续 EEG hypnogram 对齐的 30 秒 epoch 序列：

```text
X = [x_1, x_2, ..., x_T]
y_t in {W, N1, N2, N3, REM}
```

每个 epoch 先经过共享 epoch encoder：

```text
h_t = Encoder(x_t)
```

第一版不需要追求复杂 encoder。推荐使用轻量 CNN/TCN 或 TinySleepNet-style encoder，保证主创新集中在 TGCM，而不是底层特征提取。

### 3.2 多尺度上下文分支

在 epoch 表征序列上并行构建三个上下文分支：

- **short context**：约 5 分钟，捕捉 W-N1-N2 入睡边界和局部相邻关系；
- **mid context**：约 30 分钟，捕捉 N2-N3、NREM-REM 等中程结构；
- **long context**：约 90 分钟，捕捉睡眠周期和 REM 周期信息。

每个分支输出对应尺度的上下文表示：

```text
c_t^S = Context_S(h_{t-r_s:t+r_s})
c_t^M = Context_M(h_{t-r_m:t+r_m})
c_t^L = Context_L(h_{t-r_l:t+r_l})
```

第一版可以用 depthwise TCN、轻量 Transformer encoder 或 BiGRU 实现这些分支。关键是三个分支容量尽量接近，避免结果被参数量解释。

### 3.3 转期概率作为调制信号

由 epoch 表征和局部上下文预测当前 epoch 是否处于转期窗口：

```text
p_t^B = TransitionHead([h_t, c_t^S])
```

转期标签不需要额外人工标注，可由 hypnogram 自动生成：

```text
b_t = 1, if exists boundary tau where |t - tau| <= k
b_t = 0, otherwise
```

其中 boundary 定义为 `y_t != y_{t-1}`。默认 `k = 2`，即真实边界前后约 1 分钟。

### 3.4 Transition-Guided Context Gate

TGCM 的核心是一个 context gate：

```text
g_t = softmax(MLP([h_t, c_t^S, p_t^B]))
z_t = g_t^S c_t^S + g_t^M c_t^M + g_t^L c_t^L
```

直观约束是：

- 稳定区：`g_t^S` 应较高，减少过度平滑和长上下文噪声；
- 转期区：`g_t^M` / `g_t^L` 可以提高，用更多上下文判断阶段边界；
- N1 相关转期：更依赖 short/mid context；
- NREM-REM 相关转期：可能更依赖 mid/long context。

最终分类：

```text
y_hat_t = StageClassifier([h_t, z_t])
```

## 4. 训练目标

总损失：

```text
L = L_stage + lambda_B L_boundary + lambda_G L_gate + lambda_C L_consistency
```

### 4.1 主分类损失

使用 stage CE 或 class-balanced CE：

```text
L_stage = CE(y_hat_t, y_t)
```

N1 类别少，建议保留 class-balanced CE 作为默认主损失，但不要把 class imbalance 写成主贡献。

### 4.2 转期监督损失

用自动生成的 `b_t` 监督 transition head：

```text
L_boundary = BCE(p_t^B, b_t)
```

该 head 的角色是为 context gate 提供控制信号，而不是作为最终贡献。

### 4.3 Gate regularization

对稳定片段施加短上下文偏置：

```text
if b_t = 0: encourage g_t^S high
```

对转期窗口不强制使用长上下文，只允许 gate 自适应分配：

```text
if b_t = 1: avoid collapsing to only short context
```

这能避免模型学成普通固定短上下文模型，也避免全局无差别长上下文。

### 4.4 Stable consistency

只在非转期稳定片段约束相邻预测一致：

```text
if b_t = 0 and b_{t+1} = 0:
  minimize KL(p_t || p_{t+1})
```

转期窗口不施加平滑约束，避免抹平真实边界、延迟阶段转换或降低短觉醒召回。

## 5. 实验设计

### 5.1 数据集

第一阶段：

- Sleep-EDF Expanded；
- subject-independent split；
- 单通道 Fpz-Cz；
- 标签统一为 W/N1/N2/N3/REM。

第二阶段：

- ISRUC 或 MASS；
- 用于外部验证，而不是第一阶段调参。

SHHS 可作为增强验证，但访问和预处理成本较高，不作为第一版必要条件。

### 5.2 对照模型

必须包含：

- **B0 single-epoch baseline**：无上下文；
- **B1 fixed short context**：固定短上下文；
- **B2 fixed mid context**：固定中上下文；
- **B3 fixed long context**：固定 90 分钟上下文；
- **B4 transition auxiliary baseline**：只加 transition head，不做 gate，用作 TransSleep-style 对照；
- **TGCM**：转期引导的自适应上下文融合。

这样可以证明 TGCM 的收益不是来自“多一个辅助任务”，也不是来自“上下文更长”。

### 5.3 消融实验

核心消融：

- TGCM w/o context gate：等价于固定融合多尺度上下文；
- TGCM w/o transition supervision：gate 不显式知道转期；
- TGCM w/o gate regularization：检查 gate 是否退化；
- TGCM w/o stable consistency：检查碎片化是否上升；
- TGCM with only short/mid/long branch：验证不同尺度的必要性。

### 5.4 主要指标

常规指标保留：

- accuracy；
- macro-F1；
- Cohen's kappa；
- per-stage F1。

但主证据来自：

- transition-window macro-F1；
- W-N1-N2 transition F1；
- N2-N3 transition F1；
- NREM-REM transition F1；
- boundary delay；
- fragmentation error；
- transition calibration；
- gate 权重在稳定区/转期区的分布差异。

门控可视化是重要证据。论文应展示：

- 稳定 N2/N3 中 gate 是否偏 short；
- W-N1-N2 边界是否提高 mid 权重；
- NREM-REM 边界是否提高 mid/long 权重；
- 预测错误时 gate 是否异常。

## 6. 论文故事线

建议标题：

> **Transition-Guided Context Modulation for EEG Sleep Staging**

中文表达：

> **面向 EEG 睡眠分期的转期引导自适应上下文调制方法**

摘要主线：

1. EEG 睡眠分期依赖上下文，但现有方法通常使用固定或隐式上下文。
2. 固定上下文不能区分稳定 epoch 与转期 epoch，可能造成边界延迟、hypnogram 过度平滑和 N1 误判。
3. 我们提出 TGCM，用转期概率动态融合 short/mid/long 多尺度上下文。
4. 通过边界感知训练目标，模型在稳定区保持一致，在转期区保留变化敏感性。
5. 实验表明 TGCM 改善转期窗口表现并保持常规分期性能。

贡献写法：

- 提出一个转期引导的自适应上下文调制模块，用于 EEG 睡眠分期；
- 设计边界感知训练目标，使上下文建模在稳定区与转期区行为不同；
- 通过转期窗口指标和 gate 可视化证明模型确实学习到不同阶段边界的上下文需求。

## 7. 风险与规避

### 风险 1：被认为只是 TransSleep 变体

规避方式：

- 不把 transition head 写成主贡献；
- 强调 transition head 只是 gate 的控制信号；
- 重点展示 adaptive context weights，而不是只展示辅助任务提升。

### 风险 2：gate 学不到清晰模式

规避方式：

- 加入 gate regularization；
- 报告稳定区与转期区 gate 分布；
- 做 w/o transition supervision 消融。

### 风险 3：长上下文仍无明显收益

这不致命。TGCM 的假设不是“长上下文总有用”，而是“按转期状态选择上下文更合理”。如果 long branch 权重整体很低，但 mid branch 在特定转期上升，仍支持自适应机制。

### 风险 4：总体 accuracy 提升很小

可接受。文章应提前声明主目标是转期边界质量，而不是整体 accuracy 小幅 SOTA。关键是 transition-window 指标、boundary delay 和 gate 解释要有一致证据。

## 8. 下一步执行顺序

1. 更新 protocol，锁定 TGCM 为主方法。
2. 实现 transition label generation 与 transition metrics。
3. 实现 B0/B1/B2/B3/B4 基线。
4. 实现 TGCM：multi-scale context branches + transition head + context gate。
5. 先在 Sleep-EDF 跑小规模 sanity check。
6. 完整运行 subject-independent evaluation。
7. 加入 ISRUC 或 MASS 做外部验证。

## 9. 参考边界

- TransSleep: https://arxiv.org/abs/2203.12590
- SleepTransformer: https://arxiv.org/abs/2105.11043
- L-SeqSleepNet: https://arxiv.org/abs/2301.03441
- S4Sleep: https://arxiv.org/abs/2310.06715
- Long-range correlations analysis: https://arxiv.org/abs/2402.17779
- Context-aware temporal modeling: https://arxiv.org/abs/2512.22976
