# FormLens Phase 3 Evaluation

Generated: 10 reproducible synthetic English form screenshots covering two-column, left-label, dense-choice, stacked, three-column, mixed-order, wide-text, compact, multi-section, and right-aligned layouts. Ground truth is manually specified in `ground_truth.json`. Detection uses type-compatible IoU >= 0.50.

## Metrics

| Metric | Result |
|---|---:|
| Ground-truth controls | 54 |
| Predicted controls | 55 |
| Detection true positives | 54 |
| Detection false positives | 1 |
| Detection false negatives | 0 |
| Detection precision | 98.2% |
| Detection recall | 100.0% |
| Detection F1 | 99.1% |
| Label association accuracy (among IoU-matched detections) | 100.0% |
| Exact OCR label coverage (all ground-truth labels) | 100.0% |

Detection metrics are separate from OCR and matching metrics. OCR coverage checks whether RapidOCR emitted an exact label string; association accuracy checks whether the label attached to an IoU-matched control was the correct ground-truth label.

## Per-screenshot results

| Screenshot | Ground truth | Predicted | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
| form_01_two_column.png | 5 | 5 | 5 | 0 | 0 |
| form_02_left_labels.png | 4 | 4 | 4 | 0 | 0 |
| form_03_dense_choices.png | 8 | 8 | 8 | 0 | 0 |
| form_04_stacked.png | 4 | 4 | 4 | 0 | 0 |
| form_05_three_column.png | 7 | 7 | 7 | 0 | 0 |
| form_06_mixed_order.png | 5 | 6 | 5 | 1 | 0 |
| form_07_wide_text.png | 4 | 4 | 4 | 0 | 0 |
| form_08_compact.png | 6 | 6 | 6 | 0 | 0 |
| form_09_multi_section.png | 6 | 6 | 6 | 0 | 0 |
| form_10_right_aligned.png | 5 | 5 | 5 | 0 | 0 |

## Recurring errors and rule change

- Wrong label associations before the shape-filter change: 5 / 54 matched controls.
- After tightening compact-control geometry to reject boxes wider than 1.8× their height (or taller than 1.8× their width): 0 wrong label associations.
- Exact OCR label misses: 0.
- Remaining detection error: 1 false positive; this is reported separately from OCR and matching.

## Failure examples

Label-association failures after the rule change: None.

False-positive detections after the rule change:
[
  {
    "image": "form_06_mixed_order.png",
    "field": "field_06",
    "type": "text_input",
    "box": {
      "x": 136,
      "y": 622,
      "width": 895,
      "height": 153
    },
    "label": "Choose an option"
  }
]

## Artifacts

- `ground_truth.json`: control types, boxes, labels, and intended associations.
- `fixtures/`: 10 input screenshots.
- `annotated/`: pipeline outputs for visual review.
