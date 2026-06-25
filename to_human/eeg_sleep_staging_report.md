# 基于 EEG 的睡眠分期研究汇报（第一轮）

日期：2026-06-25  
范围：2021-06-25 至 2026-06-25，主线为 EEG/含 EEG PSG 的自动睡眠分期。  
本轮目标：让零基础研究者快速理解领域现状、核心问题和下一步可做研究点。

## 1. 先把任务讲清楚

睡眠分期通常把整夜 PSG 或 EEG 信号切成 **30 秒 epoch**，每个 epoch 标注为 **W、N1、N2、N3、REM**。EEG 是核心信号，因为它直接反映脑电节律：清醒时 alpha/beta 更明显，N2 有 sleep spindle 和 K-complex，N3 有慢波，REM 常呈低幅混合频率并需结合眼动/肌电判断。

模型评估不能只看 accuracy。更重要的是：

- **macro-F1**：避免 N2 占比大导致 accuracy 虚高。
- **Cohen's kappa**：衡量与人工评分一致性，常用于睡眠分期论文。
- **per-stage F1**：必须单独看 N1、REM、N3。
- **cross-subject / cross-dataset performance**：比同数据集随机切分更接近真实部署。
- **calibration / uncertainty**：临床场景要知道模型什么时候不确定。

## 2. 研究现状：近五年的方法演进

### 2.1 CNN/RNN 到注意力模型：结构创新已经相对成熟

早期深度学习主线是 CNN 从 raw EEG 或时频图提取局部特征，再用 RNN、TCN 或 attention 建模整夜序列。近五年的轻量化和注意力模型，例如 DeepSleepNet-Lite、MSDAN、SSNet，继续沿着这个方向优化。

这一类工作说明了两件事：第一，睡眠分期确实高度依赖局部波形和上下文；第二，仅靠提出一个新网络结构，在公开小数据集上再涨一点 accuracy，已经很难构成强研究贡献。

### 2.2 Transformer 与长上下文：解决“单 epoch 看不懂”的问题

SleepTransformer 这类工作把 Transformer 引入睡眠分期，强调序列关系、可解释性和不确定性。后续研究普遍承认：单个 30 秒 epoch 的边界经常不清楚，前后几个 epoch 对判断非常重要。

长上下文模型的合理性很强，因为真实睡眠具有周期性：NREM/REM cycle、入睡潜伏期、夜间觉醒、阶段转换都不是独立事件。未来模型如果不能利用整夜结构，很容易在 N1 和转期片段上犯错。

### 2.3 自监督学习：从“缺标签”走向“跨域表示”

ContraWR、contrastive learning、masked autoencoder 方向尝试从大量未标注 EEG 中学通用表示。这条线很重要，因为睡眠 PSG 标注贵、慢、有主观差异，而医院和居家设备会持续产生大量未标注信号。

但本轮判断是：**自监督本身不是贡献终点**。更值得做的是证明它在哪些场景有用，例如少标签、跨数据集、跨设备、噪声标签或老年/疾病人群迁移。

### 2.4 跨数据集泛化：领域真正的硬问题

SleepDG、HASS、transferability 相关研究集中讨论一个现实问题：模型在一个数据集上训练很好，换一个医院、设备、导联、年龄结构或评分规则后就掉性能。Sleep-EDF 上的高分，不能直接推出临床可用。

跨域问题至少来自五类差异：

- 信号采集差异：导联、采样率、滤波、阻抗和设备噪声。
- 人群差异：年龄、疾病、药物、睡眠结构。
- 标注差异：评分员习惯、AASM/R&K 历史差异、epoch 边界。
- 数据协议差异：是否包含适应夜、是否筛除觉醒、通道组合。
- 训练评测差异：subject-independent 与随机 epoch split 的难度完全不同。

### 2.5 基础模型与任意传感器：新热点，但还没完全成熟

REVE、Hypnos、AnySleep、PhysioOmni、任意传感器生成式模型等代表 EEG/生理信号基础模型正在成为热点。它们的共同目标是用大规模、多任务、多模态数据预训练一个可迁移表示。

这条线潜力很大，但目前仍有几个未解决问题：预训练数据和下游评测不透明、计算成本高、外部临床验证不足、对少通道 EEG 的收益不稳定、可解释性和失败检测不足。对个人科研入门而言，直接训练大模型成本过高；更现实的是围绕“如何评测/适配/解释 EEG 基础模型”做文章。

### 2.6 可穿戴和居家 EEG：从模型问题变成系统问题

