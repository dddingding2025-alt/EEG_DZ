# 基于 EEG 的睡眠分期：第一轮研究发现

## 当前理解

EEG 睡眠分期的标准任务通常把连续 PSG/EEG 切成 30 秒 epoch，并预测 W、N1、N2、N3、REM。深度学习在 Sleep-EDF、MASS、ISRUC 等公开数据集上已经能取得很高的 within-dataset 结果；因此，单纯在同一数据集内提升 accuracy 已经不是最有价值的问题。

近五年更重要的变化是研究目标从“更深的网络”转向“更可信的睡眠评分系统”：跨数据集泛化、少通道/任意通道、标注噪声、自监督预训练、基础模型和临床可解释性。

## 关键模式

- N1 是最难稳定识别的阶段，原因不只是模型能力不足，还来自生理边界模糊、人工标注分歧和类别占比低。
- 睡眠分期有强序列结构：孤立 epoch 分类容易犯转期错误，长上下文建模通常比单 epoch 模型更稳。
- 高性能结果常常依赖数据集内划分；跨被试、跨数据集、跨设备时性能下降明显。
- 大规模预训练和基础模型有潜力，但现有工作经常缺少严格的 clinical transfer、label-noise、calibration 和 compute-cost 分析。
- 可穿戴/居家 EEG 的关键问题不是“是否能做分类”，而是低信噪比、通道布局变化、伪迹、校准成本和失败检测。

## 暂不建议作为主线的方向

- 只在 Sleep-EDF 上提出一个新 CNN/Transformer 结构并报告 accuracy 小幅提升。
- 只做五分类平均指标，不报告 N1、REM、转期片段和混淆矩阵。
- 只把 EEG 图片化后套通用视觉模型，若没有解释为什么时频结构或跨域泛化更好，创新性较弱。
- 只做纯自监督预训练但不验证少标签、跨数据集、噪声标签或临床外部验证。

## 推荐下一步

优先做“面向 N1 标签不确定性的 EEG 睡眠分期”。可检验假设是：显式建模 N1 的 W-N1-N2 阶段相邻性和转期边界不确定性，可以比 hard-label 训练、class-weighted CE、focal loss 和普通 label smoothing 更稳定地改善 N1 F1、转期窗口 N1 F1 和校准。

建议第一版实验只使用可公开获取的数据，先在 Sleep-EDF 做 subject-independent within-dataset baseline，再在 ISRUC 复现；跨数据集测试只作为后续 robustness check，不作为第一篇文章主问题。

## 第二轮聚焦：转期感知长上下文

用户明确偏好将“转期感知的长上下文睡眠分期”作为第一篇文章方向。第二轮调研后的判断是：该方向可行，但文章必须避免写成普通长上下文模型。已有 DeepSleepNet/SeqSleepNet/IITNet/SleepTransformer/L-SeqSleepNet/S4Sleep/Mamba/NeuroLingua 等工作已经覆盖大量上下文建模。

该阶段原本建议以 transition-centered evaluation protocol 加轻量 sequence regularization 作为贡献。但用户进一步指出该方案方法创新性偏小，因此该建议已被 2026-06-26 的 TGCM 方法化修订取代。

当前保留的有效判断是：不能写成“上下文越长越好”，也不能只加一个 transition auxiliary task。新的主问题是“模型如何根据转期机制自适应选择上下文尺度，并由此改善阶段转换边界”。

## 方向1修订：N1 标签不确定性

用户指出 domain shift 与 N1 标签不确定性不应被合并为同一核心方向，这个判断成立。跨数据集泛化是独立鲁棒性问题；无论是否建模 N1 标签不确定性，它都存在。因此方向1已修订为“通过阶段相邻软标签与转期不确定性建模提升 N1 睡眠阶段识别”。

当前需要分开处理三类机制：

- Class imbalance：N1 样本少，模型偏向 W/N2；用 class weight、focal loss、balanced sampler、SleepEGAN 类增强作为基线。
- Label uncertainty：N1 与 W/N2 边界存在人工评分分歧和 30 秒 epoch 内混合证据；用 stage-adjacent soft labels、multi-rater consensus、teacher soft labels 建模。
- Transition dependence：N1 常发生在 W->N1、N1->N2 转期附近；用 transition-window smoothing 或 uncertainty weighting 降低 hard-label 过拟合。

Domain shift 只作为补充：当 Sleep-EDF 和 ISRUC 的 within-dataset subject-independent 实验证明方法有效后，再做 Sleep-EDF <-> ISRUC 或 MASS/SHHS 外部鲁棒性检查。

