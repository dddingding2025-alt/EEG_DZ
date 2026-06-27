# Codex Handoff: N1 标签不确定性睡眠分期研究

本文件用于把当前会话和工作区交接给另一台有 GPU 的电脑上的 Codex。新 Codex 读完本文件后，应能知道我们要研究什么、已经做了什么、代码在哪里、如何继续实验。

## 1. 当前工作区与代码来源

- 当前本机工作文件夹：`C:\Users\Admin\.codex\worktrees\b690\脑电方向`
- GitHub 仓库：`https://github.com/dddingding2025-alt/EEG_DZ.git`
- 协作分支：`codex/n1-label-uncertainty`
- 交接时远端最新已知提交：`abf9c44 fix: select cuda 12.8 torch wheels for rtx 50`
- 本仓库不保存原始 EEG 数据、checkpoint、大日志；这些文件应留在各自运行机器本地。

新电脑最简单的获取方式：

```bash
git clone https://github.com/dddingding2025-alt/EEG_DZ.git
cd EEG_DZ
git checkout codex/n1-label-uncertainty
```

如果 GitHub 上已经包含本 README，则新 Codex 直接阅读根目录下的 `README_CODEX_HANDOFF_N1.md`。

## 2. 研究主线

主线已经从“跨数据集泛化 + N1”收敛为：

> 通过阶段相邻软标签与转期不确定性建模提升 EEG 睡眠分期中的 N1 识别。

核心判断：

- `class imbalance` 是 N1 难识别的重要因素，但不是唯一因素。
- `label uncertainty` 是本文的主要机制：N1 位于 W-N1-N2 边界，生理形态与人工评分都更模糊。
- `transition/boundary uncertainty` 是 N1 标签不确定性的可操作代理：转期窗口附近的 hard label 更可能过拟合。
- `domain shift / cross-dataset generalization` 不作为第一篇文章主贡献，只作为后续 robustness check。
- TGCM / 自适应上下文方法可作为第二阶段增强模块，不要一开始把论文写成大模型或大而全系统。

第一篇文章优先验证：

- Stage-adjacent soft label 是否优于 hard CE、class-weighted CE、focal loss、balanced sampler、uniform smoothing。
- Transition-window stronger smoothing / downweighting 是否能提升 N1 F1、transition-window N1 F1 和 calibration。
- 是否能减少 W<->N1、N1<->N2 混淆，而不是简单把更多样本预测成 N1。

## 3. 重要研究文档

推荐新 Codex 按这个顺序阅读：

1. `experiments/transition_uncertainty_guided_n1/protocol.md`
2. `to_human/n1_transition_uncertainty_research_plan.md`
3. `to_human/direction1_n1_label_uncertainty_report.md`
4. `literature/n1_label_uncertainty_survey.md`
5. `literature/survey.md`
6. `findings.md`
7. `research-log.md`

协议中的关键假设：

- H1: Stage-adjacent soft labels improve N1 F1 and calibration over ordinary hard-label baselines.
- H2: Transition-window stronger smoothing or hard-loss downweighting improves boundary N1 behavior without harming stable epochs.
- H3: TGCM is an enhancement to test whether boundary-uncertain epochs need adaptive context.

## 4. 已实现代码结构

核心 Python 包：

```text
src/n1_uncertainty/
  labels.py              label mapping: W/N1/N2/N3/REM
  transitions.py         transition-window mask
  soft_labels.py         stage-adjacent soft targets
  metrics.py             macro-F1, kappa, N1 F1, transition N1 F1, ECE, etc.
  prepare_sleepedf.py    raw Sleep-EDF EDF -> preprocessed NPZ
  inspect_data.py        inspect raw EDF / preprocessed NPZ data layout
  training.py            lightweight TinyCNN trainer and baseline/soft-label variants
  run_experiment.py      unified experiment entrypoint
  status.py              write status.json, metrics.csv, summary.json, analysis.md
  monitor.py             lightweight status inspection
```

远程/本地 bash 入口：

```text
scripts/remote/
  install_server_deps.sh     install Python deps and CUDA-specific PyTorch
  inspect_data.sh            inspect Sleep-EDF/ISRUC data format
  prepare_sleepedf.sh        convert Sleep-EDF raw EDF to NPZ
  run_experiment.sh          run smoke/baseline/softlabel configs; supports --gpu
  sync_results.sh            commit/push lightweight results, optional if running locally
  watch_and_sync.sh          periodic result sync loop
  check_status.sh            inspect status files
```

实验配置：