少通道头带 EEG 是睡眠检测落地的重要方向。难点不是简单五分类，而是低信噪比、佩戴移动伪迹、通道脱落、跨设备差异和用户长期变化。可穿戴场景还要求轻量推理、不确定性提示和失败回退机制。

因此，居家 EEG 的研究价值更可能在 **鲁棒性、校准、质量控制、个体化适应**，而不是单纯把实验室 PSG 模型压缩一下。

## 3. 深入问题分析

### 3.1 N1 是“模型和标签共同制造”的难点

N1 是清醒到睡眠的过渡期，占比低、边界模糊，人工评分一致性也低。很多模型的 overall accuracy 很高，但 N1 F1 很差。这个问题不能只靠更复杂模型解决，因为训练标签本身包含不确定性。

更合理的研究思路是：把 N1 和转期片段视为不确定样本，显式建模阶段相邻性、软标签、评分分歧或 uncertainty，而不是强迫模型对每个 epoch 给出过度自信的 hard label。

### 3.2 类别不均衡会掩盖模型缺陷

N2 往往占据最大比例，模型即使偏向 N2 也能拿到不错 accuracy。论文如果只报告 accuracy，可能看起来很强，实际对 N1、REM 或短暂觉醒毫无帮助。

后续研究必须固定报告 macro-F1、per-stage F1、kappa 和混淆矩阵。若做临床或居家方向，还应报告转期 epoch 表现和低质量信号下的拒识/告警能力。

### 3.3 评测不可比是领域痛点

同一个模型在不同论文里可能使用不同数据清洗、不同通道、不同 epoch 删除策略、不同 train/test split。尤其是随机 epoch split 会泄漏同一个人的睡眠结构，使结果明显乐观。

因此，后续实验应优先采用：

- subject-independent split；
- leave-one-dataset-out；
- fixed preprocessing；
- 同时报告 within-dataset 与 cross-dataset；
- 不把 Sleep-EDF 单数据集结果当作唯一主结论。

### 3.4 临床可解释性还不够

临床医生并不只想要一个标签，还会关心模型为什么判为 N2、是否捕捉到 spindle/K-complex、这个 epoch 是否接近边界、是否因肌电/眼电伪迹误判。Transformer attention、时频 saliency、LLM textbook alignment 等方向开始尝试解释，但离可审计系统还有距离。

一个有价值的目标是让模型输出“标签 + 不确定性 + 证据片段 + 信号质量提示”，而不是只输出五分类概率。

## 4. 推荐研究方向排序

| 排名 | 方向 | 新颖性 | 可行性 | 发表潜力 | 实验成本 | 判断 |
|---:|---|---|---|---|---|---|
| 1 | 标签不确定性 + 跨数据集泛化 | 高 | 中高 | 高 | 中 | 最推荐 |
| 2 | 转期感知的长上下文睡眠分期 | 中高 | 高 | 中高 | 中 | 很适合第一篇 |
| 3 | 少通道/居家 EEG 的信号质量感知模型 | 高 | 中 | 高 | 中高 | 偏落地 |
| 4 | EEG 基础模型的轻量适配与评测 | 高 | 中 | 高 | 中高 | 适合跟热点 |
| 5 | 睡眠分期可解释性与医学规则对齐 | 中高 | 中 | 中高 | 中 | 适合和 LLM/规则结合 |
| 6 | 合成 EEG 数据增强与隐私保护 | 中 | 中 | 中 | 中 | 可作为支线 |

### 方向 1：标签不确定性 + 跨数据集泛化

**核心假设**：把人工评分分歧、转期边界和阶段相邻性纳入训练目标，比普通 hard-label cross entropy 更能提升外部数据集上的 N1、REM 和 macro-F1。

**可做实验**：

- 数据：Sleep-EDF + ISRUC + MASS/SHHS 中至少两个。
- 基线：轻量 CNN/TCN 或小型 Transformer。
- 方法：label smoothing 按睡眠阶段邻接关系设计；转期 epoch 加 uncertainty 权重；用模型集成或 teacher 模型生成 soft label；训练时降低高不确定样本的过拟合。
- 评测：leave-one-dataset-out，macro-F1、kappa、N1 F1、转期片段 F1、calibration error。

**为什么值得做**：它不是单纯换模型，而是直接攻击领域真实痛点：人工标签不稳、N1 难、跨域掉点。

### 方向 2：转期感知的长上下文睡眠分期

**核心假设**：显式建模睡眠周期和阶段转换约束，能减少孤立误判，尤其改善 W-N1-N2、N2-N3、NREM-REM 的边界。

