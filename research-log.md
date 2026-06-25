# Research Log

## 2026-06-25

- 启动第一轮文献调研，研究范围锁定为 EEG/含 EEG PSG 的自动睡眠五分类。
- 检查工作区：仅发现 `.codex` 和 `.git`，无既有文献或实验文件。
- 根据 autoresearch 结构创建 `literature/`、`to_human/`、`data/`、`experiments/`、`src/`、`paper/`。
- 完成第一轮文献筛选：37 篇近五年论文/预印本，25 篇核心分析条目，31 张论文卡片，7 个常用数据源。
- 形成中文汇报：`to_human/eeg_sleep_staging_report.md`。
- 主要判断：下一步最值得推进的是“标签不确定性与跨数据集泛化”，而不是单纯提出一个新 Transformer 变体。
- 用户选择继续深挖“转期感知的长上下文睡眠分期”作为第一篇文章方向。
- 建立 20 分钟 heartbeat：`autoresearch-transition-aware-sleep-staging`，用于持续推进本线程 autoresearch。
- 完成第二轮专题调研：新增 `literature/transition_context_survey.md`、`to_human/transition_aware_sleep_staging_report.md`、`experiments/transition-aware-long-context/protocol.md`。
- 新增关键论文卡片：TransSleep、L-SeqSleepNet、S4Sleep、长相关性分析、continuous sleep depth、NeuroLingua、context-aware temporal modeling、ProductGraphSleepNet。
- 第二轮判断：该方向可作为第一篇文章，但贡献应聚焦 transition-centered evaluation 和轻量 sequence regularization，而非单纯更长上下文模型。

## 2026-06-25 方向1深化

- 针对用户提出的“跨数据集泛化”不清楚的问题，形成正式解释：训练集和测试集来自不同数据集/中心/设备/人群，用于检验模型是否学到可迁移睡眠规律。
- 新增方向1专题报告：`to_human/direction1_n1_uncertainty_cross_dataset_report.md`。
- 新增实验协议草案：`experiments/n1_label_uncertainty_cross_dataset/protocol.md`。
- 补充方向1文献链：19 条 N1、multi-rater、uncertainty、label noise、domain generalization、cross-dataset adaptation 相关条目。
- 新增 9 张论文卡片，使 `literature/papers/` 累计达到 40 张。
- 形成三个可执行假设：stage-adjacent soft label、transition-aware training、label uncertainty + domain generalization 联合建模。