```text
experiments/transition_uncertainty_guided_n1/configs/
  smoke_synthetic.yaml
  baseline_sleepedf.yaml
  softlabel_sleepedf.yaml
  replicate_isruc.yaml
  tgcm_sleepedf.yaml
```

当前已真正实现第 0-3 阶段基础能力：数据检查、Sleep-EDF 转换、baseline 训练、soft-label 训练目标和指标。`tgcm_sleepedf.yaml` 目前仍是第四阶段占位，TGCM 结构还没有真正实现，不要先跑 TGCM。

## 5. 环境安装

推荐在 Linux / WSL2 / Git Bash 可运行 bash 的环境里操作，因为当前脚本是 `.sh`。新电脑如果是 Windows，建议使用 WSL2 Ubuntu 并确认 GPU 可被 PyTorch 访问。

创建环境：

```bash
conda create -n eeg-n1 python=3.10 -y
conda activate eeg-n1
bash scripts/remote/install_server_deps.sh
```

依赖逻辑：

- 基础依赖在 `requirements.txt`。
- 普通 CUDA 12.2 / 535 驱动环境使用 `requirements-cu121.txt`，安装 `torch==2.5.1+cu121`。
- RTX 50 系列 / Blackwell 显卡使用 `requirements-cu128.txt`，安装 `torch==2.7.0+cu128`。
- `install_server_deps.sh` 会尝试通过 `nvidia-smi` 自动选择 cu121/cu128，并打印：
  - `torch`
  - `torch cuda runtime`
  - `cuda available`
  - `cuda device`

如果自动选择不合适，可以手动指定：

```bash
PYTORCH_REQUIREMENTS=requirements-cu121.txt bash scripts/remote/install_server_deps.sh
PYTORCH_REQUIREMENTS=requirements-cu128.txt bash scripts/remote/install_server_deps.sh
```

## 6. 数据准备

第一阶段数据：Sleep-EDF Expanded。

推荐数据目录：

```text
DATA_ROOT=/path/to/eeg_data
$DATA_ROOT/raw/sleep-edf/sleep-cassette/*.edf
```

旧服务器上的实际数据曾是：

```text
/home/nefu1020230004/code/EEG/data/raw/sleep-edf/sleep-cassette/
```

新电脑上不需要完全一样，只要设置 `DATA_ROOT` 即可：

```bash
export DATA_ROOT=/path/to/eeg_data
bash scripts/remote/inspect_data.sh sleepedf
```

如果输出 `raw_edf_needs_conversion`，说明检测到了原始 EDF，需要转换：

```bash
export DATA_ROOT=/path/to/eeg_data
bash scripts/remote/prepare_sleepedf.sh
bash scripts/remote/inspect_data.sh sleepedf
```

转换输出：

```text
$DATA_ROOT/sleepedf/preprocessed.npz
```

NPZ 需要包含：

- `x`: `(n_epochs, n_channels, n_samples)` 或 `(n_epochs, n_samples)`
- `y`: 0-4 integer labels, order is `W/N1/N2/N3/REM`
- `subject`: each epoch's subject id

已修过的 Sleep-EDF 坑：

- 某些 night 没有 Sleep stage 4，早期转换会报 `No matching events found for Sleep stage 4`。已在 `9f130d6` 修复，转换时只使用当前文件实际存在的 event id。
- Stage 3/4 会合并为 N3。
- 默认提取 `Fpz-Cz`，30 秒 epoch，重采样到 100 Hz，保留睡眠前后 30 分钟 wake。

## 7. 如何运行实验

先 smoke test，不读取真实数据，只检查环境、指标、结果写出：

```bash
bash scripts/remote/run_experiment.sh --gpu 0 --smoke
```

多显卡时：

```bash
bash scripts/remote/run_experiment.sh --gpu 1 baseline_sleepedf
```

`--gpu 1` 会设置 `CUDA_VISIBLE_DEVICES=1`。程序内部看到的是 `cuda:0`，实际对应物理第 1 张卡。

也可以这样写：

```bash
GPU_ID=1 bash scripts/remote/run_experiment.sh baseline_sleepedf
CUDA_VISIBLE_DEVICES=1 bash scripts/remote/run_experiment.sh baseline_sleepedf
```

第一阶段 baseline：

```bash
export DATA_ROOT=/path/to/eeg_data
bash scripts/remote/run_experiment.sh --gpu 0 baseline_sleepedf
```

baseline variants:

- `hard_ce`
- `class_weighted_ce`
- `focal_loss`
- `balanced_sampler`
- `uniform_smoothing`

第二阶段 soft-label:

