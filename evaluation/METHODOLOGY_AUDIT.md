# FormLens Phase 3.1 Methodology Audit

## Tuning chronology

The original 10-image evaluation was **not** untouched. The first run produced 91.5% detection precision and 90.7% label-association accuracy. Inspection showed duplicate wide checkbox/radio regions. The compact-control aspect-ratio rule was then tightened from a width-only ratio of 3.0 to a symmetric maximum aspect ratio of 1.8. The development set was rerun and produced 98.2% precision, 100.0% recall, 99.1% F1, and 100.0% label-association accuracy.

Therefore, the original 10-image results are development-set results and must not be presented as independent generalization performance.

## Independent holdout

Ten new screenshots were generated after that tuning decision. The pipeline, threshold, IoU criteria, and matching rules were frozen before the holdout run. No code or configuration was changed after inspecting holdout failures. The holdout report is in `holdout/REPORT.md` and its frozen configuration is in `holdout/config.json`.

## Metric definitions

- Detection precision: `TP / (TP + FP)`. A true positive requires matching control type and IoU >= 0.50. Extra predictions are false positives.
- Detection recall: `TP / (TP + FN)`. Ground-truth controls without a compatible prediction are false negatives.
- Detection F1: harmonic mean of precision and recall.
- Label-association accuracy: correct normalized label attached to an IoU-matched control divided by all IoU-matched detections. Wrong, missing, or unmatched labels receive no credit. Uncertain status does not receive automatic credit.
- Exact OCR label coverage: ground-truth labels emitted exactly by OCR after normalization divided by all ground-truth labels. It is independent of detector matching.

## Reproducibility

The exact configuration for each run is saved in `config_development.json` and `holdout/config.json`. The benchmark generators and evaluators are `run_evaluation.py` and `run_holdout.py`.
