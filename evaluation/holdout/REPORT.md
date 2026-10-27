# FormLens Phase 3.1 Independent Holdout Validation

This set was generated after the original 10-image evaluation was used for development tuning. It was not used to modify the pipeline, thresholds, or matching rules. No changes were made after inspecting these holdout results.

## Frozen configuration

See `config.json`. Detection uses ScreenParser at confidence 0.18, `imgsz=1280`, NMS IoU 0.30, compact-control aspect ratio maximum 1.8, association acceptance score 0.45, uncertain association below 0.70, and evaluation IoU 0.50.

## Metric definitions

- Detection precision = TP / (TP + FP). TP requires a predicted control and ground-truth control with the same normalized type and IoU >= 0.50. Extra predictions are FP.
- Detection recall = TP / (TP + FN). A ground-truth control without a matched prediction is FN.
- Detection F1 = harmonic mean of precision and recall.
- Label-association accuracy = correctly associated normalized label / IoU-matched detections. Unmatched or wrong labels count as incorrect; uncertain status does not receive credit unless the underlying label is correct.
- Exact OCR label coverage = ground-truth labels emitted exactly by OCR after normalization / all ground-truth labels. Missing OCR text counts as a miss, independently of detector matching.

## Holdout results

| Metric | Result |
|---|---:|
| Ground-truth controls | 47 |
| Predicted controls | 50 |
| True positives | 47 |
| False positives | 3 |
| False negatives | 0 |
| Detection precision | 94.0% |
| Detection recall | 100.0% |
| Detection F1 | 96.9% |
| Label-association accuracy | 91.5% |
| Exact OCR label coverage | 100.0% |

## Per-screenshot results

| Screenshot | Ground truth | Predicted | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| holdout_11.png | 4 | 4 | 4 | 0 | 0 |
| holdout_12.png | 4 | 4 | 4 | 0 | 0 |
| holdout_13.png | 5 | 6 | 5 | 1 | 0 |
| holdout_14.png | 6 | 7 | 6 | 1 | 0 |
| holdout_15.png | 5 | 6 | 5 | 1 | 0 |
| holdout_16.png | 4 | 4 | 4 | 0 | 0 |
| holdout_17.png | 5 | 5 | 5 | 0 | 0 |
| holdout_18.png | 4 | 4 | 4 | 0 | 0 |
| holdout_19.png | 5 | 5 | 5 | 0 | 0 |
| holdout_20.png | 5 | 5 | 5 | 0 | 0 |

## Failures

Association failures:
[
  {
    "image": "holdout_13.png",
    "field": "field_02",
    "expected": "Service category",
    "predicted": "New screenshot reserved for final validation.",
    "iou": 0.869
  },
  {
    "image": "holdout_15.png",
    "field": "field_04",
    "expected": "Option beta",
    "predicted": "Option gamma",
    "iou": 0.93
  },
  {
    "image": "holdout_15.png",
    "field": "field_05",
    "expected": "Option gamma",
    "predicted": "Priority",
    "iou": 0.93
  },
  {
    "image": "holdout_15.png",
    "field": "field_06",
    "expected": "Priority",
    "predicted": null,
    "iou": 0.961
  }
]

OCR misses:
None.

False positives:
[
  {
    "image": "holdout_13.png",
    "field": "field_01",
    "type": "search_input",
    "label": "Service category"
  },
  {
    "image": "holdout_14.png",
    "field": "field_02",
    "type": "search_input",
    "label": "New screenshot reserved for final validation."
  },
  {
    "image": "holdout_15.png",
    "field": "field_03",
    "type": "search_input",
    "label": "Option beta"
  }
]

## Limitations

This is a synthetic holdout, not a sample of production web pages. It tests layout variation and reproducibility, but does not establish performance on scanned paper forms, native applications, handwriting, severe compression, or unseen languages. The original development-set results must not be presented as independent generalization results.
