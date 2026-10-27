# FormLens MVP

Local screenshot-to-field-inventory prototype. It runs pretrained ScreenParser for visual controls and RapidOCR for visible English labels, then matches them with deterministic geometry rules. Feature development is frozen for submission.

## Run

```bash
.venv/bin/streamlit run app.py
```

Open the local URL printed by Streamlit and upload a PNG, JPEG, or WebP blank-form screenshot.

## Test sample

```bash
.venv/bin/python tests/create_sample.py
.venv/bin/python tests/test_e2e.py
```

The generated image is `tests/fixtures/english_registration_form.png`; the smoke test writes validated output files to `outputs/`.

## Output

The interface renders an annotated image and exposes PNG and complete JSON downloads. The image uses thin control outlines, separate dashed OCR regions, compact field IDs, and match lines. Each field contains detector class, normalized control type, bounding box, nearby OCR label, detector/OCR/matching confidence values, explicit match status (`Matched`, `Uncertain`, or `Unmatched`), and a review flag. Filters are available for control type and match status; selecting a field highlights it in magenta.

Hindi OCR and browser DOM matching are intentionally outside this MVP.

## Submission documents

- `docs/FINAL_SUBMISSION.md` — abstract, architecture, reproducibility, evaluation boundary, and limitations.
- `docs/VIVA_QUESTIONS.md` — viva questions with concise answers.
- `evaluation/REPORT.md` — synthetic development-set evaluation.
- `evaluation/holdout/REPORT.md` — independent synthetic holdout.
- `evaluation/real_world/REPORT.md` — separate five-form robustness check.

Inference is local and uses the isolated `.venv`. No cloud API, browser extension, database, Docker, Node.js, local LLM, training dataset, or fine-tuning is required.