```bash
export DATA_ROOT=/path/to/eeg_data
bash scripts/remote/run_experiment.sh --gpu 0 softlabel_sleepedf
```

soft-label variants:

- `stage_adjacent_eps_005`
- `stage_adjacent_eps_010`
- `transition_smoothing`
- `hybrid_softlabel_downweight`

结果文件写到：

```text
experiments/transition_uncertainty_guided_n1/runs/<run_id>/
  status.json
  metrics.csv
  summary.json
  analysis.md
```

如果在新电脑本地直接跑 Codex，不一定需要 `sync_results.sh`。它主要服务旧的服务器-GitHub-Codex 三端协作模式。

## 8. 旧服务器运行状态

我们曾在旧服务器上运行过 smoke 和 `baseline_sleepedf`。

旧服务器输出显示有一个本地结果提交：

```text
1635561 research(results): sync baseline_sleepedf-20260627-015549
```

并且旧服务器本地存在这些结果文件：

```text
experiments/transition_uncertainty_guided_n1/runs/latest.json
experiments/transition_uncertainty_guided_n1/runs/baseline_sleepedf-20260627-015549/summary.json
experiments/transition_uncertainty_guided_n1/runs/baseline_sleepedf-20260627-015549/analysis.md
experiments/transition_uncertainty_guided_n1/runs/baseline_sleepedf-20260627-015549/metrics.csv
experiments/transition_uncertainty_guided_n1/runs/baseline_sleepedf-20260627-015549/status.json
```

但截至本交接 README 编写前，GitHub 远端分支仍没有 `runs/latest.json`，说明旧服务器的结果提交大概率没有成功 push。既然现在计划换到一台有 GPU 的新电脑，最简单路线是：不要继续修旧服务器同步，直接在新电脑重新跑 baseline。

## 9. 下一步建议

新电脑 Codex 接手后，按这个顺序做：

1. 确认仓库在 `codex/n1-label-uncertainty` 分支。
2. 配好 `eeg-n1` 环境，确认 `torch.cuda.is_available()` 为 True。
3. 设置 `DATA_ROOT`，检查 Sleep-EDF 数据。
4. 如果只有 raw EDF，先运行 `prepare_sleepedf.sh`。
5. 运行 `--smoke`，确认结果写出。
6. 运行 `baseline_sleepedf`，读取 `metrics.csv/summary.json`。
7. 先分析 baseline：N1 F1、N1 precision/recall、macro-F1、kappa、ECE、transition N1 F1、N1 overprediction。
8. 如果 baseline 正常，再运行 `softlabel_sleepedf`。
9. 对比 baseline vs soft-label，不要只看 overall accuracy。
10. 如果 stage-adjacent / transition smoothing 有收益，再考虑 ISRUC 复现。
11. TGCM 只在 soft-label 主假设站住后实现。

核心判断规则：

- 如果 class-weighted CE 已解释全部 N1 提升，说明当前设置更像 class imbalance 研究，需调整论文故事。
- 如果 soft label 只提高 recall 但 precision 崩溃，说明 smoothing 太强或应用太宽，应降低 epsilon 或只在 transition-window 使用。
- 如果 transition-window 指标不提升，说明 k=2 标签边界可能太粗，需要考虑 teacher entropy、多评分员数据或更细的转期代理。
- 如果 macro-F1/kappa 明显下降，即使 N1 F1 上升，也不能宣称方法成功。

## 10. 给新 Codex 的一句话任务

可以把下面这段直接发给新电脑上的 Codex：

```text
请阅读仓库根目录的 README_CODEX_HANDOFF_N1.md，并继续“通过阶段相邻软标签与转期不确定性建模提升 EEG 睡眠分期中的 N1 识别”这个项目。当前先不要做 TGCM，也不要把跨数据集泛化作为主贡献。请先在本机 GPU 环境中跑通 Sleep-EDF smoke、preprocessing、baseline_sleepedf，然后读取 runs/<run_id>/metrics.csv 和 summary.json，分析 baseline 是否可信，再决定是否运行 softlabel_sleepedf。
```

## 11. 不要做的事

- 不要把 raw Sleep-EDF、ISRUC、SHHS、MASS 数据提交到 Git。
- 不要提交 checkpoint、大日志、缓存。
- 不要把跨数据集泛化重新作为第一篇文章标题。
- 不要一开始实现复杂 TGCM，先用固定轻量 backbone 验证训练目标是否有效。
- 不要只报告 accuracy；N1 F1、transition-window N1 F1、precision/recall、ECE 和混淆矩阵更关键。

