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
- 第二轮当时判断：该方向可作为第一篇文章，但贡献应聚焦 transition-centered evaluation 和轻量 sequence regularization，而非单纯更长上下文模型；该表述已在 2026-06-26 被 TGCM 方法化修订取代。

## 2026-06-25 方向1深化

- 针对用户提出的“跨数据集泛化”不清楚的问题，形成正式解释：训练集和测试集来自不同数据集/中心/设备/人群，用于检验模型是否学到可迁移睡眠规律。
- 新增方向1专题报告：`to_human/direction1_n1_label_uncertainty_report.md`。
- 新增实验协议草案：`experiments/n1_label_uncertainty/protocol.md`。
- 补充方向1文献链：19 条 N1、multi-rater、uncertainty、label noise、domain generalization、cross-dataset adaptation 相关条目。
- 新增 9 张论文卡片，使 `literature/papers/` 累计达到 40 张。
- 当时形成三个可执行假设：stage-adjacent soft label、transition-aware training、label uncertainty + domain generalization 联合建模；第三项已在 2026-06-26 修订为后续 robustness check，不再作为方向1核心机制。

## 2026-06-26 方向1修订

- 根据用户反馈，确认 `Domain shift / 跨数据集泛化` 不应与 N1 标签不确定性绑定为同一核心问题；跨数据集泛化改为后续 robustness check。
- 研究主线修订为：通过阶段相邻软标签与转期不确定性建模提升 N1 睡眠阶段识别。
- 修订方向1汇报：`to_human/direction1_n1_label_uncertainty_report.md`，删除“跨数据集泛化”作为标题和主贡献。
- 新增专题文献报告：`literature/n1_label_uncertainty_survey.md`，按 class imbalance、transition/context、multi-rater uncertainty、soft label、medical label uncertainty 五类整理。
- 修订实验协议：`experiments/n1_label_uncertainty/protocol.md`，主设置改为 Sleep-EDF 与 ISRUC 的 subject-independent within-dataset evaluation。
- 更新 `findings.md`、`literature/survey.md` 和 `research-state.yaml`，确保后续执行聚焦 N1 标签不确定性而非 domain shift。

## 2026-06-26 方向2方法化修订

- 根据用户反馈，确认原“转期感知长上下文”方案偏实验创新，方法贡献不足。
- 将方向2正式修订为方法主导方案：Transition-Guided Context Modulation (TGCM)。
- 更新 `to_human/transition_aware_sleep_staging_report.md`，把文章主线改为“转期概率动态调制 short/mid/long 上下文尺度”。
- 更新 `experiments/transition-aware-long-context/protocol.md`，锁定 TGCM 的方法结构、训练目标、baseline、ablation 和验收标准。
- 更新 `findings.md` 和 `research-state.yaml`，确保后续研究状态聚焦 TGCM，而不是 transition-centered evaluation 本身。

## 2026-06-26 统一研究方案

- 根据用户要求，将 N1 标签不确定性与 TGCM 的重叠点统一为“转期/边界不确定性”。
- 明确第一篇文章主线为 N1 标签不确定性：stage-adjacent soft label + transition-window uncertainty。
- 明确 TGCM 作为第二阶段增强模块，用于验证边界不确定样本是否需要自适应上下文尺度。
- 新增统一研究规划：`to_human/n1_transition_uncertainty_research_plan.md`。
- 新增统一实验前注册 protocol：`experiments/transition_uncertainty_guided_n1/protocol.md`。
- 更新 `research-state.yaml` 与 `findings.md`，后续执行顺序改为先 Sleep-EDF N1 soft-label 方法，再 ISRUC 复现，最后 TGCM 扩展。

## 2026-06-26 GitHub-服务器协作框架

- 根据用户说明，本机无 GPU，实验转为远程服务器执行；协作分支固定为 `codex/n1-label-uncertainty`。
- 新增 N1 不确定性工具包：`src/n1_uncertainty/`，包含标签映射、转期窗口、soft label、metrics、状态写出、NPZ 训练入口和结果监控。
- 新增远程脚本：`scripts/remote/run_experiment.sh`、`sync_results.sh`、`watch_and_sync.sh`、`check_status.sh`。
- 新增实验配置：`smoke_synthetic.yaml`、`baseline_sleepedf.yaml`、`softlabel_sleepedf.yaml`、`replicate_isruc.yaml`、`tgcm_sleepedf.yaml`。
- 新增协作指南：`to_human/github_server_collaboration_guide.md`，规定服务器部署、tmux 运行、结果同步和 Codex 监控逻辑。
- 本机 Python 不可访问，未能执行本地 Python smoke test；应由服务器先执行 `bash scripts/remote/run_experiment.sh --smoke`。

## 2026-06-26 数据格式检查

- 用户已将 Sleep-EDF 数据下载到服务器 `~/data`，但不确定是否符合训练入口要求。
- 新增服务器检查脚本：`scripts/remote/inspect_data.sh sleepedf`。
- 新增检查模块：`src/n1_uncertainty/inspect_data.py`，可判定 `ready_npz`、`npz_at_nonstandard_path`、`raw_edf_needs_conversion` 或 `missing`。
- 当前训练入口仍要求 `$DATA_ROOT/sleepedf/preprocessed.npz`，包含 `x`、`y`、`subject` 三个数组；如果检查结果是 raw EDF，下一步需要实现或运行 EDF->NPZ 转换。

## 2026-06-26 Sleep-EDF 转换脚本

- 根据用户服务器输出，确认 `~/data` 下为原始 Sleep-EDF EDF：197 个 PSG、197 个 Hypnogram。
- 新增转换模块：`src/n1_uncertainty/prepare_sleepedf.py`。
- 新增服务器脚本：`scripts/remote/prepare_sleepedf.sh`。
- 默认转换为 `$DATA_ROOT/sleepedf/preprocessed.npz`，包含 `x`、`y`、`subject`、`night`、`stage_names`、`metadata`。
- 默认提取 `Fpz-Cz`，30 秒 epoch，目标采样率 100 Hz，Sleep stage 3/4 合并为 N3，剔除非 W/N1/N2/N3/REM 注释，保留睡眠段前后各 30 分钟 W。
