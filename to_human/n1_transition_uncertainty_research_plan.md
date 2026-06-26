# 研究方案：转期不确定性引导的 N1 睡眠阶段识别

日期：2026-06-26  
状态：正式研究规划；第一阶段不下载数据、不训练模型；后续实验前需先提交 protocol。

## 1. 核心定位

本项目的最新主线收束为：

> 用转期/边界不确定性同时调节标签监督和上下文建模，以提升 EEG 睡眠分期中的 N1 识别。

第一篇文章不主打跨数据集泛化，也不直接主打 TGCM 大模型。主线应是 **N1 标签不确定性**：

- N1 的困难不只是样本少；
- W-N1-N2 边界本身存在生理连续性和人工评分分歧；
- hard label 会把边界 epoch 过度压成单一确定类别；
- 阶段相邻 soft label 与转期窗口不确定性建模是第一版最清晰的贡献。

TGCM 作为第二阶段增强模块引入。它回答另一个相关问题：边界不确定样本是否也需要不同上下文尺度。这样两条线不是并列堆叠，而是由“转期/边界不确定性”统一。

## 2. 统一研究假设

### H1：N1 的边界不确定性需要结构化 soft label

N1 难识别不仅因为样本少，还因为 W-N1-N2 边界标签本身不确定。阶段相邻 soft label 应优于 hard CE、class-weighted CE、focal loss 和 uniform label smoothing。

预期结果：

- N1 F1 上升；
- N1 precision/recall 更平衡；
- ECE 或 boundary-adjacent ECE 改善；
- N1 overprediction rate 不显著上升。

### H2：转期窗口需要降低 hard-label 过拟合

转期窗口内的 30 秒 epoch 可能同时包含多个阶段证据。对 W↔N1、N1↔N2 边界使用更强 softening 或降低 hard-label loss 权重，应优先提升 transition-window N1 F1 与校准。

预期结果：

- transition-window N1 F1 上升；
- stable-vs-transition gap 缩小；
- W↔N1、N1↔N2 混淆结构更合理。

### H3：TGCM 是边界不确定性的上下文扩展

如果 TGCM 在转期窗口提高 mid/long context gate，在稳定区偏 short context，则说明边界不确定性不仅影响标签监督，也影响上下文需求。

预期结果：

- TGCM 相比 fixed-context 和 only-transition-head baseline 改善至少一个核心转期指标；
- gate 权重在稳定区和转期区出现可解释差异；
- TGCM + soft label 优于 TGCM hard label 或 fixed-context soft label。

## 3. 方法路线

### 阶段一：N1 标签不确定性主方法

默认 backbone 固定为轻量 CNN/TCN 或 compact Transformer。第一阶段不追求架构创新，重点比较训练目标。

Baseline：

- hard-label CE；
- class-weighted CE；
- focal loss；
- balanced sampler；
- uniform label smoothing。

方法：

- Stage-adjacent soft label；
- transition-window stronger smoothing；
- transition-window hard-loss downweighting；
- A+B hybrid：全局阶段相邻 soft label + W↔N1/N1↔N2 转期窗口更强不确定性建模。

默认 soft label 结构：

| 原标签 | 软标签邻接 |
|---|---|
| W | W 主概率，少量给 N1 |
| N1 | N1 主概率，少量给 W/N2 |
| N2 | N2 主概率，少量给 N1/N3 |
| N3 | N3 主概率，少量给 N2 |
| REM | 第一版 near-hard；仅分析 REM-W/N1 混淆 |

### 阶段二：TGCM 增强模块

TGCM 不抢第一阶段主线，而作为增强模块验证“边界不确定样本需要自适应上下文”。

结构：

- epoch encoder；
- short/mid/long context branches；
- transition head；
- context gate；
- stage classifier。

默认上下文尺度：

- short：约 5 分钟；
- mid：约 30 分钟；
- long：约 90 分钟。

关键对照：

- fixed short context；
- fixed mid context；
- fixed long context；
- only-transition-head baseline；
- TGCM；
- TGCM + A+B hybrid。

## 4. 实验规划

### 数据与划分

第一阶段：

- Sleep-EDF Expanded；
- 单通道 Fpz-Cz；
- subject-independent split；
- 五分类标签 W/N1/N2/N3/REM；
- 剔除 Movement/Unknown。

第二阶段：

- ISRUC 独立复现；
- 使用同一预处理原则、转期定义和指标；
- 不用 ISRUC 调 Sleep-EDF 超参。

扩展：

