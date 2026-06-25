# Research Log

## 2026-06-25

- 启动第一轮文献调研，研究范围锁定为 EEG/含 EEG PSG 的自动睡眠五分类。
- 检查工作区：仅发现 `.codex` 和 `.git`，无既有文献或实验文件。
- 根据 autoresearch 结构创建 `literature/`、`to_human/`、`data/`、`experiments/`、`src/`、`paper/`。
- 完成第一轮文献筛选：37 篇近五年论文/预印本，25 篇核心分析条目，31 张论文卡片，7 个常用数据源。
- 形成中文汇报：`to_human/eeg_sleep_staging_report.md`。
- 主要判断：下一步最值得推进的是“标签不确定性与跨数据集泛化”，而不是单纯提出一个新 Transformer 变体。

## 2026-06-25 方向1深化

- 针对用户提出的“跨数据集泛化”不清楚的问题，形成正式解释：训练集和测试集来自不同数据集/中心/设备/人群，用于检验模型是否学到可迁移睡眠规律。
- 新增方向1专题报告：`to_human/direction1_n1_uncertainty_cross_dataset_report.md`。
- 新增实验协议草案：`experiments/n1_label_uncertainty_cross_dataset/protocol.md`。
- 补充方向1文献链：19 条 N1、multi-rater、uncertainty、label noise、domain generalization、cross-dataset adaptation 相关条目。
- 新增 9 张论文卡片，使 `literature/papers/` 累计达到 40 张。
- 形成三个可执行假设：stage-adjacent soft label、transition-aware training、label uncertainty + domain generalization 联合建模。
