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

优先做“标签不确定性 + 跨数据集泛化”的 EEG 睡眠分期研究。可检验假设是：显式建模人工评分不确定性、转期边界和阶段相邻性，可以比 hard-label 训练在外部数据集上更稳定，尤其改善 N1 和转期片段。

建议第一版实验只使用可公开获取的数据，先复现轻量 CNN/Transformer baseline，再加入 uncertainty-aware loss、transition-aware smoothing 或 multi-rater/soft-label 代理机制。主指标应为 macro-F1、Cohen's kappa、per-stage F1、N1 F1 和 leave-one-dataset-out 表现。

## 方向1深化：N1 标签不确定性

跨数据集泛化的含义是：模型在一个或多个数据集上训练后，在另一个未见过的数据集上测试。它比同数据集内划分更接近真实部署，因为导联、采样率、滤波、设备、人群、疾病构成和评分员习惯都会变化。

N1 难题不能归结为单一“模型不够强”。当前需要分开处理三类机制：

- Class imbalance：N1 样本少，模型偏向 W/N2；可用 class weight、focal loss、GAN/SMOTE、balanced sampler 作为基线。
- Label uncertainty：N1 与转期 epoch 的人工评分分歧高；应测试 soft label、multi-rater consensus、uncertainty loss、reject option。
- Domain shift：换数据集/设备/人群后，N1 的弱特征更容易失效；应测试 leave-one-dataset-out、domain alignment、source selection、test-time adaptation。

下一步最小实验假设：stage-adjacent label smoothing 和 transition-aware smoothing 应优先改善 cross-dataset N1 F1、transition-window F1 和 calibration，而不一定显著提升 overall accuracy。
