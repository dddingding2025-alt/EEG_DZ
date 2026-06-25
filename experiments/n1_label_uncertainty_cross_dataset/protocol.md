# Protocol: N1 Label Uncertainty and Cross-Dataset Generalization

Status: planned, no data downloaded, no training run.  
Date: 2026-06-25  

## Research Question

Can explicit modeling of label uncertainty, transition boundaries, and sleep-stage adjacency improve external-dataset N1 F1, REM F1, macro-F1, and calibration compared with hard-label cross entropy?

## Datasets

Minimum planned setting:

- Source/target pair A: Sleep-EDF train -> ISRUC test.
- Source/target pair B: ISRUC train -> Sleep-EDF test.

Extension:

- Leave-one-dataset-out with Sleep-EDF, ISRUC, and MASS or SHHS.
- DOD-H/DOD-O as optional multi-rater evidence for uncertainty calibration, not as the first training target.

## Baselines

- Hard-label cross entropy.
- Class-weighted cross entropy.
- Focal loss.
- Balanced sampler.
- Compact CNN/TCN or compact Transformer with identical preprocessing across variants.

## Proposed Variants

- Stage-adjacent label smoothing:
  - N1 soft target spreads limited mass to W and N2.
  - N2 soft target spreads limited mass to N1 and N3.
  - N3 soft target spreads limited mass to N2.
  - REM soft target allows limited mass to W/N1 only as an EEG-only confusion hypothesis.
- Transition-aware smoothing:
  - Define transition epoch as an epoch whose label differs from at least one immediate neighbor.
  - Apply stronger smoothing or lower hard-label loss weight to transition epochs.
- Teacher soft labels:
  - Use cross-validation ensemble predictions as uncertainty proxies.
  - If multi-rater labels are available, prefer scorer distribution over teacher distribution.

## Evaluation

Required:

- macro-F1;
- Cohen's kappa;
- N1 F1;
- REM F1;
- transition-window F1;
- expected calibration error (ECE);
- confusion counts for W<->N1, N1<->N2, REM<->W/N1.

Report both:

- stable epochs;
- transition-window epochs.

## Confirmatory Hypotheses

H1: Stage-adjacent smoothing improves cross-dataset N1 F1 and ECE over hard CE and uniform smoothing.

H2: Transition-aware smoothing improves transition-window F1 without large degradation on stable epochs.

H3: Combining uncertainty-aware labels with domain-generalization or source-selection methods improves leave-one-dataset-out macro-F1 and N1 F1 more consistently than either component alone.

## Failure Interpretation

- If N1 F1 improves only within-dataset, the method is likely addressing class imbalance but not domain shift.
- If ECE improves but F1 does not, uncertainty modeling may be useful for reject/triage but not enough for classification.
- If cross-dataset performance drops after smoothing, source-target preprocessing or source selection may dominate label uncertainty.
- If transition-window F1 does not improve, the immediate-neighbor transition definition is too crude and should be replaced by teacher or multi-rater uncertainty.

## Next Implementation Step

Before training, lock preprocessing decisions:

- channel selection;
- sampling rate;
- filtering;
- label mapping;
- subject-independent splits;
- whether to include EOG/EMG or EEG-only in v1.
