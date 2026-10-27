"""Runnable local smoke test for the English FormLens MVP."""

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from formlens.pipeline import FormLensPipeline


SAMPLE = ROOT / "tests" / "fixtures" / "english_registration_form.png"
OUTPUT_DIR = ROOT / "outputs"
EXPECTED_LABELS = [
    "First Name",
    "Email Address",
    "Date of Birth",
    "I agree to receive event updates",
]


def main() -> None:
    if not SAMPLE.exists():
        raise FileNotFoundError("Create the sample first: .venv/bin/python tests/create_sample.py")

    pipeline = FormLensPipeline(ROOT / "models" / "ScreenParser" / "best.pt")
    annotated, fields = pipeline.analyze(SAMPLE.read_bytes())

    labels = [field.label for field in fields]
    if labels != EXPECTED_LABELS:
        raise AssertionError(f"Unexpected labels: {labels}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    Image.fromarray(annotated).save(OUTPUT_DIR / "english_registration_form_annotated.png")
    (OUTPUT_DIR / "english_registration_form_fields.json").write_text(
        json.dumps({"schema_version": "1.0", "fields": [field.to_dict() for field in fields]}, indent=2)
    )
    print(f"PASS: {len(fields)} controls and labels detected")


if __name__ == "__main__":
    main()