下一步最小实验假设：stage-adjacent label smoothing 和 transition-aware smoothing 应优先改善 N1 F1、transition-window N1 F1、W<->N1/N1<->N2 混淆和 ECE，而不一定显著提升 overall accuracy。

## 方向2修订：TGCM 转期机制驱动方法

用户指出原“转期感知长上下文”方案的方法创新性偏小，主要贡献集中在实验和评价上。该判断成立。因此方向2已正式从“transition-centered evaluation + lightweight regularization”修订为方法主导方案：

> **Transition-Guided Context Modulation (TGCM)：用转期机制动态调节 EEG 睡眠分期中的上下文尺度。**

新的核心假设是：不同 epoch 对上下文长度的需求不同。稳定 N2/N3 片段不需要强长上下文平滑；W-N1-N2、N2-N3、NREM-REM 等转期或不确定区域需要更多多尺度上下文来判断边界。固定上下文模型无法区分这两类情形，可能导致边界延迟、N1 误判或 hypnogram 过度平滑。

TGCM 的方法结构应包括：

- epoch encoder：提取每个 30 秒 EEG epoch 的局部表征。
- short / mid / long 多尺度上下文分支：分别对应约 5 分钟、30 分钟、90 分钟上下文。
- transition head：由 hypnogram 自动生成的边界窗口标签监督，预测当前 epoch 的转期概率。
- context gate：用转期概率动态融合不同上下文尺度。
- stage classifier：输出 W/N1/N2/N3/REM。

论文贡献应重新表述为：

- 提出一个转期引导的自适应上下文调制模块，而不是又一个长上下文 Transformer。
- 设计边界感知训练目标，使模型在稳定区保持一致，在转期区保留变化敏感性。
- 通过 transition-window 指标和 gate 可视化证明模型确实学习到不同阶段边界的上下文需求。

后续实验必须包含 only-transition-head baseline，用来证明收益不是来自 TransSleep-style 辅助任务本身；还必须包含 fixed short/mid/long context baselines，用来证明收益不是来自单纯增加上下文长度。

## 统一研究规划：转期不确定性引导的 N1 识别

最新研究主线已从“方向1 N1 标签不确定性”和“方向2 TGCM 自适应上下文”两条并行路线，收束为一个统一问题：

> 用转期/边界不确定性同时调节标签监督和上下文建模，以提升 EEG 睡眠分期中的 N1 识别。

第一篇文章仍应优先聚焦 N1 标签不确定性。核心贡献是 stage-adjacent soft labels 与 transition-window uncertainty，而不是跨数据集泛化，也不是一开始就把 TGCM 写成大模型主线。TGCM 的合理定位是第二阶段增强模块：如果边界不确定样本确实需要更多或不同尺度的上下文，TGCM 应在转期窗口提高 mid/long gate，在稳定区偏向 short gate。

当前执行顺序应固定为：

1. 先完成 unified protocol 和实验前注册；
2. 实现数据统计与 N1/转期/校准指标；
3. 在 Sleep-EDF 建立 hard CE、class imbalance、uniform smoothing baseline；
4. 验证 stage-adjacent smoothing、transition smoothing/downweighting、A+B hybrid；
5. 在 ISRUC 复现；
6. 再实现 TGCM 和 TGCM + soft label；
7. 最后做错误分析、gate 可视化和 Sleep-EDF↔ISRUC robustness check。

成功标准不能只看 overall accuracy。必须同时报告 N1 F1、transition-window N1 F1、W↔N1/N1↔N2 混淆、ECE、N1 overprediction rate、boundary delay 和 fragmentation error。

## GitHub-服务器-Codex 协作框架

由于本机没有可用 GPU，实验执行改为 GitHub 与远程服务器协作。协作分支固定为 `codex/n1-label-uncertainty`，服务器通过 SSH + tmux 运行训练，轻量结果提交回 GitHub。仓库只保存 `status.json`、`metrics.csv`、`summary.json`、`analysis.md` 和少量图表；原始数据、checkpoint、完整日志保留在服务器。

当前已建立第 0-3 阶段的工程接口：`src/n1_uncertainty/` 提供标签映射、转期窗口、soft label、metrics、状态文件和基础 NPZ 训练入口；`scripts/remote/` 提供运行、同步和状态检查脚本；`experiments/transition_uncertainty_guided_n1/configs/` 提供 smoke、Sleep-EDF baseline、Sleep-EDF soft label、ISRUC 复现和 TGCM 占位配置。

重要限制：本机默认 `python.exe` 不可访问，因此 Python smoke test 需要在服务器执行。`tgcm_sleepedf` 目前是第 4 阶段配置占位；在实现真正 context gate 前不应运行，否则会产生误导。
