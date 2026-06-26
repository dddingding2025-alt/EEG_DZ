# Protocol: N1 Label Uncertainty via Stage-Adjacent Soft Labels

Status: planned; aligned to the N1 label-uncertainty direction; no data downloaded; no training run.  
Date: 2026-06-26  
Primary question: N1 label uncertainty and transition-boundary modeling.  
Secondary check: cross-dataset robustness only after within-dataset effects are established.

Unified-plan note: this protocol remains the first-stage confirmatory protocol. TGCM is introduced later as an enhancement module through `experiments/transition_uncertainty_guided_n1/protocol.md`.

## 1. Research Question

Can stage-adjacent soft labels and transition-aware uncertainty weighting improve N1 sleep stage recognition compared with hard-label training and class-imbalance baselines?

The core mechanism is not domain generalization. Domain shift will be evaluated later as a robustness check because it is an independent deployment problem.

## 2. Hypotheses

H1: Stage-adjacent soft labels improve N1 F1 and calibration over hard-label CE, class-weighted CE, focal loss, and uniform label smoothing.

H2: Transition-window softening or uncertainty weighting improves transition-window N1 F1 without materially degrading stable-epoch performance.

H3: If multi-rater labels or ensemble teacher distributions are available, soft-consensus / teacher soft labels should outperform fixed smoothing; if not, stage-adjacent smoothing is a low-cost proxy.

## 3. Datasets

Minimum first-stage setting:

- Sleep-EDF: first reproducible dataset.
- ISRUC: independent replication dataset.

Optional later extensions:

- MASS or SHHS for larger robustness checks.
- Dreem Open Datasets / DOD-H / DOD-O for multi-rater label-distribution validation.

First-stage evaluation must be subject-independent within each dataset. Cross-dataset tests such as Sleep-EDF -> ISRUC are secondary robustness checks, not confirmatory tests for the main mechanism.

## 4. Backbone

Use one fixed lightweight backbone across all variants:

- Option 1: compact CNN/TCN.
- Option 2: compact Transformer.

The first implementation should prefer the simpler backbone that is easiest to reproduce. Architecture changes are not part of the main contribution.

## 5. Baselines

Required:

- B0: hard-label cross entropy.
- B1: class-weighted cross entropy.
- B2: focal loss.
- B3: balanced sampler.
- B4: uniform label smoothing.

Purpose:

- B1-B3 test whether gains are merely class-imbalance compensation.
- B4 tests whether gains come from generic smoothing rather than sleep-stage adjacency.

## 6. Proposed Variants

### A. Stage-Adjacent Soft Label

Replace one-hot labels with structured soft targets:

- W: main mass on W; small mass on N1.
- N1: main mass on N1; small mass on W and N2.
- N2: main mass on N2; small mass on N1 and N3.
- N3: main mass on N3; small mass on N2.
- REM: keep near-hard in v1; analyze REM-W/N1 errors separately.

Planned ablations:

- epsilon in {0.05, 0.10, 0.15}.
- N1-only smoothing vs all-stage adjacent smoothing.
- stage-adjacent smoothing vs uniform smoothing.

### B. Transition-Uncertainty Weighting

Define transition-window:

- Immediate rule: epoch `t` is transition if `y[t] != y[t-1]` or `y[t] != y[t+1]`.
- Window rule: include +/- k epochs around each label boundary, with k in {1, 2, 3}.

Training variants:

- stronger stage-adjacent smoothing inside transition-window;
- lower hard-label CE weight inside transition-window;
- optional auxiliary transition/uncertainty head.

Do not blindly upweight transition epochs. The hypothesis is that boundary labels are less certain, not that they should be fit harder.

### C. Soft-Consensus / Teacher Soft Labels

If multi-rater labels are available:

- use empirical rater distribution as target;
- compare against fixed stage-adjacent smoothing.

If only single-rater labels are available:

- train K-fold or seed ensemble teachers;
- use mean teacher probability as soft target;
- use entropy/disagreement to define uncertainty strength.

C is optional for v1 and can be moved to a follow-up experiment.

### D. Hybrid A+B

Main proposed method:

- apply stage-adjacent soft labels globally;
- apply stronger softening or lower hard-label weight around W<->N1 and N1<->N2 boundaries.

## 7. Metrics

Primary:

- N1 F1.
- N1 precision and recall.
- macro-F1.
- Cohen's kappa.
- expected calibration error (ECE).

Error analysis:

- W<->N1 confusion.
- N1<->N2 confusion.
- REM<->W/N1 confusion as secondary observation.

Transition-specific:

- transition-window N1 F1.
- stable-vs-transition performance gap.
- boundary-adjacent ECE.
- N1 overprediction rate.
- predicted N1 proportion vs true N1 proportion.

## 8. Success Criteria

Compared with B0-B4:

- N1 F1 or transition-window N1 F1 improves consistently.
- macro-F1 and kappa do not materially decrease.
- ECE does not worsen; improvement is preferred.
- N1 overprediction rate remains controlled.
- W<->N1 and N1<->N2 confusion changes are explainable, not just a recall/precision tradeoff hidden by one metric.

## 9. Failure Interpretation

If only class-weighted CE improves N1:

- the dominant factor may be class imbalance, and the uncertainty hypothesis is weak under the current setup.

If uniform smoothing matches stage-adjacent smoothing:

- gains may come from regularization; need stronger adjacency design or N1-specific smoothing.

If N1 recall rises but precision collapses:

- smoothing is too strong or transition-window is too wide.

If transition-window metrics do not improve:

- the label-change proxy may be too crude; use teacher entropy or multi-rater distributions.

If within-dataset works but cross-dataset robustness fails:

- domain shift should be treated as a separate second-stage paper component, not folded back into the core N1 uncertainty claim.

## 10. Implementation Order

1. Implement dataset statistics: stage proportions, N1 count, transition count, W-N1/N1-N2 boundary count.
2. Implement metrics: N1 F1, transition-window N1 F1, ECE, N1 overprediction, adjacent confusion matrix.
3. Train B0-B4 on Sleep-EDF subject-independent split.
4. Add Method A.
5. Add Method B.
6. Add Method D.
7. Replicate on ISRUC.
8. Run optional Sleep-EDF <-> ISRUC robustness checks.

## 11. Locked Assumptions for v1

- N1 is the primary target.
- REM is a secondary error-analysis stage, not a second main task.
- Cross-dataset generalization is not the core contribution.
- Multi-rater data is useful for validation but not required for the first implementation.