- MASS/SHHS 仅作为后续鲁棒性数据；
- Dreem/LSSC 多评分员数据仅用于验证 soft-label 先验，不作为第一版依赖。

### 转期定义

默认转期窗口 `k=2`：

```text
boundary tau: y_tau != y_{tau-1}
transition-window: |t - tau| <= 2
```

需单独统计：

- W↔N1；
- N1↔N2；
- N2↔N3；
- NREM↔REM。

### 指标

主指标：

- N1 F1；
- N1 precision/recall；
- macro-F1；
- Cohen's kappa；
- ECE；
- W↔N1、N1↔N2 混淆。

专项指标：

- transition-window N1 F1；
- transition-window macro-F1；
- stable-vs-transition gap；
- boundary-adjacent ECE；
- N1 overprediction rate；
- boundary delay；
- fragmentation error。

TGCM 机制证据：

- 稳定区 vs 转期区 gate 权重分布；
- W-N1-N2 与 NREM-REM 边界上下文权重差异；
- 错误样本的 gate 异常分析。

## 5. 执行路线图

### 第 0 阶段：实验前注册与工具准备

- 锁定统一 protocol；
- 实现数据统计脚本：阶段比例、N1 占比、转期比例、边界类型计数；
- 实现指标脚本：N1 F1、transition-window F1、ECE、N1 overprediction、boundary delay、fragmentation。

### 第 1 阶段：Sleep-EDF baseline

- 跑 hard CE；
- 跑 class-weighted CE；
- 跑 focal loss；
- 跑 balanced sampler；
- 跑 uniform label smoothing。

目标是建立可信基线，判断 N1 低性能到底能被 class imbalance 解释多少。

### 第 2 阶段：N1 标签不确定性方法

- 加入 stage-adjacent soft label；
- 加入 transition-window stronger smoothing；
- 加入 transition-window hard-loss downweighting；
- 跑 A+B hybrid。

若 A+B 相比 hard CE 和 class imbalance baseline 稳定提升 N1 F1 或 transition-window N1 F1，第一篇文章主贡献成立。

### 第 3 阶段：ISRUC 复现

- 复现第 1-2 阶段；
- 只做同数据集 subject-independent 复现；
- 暂不把跨数据集结果写成主贡献。

### 第 4 阶段：TGCM 增强实验

- 实现 fixed short/mid/long context；
- 实现 only-transition-head baseline；
- 实现 TGCM；
- 实现 TGCM + A+B hybrid；
- 报告 gate 分布和转期指标。

### 第 5 阶段：错误分析与论文整理

- 分析 W↔N1、N1↔N2 典型错误；
- 对比 stable epoch 与 transition epoch；
- 检查 soft label 是否只是提高 N1 预测比例；
- 最后再做 Sleep-EDF↔ISRUC 跨数据集 robustness check。

## 6. 成功标准与失败处理

成功标准：

- 相对 hard CE 和 class imbalance baselines，N1 F1 或 transition-window N1 F1 稳定提升；
- macro-F1/kappa 不明显下降；
- ECE 不恶化；
- N1 overprediction rate 不显著升高；
- TGCM 的 gate 可视化呈现稳定区/转期区差异。

失败处理：

- 如果 class-weighted CE 已解释全部收益，研究收窄为 N1 不均衡与校准；
- 如果 soft label 只提高 recall 但 precision 崩溃，降低 smoothing 强度或只对转期窗口启用；
- 如果 transition-window 指标不提升，改用 teacher entropy 或多评分员分布定义不确定性；
- 如果 TGCM 无额外收益，把它作为扩展负结果，不强行并入主论文。

## 7. 论文故事线

建议第一篇中文主线：

> 面向 N1 标签不确定性的阶段相邻软标签与转期边界建模。

建议英文标题方向：

> Transition-Uncertainty Guided Soft Labels for Improving N1 Sleep Stage Recognition from EEG

摘要逻辑：

1. N1 是自动睡眠分期中最难识别的阶段之一；
2. 现有方法多从类别不均衡或模型结构解决，但忽略 W-N1-N2 边界标签不确定性；
3. 我们提出阶段相邻 soft label 和转期窗口不确定性建模；
4. 进一步用 TGCM 验证边界不确定性也影响上下文尺度需求；
5. 实验用 N1 F1、transition-window N1 F1、校准和相邻混淆证明方法有效。

## 8. 关键约束

- 第一篇不主打完整 domain generalization；
- 第一阶段不依赖多评分员数据；
- 不做疾病检测；
- 不训练基础模型；
- 所有 confirmatory 实验必须先有 protocol，再跑结果；
- 探索性结果必须单独标注。
