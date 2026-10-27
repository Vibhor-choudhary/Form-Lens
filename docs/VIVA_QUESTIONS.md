# FormLens Viva Questions and Short Answers

1. **What problem does FormLens solve?** It recovers visual form controls and nearby labels from a screenshot and exports a reviewable inventory.
2. **Was it trained from scratch?** No. ScreenParser and RapidOCR are pretrained models used for local inference; no project-specific training or fine-tuning was performed.
3. **Why use object detection?** OCR reads text but does not reliably locate checkboxes, radios, selects, or input rectangles.
4. **What does RapidOCR provide?** Text, OCR confidence, and text-region coordinates.
5. **How are labels matched?** Candidate labels are scored using relative geometry, reading order, distance, and control type; compact controls prefer nearby text to the right.
6. **What is IoU?** Intersection area divided by union area of predicted and ground-truth boxes.
7. **How is precision calculated?** `TP/(TP+FP)` using same type and IoU at least 0.50.
8. **How is recall calculated?** `TP/(TP+FN)`, where an annotated control without a match is a false negative.
9. **What is F1?** `2PR/(P+R)`, the harmonic mean of precision and recall.
10. **How is association accuracy separated from detection?** It is the proportion of IoU-matched detections whose normalized label is correct.
11. **What is exact OCR coverage?** Ground-truth labels emitted exactly by OCR after normalization divided by all ground-truth labels.
12. **Why can detector confidence not prove a correct label?** It measures visual-control prediction, not semantic label relation.
13. **Why is the holdout important?** The original ten-image set was used for development tuning, so a separate untouched holdout estimates generalization.
14. **What did the holdout show?** 94.0% precision, 100% recall, 96.9% F1, 91.5% association accuracy, and 100% exact OCR coverage.
15. **What did the real-world check show?** Five official forms produced 39.8% precision, 94.6% recall, 56.0% F1, 42.9% association accuracy, and 51.4% exact OCR coverage.
16. **Why did real-world precision fall?** Paper-form tables and administrative regions are out of domain for a screenshot-oriented detector.
17. **What is the main limitation?** Domain shift; scanned forms, handwriting, dense tables, and instructional prose create false positives and wrong associations.
18. **Why is processing local?** Privacy and reproducibility; screenshots remain on the Mac.
19. **How could it improve later?** Add domain-specific annotations and fine-tune or replace the detector, then evaluate on a new holdout.
20. **What is intentionally out of scope?** Browser autofill, cloud inference, training, fine-tuning, extra models, databases, and extensions.
