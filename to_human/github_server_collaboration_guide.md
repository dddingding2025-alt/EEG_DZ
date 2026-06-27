# GitHub-服务器-Codex 协作指南

日期：2026-06-26  
分支：`codex/n1-label-uncertainty`  
运行方式：远程服务器 `SSH + tmux`  
结果回传：小型 CSV/JSON/Markdown/PNG 提交到 GitHub。

## 1. 职责分工

- Codex：写代码、配置实验、分析 GitHub 上的轻量结果、修复失败并推送。
- 你：在服务器执行部署、更新和运行命令；确认数据放在 `DATA_ROOT`。
- GitHub：唯一同步中心；不传原始数据、checkpoint 和完整日志。
- 服务器：保存 GPU 训练过程中的大文件，尤其是数据、缓存、checkpoint 和完整日志。

## 2. 首次部署

```bash
git clone https://github.com/dddingding2025-alt/EEG_DZ.git
cd EEG_DZ
git checkout codex/n1-label-uncertainty

conda create -n eeg-n1 python=3.10 -y
conda activate eeg-n1
bash scripts/remote/install_server_deps.sh

export DATA_ROOT=/path/to/eeg_data
export RUN_ROOT=/path/to/eeg_runs
git config user.name "remote-runner"
git config user.email "remote-runner@example.com"
```

服务器驱动为 NVIDIA 535.x / CUDA 12.2 时，默认使用 `requirements-cu121.txt` 安装 `torch==2.5.1+cu121`。不要直接运行 `pip install torch`，否则 pip 可能装到 CPU 版或需要更高驱动的 CUDA 轮子。

第一版真实训练默认读取：

```text
$DATA_ROOT/sleepedf/preprocessed.npz
$DATA_ROOT/isruc/preprocessed.npz
```

NPZ 必须包含：

- `x`: shape `(n_epochs, n_channels, n_samples)` 或 `(n_epochs, n_samples)`；
- `y`: 0-4 整数标签，顺序为 `W/N1/N2/N3/REM`；
- `subject`: 每个 epoch 的 subject id，用于 subject-independent split。

## 3. 服务器 smoke test

先检查数据格式：

```bash
conda activate eeg-n1
cd EEG_DZ
export DATA_ROOT=~/data
bash scripts/remote/inspect_data.sh sleepedf
```

如果输出 `verdict: ready_npz`，可以直接跑真实训练。
如果输出 `verdict: raw_edf_needs_conversion`，说明你现在是原始 Sleep-EDF `.edf` 文件，还需要先转换成：

```text
$DATA_ROOT/sleepedf/preprocessed.npz
```

该 NPZ 需要包含 `x`、`y`、`subject` 三个数组。

Sleep-EDF 原始 EDF 转换命令：

```bash
conda activate eeg-n1
cd EEG_DZ
git pull --ff-only
bash scripts/remote/install_server_deps.sh
export DATA_ROOT=~/data
bash scripts/remote/prepare_sleepedf.sh
bash scripts/remote/inspect_data.sh sleepedf
```

如果想先快速试转两晚数据：

```bash
export MAX_PAIRS=2
bash scripts/remote/prepare_sleepedf.sh
unset MAX_PAIRS
```

默认行为：提取 `Fpz-Cz`，按 30 秒 epoch，采样率重采样到 100 Hz，合并 Sleep stage 3/4 为 N3，并保留入睡前后各 30 分钟清醒片段。

```bash
tmux new -s n1_smoke
conda activate eeg-n1
cd EEG_DZ
bash scripts/remote/run_experiment.sh --smoke
bash scripts/remote/sync_results.sh
```

如果 smoke test 成功，GitHub 上应出现：

```text
experiments/transition_uncertainty_guided_n1/runs/latest.json
experiments/transition_uncertainty_guided_n1/runs/<run_id>/status.json
experiments/transition_uncertainty_guided_n1/runs/<run_id>/metrics.csv
experiments/transition_uncertainty_guided_n1/runs/<run_id>/summary.json
experiments/transition_uncertainty_guided_n1/runs/<run_id>/analysis.md
```

## 4. 第一阶段 baseline

```bash
tmux new -s n1_baseline
conda activate eeg-n1
cd EEG_DZ
git pull --ff-only
export DATA_ROOT=/path/to/eeg_data
bash scripts/remote/run_experiment.sh baseline_sleepedf
```

另开一个 tmux 或在训练结束后同步：

```bash
cd EEG_DZ
bash scripts/remote/watch_and_sync.sh
```

默认每 10 分钟尝试提交一次轻量结果。

## 5. Codex 推送修复后的服务器更新

```bash
cd EEG_DZ
git fetch origin
git checkout codex/n1-label-uncertainty
git pull --ff-only
conda activate eeg-n1
bash scripts/remote/install_server_deps.sh
bash scripts/remote/run_experiment.sh --resume <run_id> baseline_sleepedf
```

如果不是 baseline，请把最后的配置名替换为：

- `softlabel_sleepedf`
- `replicate_isruc`
- `tgcm_sleepedf`

## 6. Codex 监控逻辑

Codex 周期性读取远端分支中的：

```bash
git fetch origin codex/n1-label-uncertainty
git show origin/codex/n1-label-uncertainty:experiments/transition_uncertainty_guided_n1/runs/latest.json
```

判断规则：

- `running` 且 30 分钟内更新：继续等待；
- `running` 但超过 60 分钟无更新：提醒你检查服务器 tmux/GPU 进程；
- `failed`：读取 `last_error`，修复代码后推送；
- `completed`：读取 `summary.json` 和 `metrics.csv`，更新 findings 并决定下一实验。

## 7. 实验顺序

1. `--smoke`
2. `baseline_sleepedf`
3. `softlabel_sleepedf`
4. `replicate_isruc`
5. `tgcm_sleepedf`

真实研究结论只从第 2 步开始计入，smoke test 只证明流程可用。

注意：当前已实现第 0-3 阶段所需的基础训练入口和 N1 标签不确定性工具；`tgcm_sleepedf` 是第 4 阶段配置占位。只有在后续实现 TGCM context gate 后，才应运行第 5 步。
