# Protocol: Transition-Uncertainty Guided N1 Sleep Staging

Status: planned; confirmatory protocol should be committed before running experiments.  
Date: 2026-06-26  
Primary article direction: N1 label uncertainty.  
Second-stage enhancement: TGCM adaptive context.

## 1. Research Question

Can transition/boundary uncertainty improve N1 sleep stage recognition by guiding both soft-label supervision and adaptive context modeling?

The first confirmatory claim is about N1 label uncertainty, not domain generalization and not a new backbone. TGCM is tested after the soft-label method to determine whether boundary-uncertain epochs also require adaptive context.

## 2. Confirmatory Hypotheses

H1: Stage-adjacent soft labels improve N1 F1 and calibration over hard CE, class-weighted CE, focal loss, balanced sampling, and uniform label smoothing.

H2: Transition-window stronger softening or hard-loss downweighting improves transition-window N1 F1 and boundary-adjacent ECE without materially harming stable-epoch performance.

H3: TGCM improves transition-window metrics over fixed-context and only-transition-head baselines; TGCM + soft labels provides additional gains if label uncertainty and context demand are coupled.

## 3. Data And Splits

Primary dataset:

- Sleep-EDF Expanded.
- Single-channel Fpz-Cz.
- Subject-independent split.
- Labels mapped to W/N1/N2/N3/REM.
- Movement/Unknown removed.

Replication dataset:

- ISRUC.
- Same label mapping, transition definition, and metrics.
- Used only after Sleep-EDF protocol is stable.

Optional robustness:

- Sleep-EDF -> ISRUC and ISRUC -> Sleep-EDF.
- MASS/SHHS if preprocessing and access cost are acceptable.

## 4. Transition Definition

Default:

```text
boundary tau: y_tau != y_{tau-1}
transition-window: |t - tau| <= 2
```

Report transition metrics separately for:

- W<->N1.
- N1<->N2.
- N2<->N3.
- NREM<->REM.

Run sensitivity analysis for `k in {1, 2, 3}` only after the default k=2 result is established.

## 5. Methods

### Baselines

- B0: hard-label CE.
- B1: class-weighted CE.
- B2: focal loss.
- B3: balanced sampler.
- B4: uniform label smoothing.
- B5: fixed short context.
- B6: fixed mid context.
- B7: fixed long context.
- B8: only-transition-head baseline.

### N1 Label-Uncertainty Methods

- M1: stage-adjacent soft label.
- M2: transition-window stronger smoothing.
- M3: transition-window hard-loss downweighting.
- M4: A+B hybrid, using global stage-adjacent soft labels plus stronger W<->N1/N1<->N2 transition uncertainty.

### TGCM Enhancement

- M5: TGCM with hard labels.
- M6: TGCM + M4 hybrid.

TGCM components:

- epoch encoder;
- short/mid/long context branches;
- transition head;
- context gate;
- stage classifier.

Default context scales:

- short: about 5 minutes;
- mid: about 30 minutes;
- long: about 90 minutes.

## 6. Soft-Label Defaults

Stage-adjacent soft target:

- W: main mass on W, small mass on N1.
- N1: main mass on N1, small mass on W and N2.
- N2: main mass on N2, small mass on N1 and N3.
- N3: main mass on N3, small mass on N2.
- REM: near-hard in v1; REM-W/N1 confusion is analyzed, not treated as a main soft-label target.

Initial epsilon grid:

- 0.05;
- 0.10;
- 0.15.

Default first report uses the best validation epsilon chosen within Sleep-EDF training only.

## 7. Metrics

Primary:

- N1 F1.
- N1 precision and recall.
- macro-F1.
- Cohen's kappa.
- ECE.
- W<->N1 and N1<->N2 confusion.

Transition-specific:

- transition-window N1 F1.
- transition-window macro-F1.
- stable-vs-transition performance gap.
- boundary-adjacent ECE.
- N1 overprediction rate.
- boundary delay.
- fragmentation error.

TGCM mechanism:

- stable vs transition gate-weight distribution.
- gate distribution by boundary type.
- gate behavior on typical errors.

## 8. Acceptance Criteria

M4 is considered successful if, compared with B0-B4:

- N1 F1 or transition-window N1 F1 improves consistently;
- macro-F1 and kappa do not materially decline;
- ECE does not worsen;
- N1 overprediction rate remains controlled.

M6 is considered successful if, compared with B5-B8 and M4:

- at least one core transition metric improves;
- regular macro-F1/kappa remains competitive;
- gate weights differ meaningfully between stable and transition windows.

## 9. Failure Interpretation

If B1 class-weighted CE explains all N1 gains:

- the current setup supports class imbalance more than label uncertainty; report this and narrow the article.

If soft labels raise recall but collapse precision:

- smoothing is too strong or applied too broadly; reduce epsilon or restrict stronger smoothing to transition windows.

If transition-window metrics do not improve:

- label-change windows may be too crude; use teacher entropy or multi-rater distributions as uncertainty proxies.

If TGCM adds no benefit:

- keep TGCM as a negative extension; do not force it into the first article.

## 10. Execution Order

1. Implement data statistics and transition-window labeling.
2. Implement N1, transition, calibration, boundary delay, and fragmentation metrics.
3. Run B0-B4 on Sleep-EDF.
4. Run M1-M4 on Sleep-EDF.
5. Replicate B0-B4 and M1-M4 on ISRUC.
6. Run B5-B8 on Sleep-EDF.
7. Run M5-M6 and TGCM ablations.
8. Perform error analysis and gate visualization.
9. Run optional Sleep-EDF<->ISRUC robustness checks.

## 11. Reporting Discipline

- Confirmatory experiments must follow this protocol.
- Any additional trial is exploratory unless added to a new protocol before execution.
- Report negative results with what they rule out.
- Do not select a final story from overall accuracy alone.