**可做实验**：

- 比较 30 秒、5 分钟、30 分钟、整夜上下文。
- 加入 transition prior 或 sequence-level loss。
- 单独评估转期前后若干 epoch。

**风险**：如果只把 Transformer 做长一点，创新性不足；必须把“转期”作为核心评测对象。

### 方向 3：少通道/居家 EEG 的信号质量感知模型

**核心假设**：在低质量 EEG 下，模型如果能先识别信号质量和伪迹，再进行分期或拒识，会比直接五分类更可靠。

**可做实验**：

- 模拟通道缺失、噪声、运动伪迹、采样率变化。
- 输出 sleep stage + signal quality + abstention。
- 在头带 EEG 或单通道数据上验证。

**价值**：贴近真实产品和居家监测，但数据获取和伪迹标注会更麻烦。

### 方向 4：EEG 基础模型的轻量适配与评测

**核心假设**：通用 EEG/生理基础模型在睡眠分期上并非总是优于专用模型；收益取决于数据规模、通道布局和外部域差异。

**可做实验**：

- 选择公开基础模型表示或复现小规模预训练。
- 比较 linear probe、LoRA/adapters、full fine-tuning。
- 主打少标签和跨数据集迁移。

**风险**：训练大模型成本高；建议做“评测与适配”而不是从零训练基础模型。

### 方向 5：可解释睡眠分期：从标签到证据

**核心假设**：将 spindle、K-complex、slow wave、REM 特征等医学规则与模型解释对齐，可以提升医生信任，也能发现模型是否学到伪相关。

**可做实验**：

- 输出重要时频片段或 EEG graphoelement 证据。
- 与规则检测器或医学文本知识对齐。
- 分析误判样本是否来自伪迹、边界还是真实模糊。

**风险**：解释性评估标准较难定义，需要小心避免只做漂亮可视化。

## 5. 不建议优先投入的方向

- **只改网络结构**：例如“某某 Transformer + Sleep-EDF accuracy 提升 0.5%”，除非有非常强的泛化或解释证据。
- **只做单数据集高分**：Sleep-EDF 很适合入门，但单独作为论文主结论太弱。
- **只做图像化 EEG + 视觉模型**：如果没有说明为什么时频图更稳、更泛化或更可解释，容易变成套模型。
- **只做基础模型口号**：没有外部验证、少标签分析和计算成本分析的大模型结果说服力不足。
- **忽略 N1 和转期**：这会绕开睡眠分期最核心的困难。

## 6. 我的建议：下一步研究点

如果我们要继续推进，我建议第一条主线定为：

> **面向跨数据集泛化的 uncertainty-aware EEG 睡眠分期：把人工标注不确定性、阶段转换和 N1 难分类显式纳入训练与评测。**

这条线的好处是：不需要从零训练超大模型；可以用公开数据；问题足够真实；容易设计清晰 ablation；结果如果成立，论文故事也比较完整。

最小可行实验路线：

1. 复现一个轻量 CNN/Transformer baseline。
2. 固定 Sleep-EDF、ISRUC、MASS/SHHS 中两个或三个数据集的预处理。
3. 做 within-dataset、cross-dataset、leave-one-dataset-out 三类评测。
4. 加入 uncertainty-aware label smoothing、transition-aware sample weighting 或 soft-label teacher。
5. 重点报告 N1 F1、macro-F1、kappa、转期片段表现和校准误差。

预期贡献可以写成：

- 证明 hard label 训练是跨域泛化和 N1 识别的瓶颈之一；
- 提出一个低成本、可插拔的 uncertainty-aware 训练框架；
- 给出比单数据集 accuracy 更可信的跨数据集评测协议；
- 展示哪些错误来自真实睡眠边界模糊，哪些来自模型缺陷。

## 7. 参考入口

完整文献表见 `literature/survey.md`，精读卡片见 `literature/papers/`。核心入口包括：

- Phan & Mikkelsen, automatic sleep staging review: https://arxiv.org/abs/2111.08446
- SleepTransformer: https://arxiv.org/abs/2105.11043
- ContraWR: https://arxiv.org/abs/2110.15278
- SleepDG: https://arxiv.org/abs/2401.05363
- Arbitrary sensor generative sleep staging: https://arxiv.org/abs/2408.15253
- REVE: https://arxiv.org/abs/2510.21585
- Sleep-EDF: https://physionet.org/content/sleep-edfx/1.0.0/
- SHHS: https://sleepdata.org/datasets/shhs
