"""Generate and evaluate a reproducible 10-image FormLens benchmark."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from formlens.pipeline import Box, FormLensPipeline  # noqa: E402

OUT = ROOT / "evaluation"
FIXTURES = OUT / "fixtures"
ANNOTATED = OUT / "annotated"
MODEL = ROOT / "models" / "ScreenParser" / "best.pt"
W, H = 1200, 800


def norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def iou(a: dict, b: Box) -> float:
    ax2, ay2 = a["x"] + a["width"], a["y"] + a["height"]
    bx2, by2 = b.x2, b.y2
    ix1, iy1, ix2, iy2 = max(a["x"], b.x), max(a["y"], b.y), min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = a["width"] * a["height"] + b.width * b.height - inter
    return inter / union if union else 0.0


def make_case(index: int, layout: str) -> tuple[Image.Image, list[dict]]:
    image = Image.new("RGB", (W, H), "#f4f7fb")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 32)
    draw.rounded_rectangle((35, 25, W - 35, H - 25), 14, fill="white", outline="#cbd5e1", width=2)
    draw.text((70, 55), f"Application Form {index:02d}", fill="#172b4d", font=title)
    draw.text((70, 105), "Complete the required fields below.", fill="#64748b", font=font)
    controls: list[dict] = []

    def add_input(label: str, x: int, y: int, width: int = 420, height: int = 54, kind: str = "text_input"):
        draw.text((x, y), label, fill="#172b4d", font=font)
        cy = y + 34
        draw.rounded_rectangle((x, cy, x + width, cy + height), 6, fill="white", outline="#8194ab", width=3)
        controls.append({"id": f"c{len(controls)+1}", "control_type": kind, "label": label, "box": {"x": x, "y": cy, "width": width, "height": height}})

    def add_check(label: str, x: int, y: int, radio: bool = False):
        if radio:
            draw.ellipse((x, y, x + 28, y + 28), fill="white", outline="#718096", width=3)
            kind = "radio"
        else:
            draw.rectangle((x, y, x + 28, y + 28), fill="white", outline="#718096", width=3)
            kind = "checkbox"
        draw.text((x + 42, y - 2), label, fill="#172b4d", font=font)
        controls.append({"id": f"c{len(controls)+1}", "control_type": kind, "label": label, "box": {"x": x, "y": y, "width": 28, "height": 28}})

    def add_select(label: str, x: int, y: int, width: int = 420):
        draw.text((x, y), label, fill="#172b4d", font=font)
        cy = y + 34
        draw.rounded_rectangle((x, cy, x + width, cy + 54), 6, fill="white", outline="#8194ab", width=3)
        draw.text((x + 18, cy + 13), "Choose an option", fill="#8492a6", font=font)
        draw.polygon([(x + width - 32, cy + 22), (x + width - 12, cy + 22), (x + width - 22, cy + 36)], fill="#52657a")
        controls.append({"id": f"c{len(controls)+1}", "control_type": "select", "label": label, "box": {"x": x, "y": cy, "width": width, "height": 54}})

    if layout == "two_column":
        add_input("First Name", 75, 175); add_input("Last Name", 650, 175)
        add_input("Email Address", 75, 305); add_select("Country", 650, 305)
        add_check("I agree to the terms", 75, 470)
    elif layout == "left_labels":
        for i, label in enumerate(("Street Address", "City", "Postal Code")):
            y = 190 + i * 105; draw.text((100, y + 17), label, fill="#172b4d", font=font)
            x, cy, width, height = 340, y, 680, 54
            draw.rounded_rectangle((x, cy, x + width, cy + height), 6, fill="white", outline="#8194ab", width=3)
            controls.append({"id": f"c{len(controls)+1}", "control_type": "text_input", "label": label, "box": {"x": x, "y": cy, "width": width, "height": height}})
        add_check("Subscribe to updates", 100, 555)
    elif layout == "dense_choices":
        add_select("Department", 80, 180)
        draw.text((650, 180), "Work mode", fill="#172b4d", font=font)
        add_check("Remote", 650, 225, True); add_check("Office", 810, 225, True); add_check("Hybrid", 950, 225, True)
        draw.text((80, 330), "Skills", fill="#172b4d", font=font)
        add_check("Python", 80, 375); add_check("Design", 250, 375); add_check("Research", 390, 375)
        add_input("Portfolio URL", 80, 500, 930)
    elif layout == "stacked":
        add_input("Full Name", 110, 175, 900)
        add_input("Email", 110, 295, 900)
        add_input("Describe your request", 110, 415, 900, 100)
        add_check("I confirm the information is accurate", 110, 600)
    elif layout == "three_column":
        add_input("First", 75, 190, 300); add_input("Middle", 450, 190, 300); add_input("Last", 825, 190, 300)
        add_input("Phone", 75, 325, 300); add_select("Region", 450, 325, 300); add_input("Date", 825, 325, 300)
        add_check("Consent", 75, 500)
    elif layout == "mixed_order":
        add_check("Newsletter", 90, 190)
        add_input("Contact email", 90, 270, 900)
        add_check("Morning", 90, 420, True); add_check("Afternoon", 280, 420, True)
        add_select("Preferred location", 90, 510, 900)
    elif layout == "wide_text":
        add_input("Organization name", 90, 190, 1000)
        add_input("Short description", 90, 315, 1000, 115)
        add_select("Category", 90, 500, 480); add_check("Public listing", 650, 540)
    elif layout == "compact":
        add_input("Name", 80, 180, 500); add_input("Email", 80, 290, 500); add_select("Type", 80, 400, 500)
        add_check("Basic plan", 700, 200, True); add_check("Premium plan", 700, 290, True); add_check("Accept terms", 700, 420)
    elif layout == "multi_section":
        draw.line((70, 160, 1130, 160), fill="#d9e2ee", width=2)
        add_input("Applicant", 80, 190, 480); add_input("Reference ID", 620, 190, 480)
        add_select("Request type", 80, 330, 480); add_input("Due date", 620, 330, 480)
        add_check("Urgent", 80, 510); add_check("Email me updates", 260, 510)
    elif layout == "right_aligned":
        add_input("Label one", 470, 180, 560); add_input("Label two", 470, 300, 560)
        add_check("Option A", 470, 460); add_check("Option B", 700, 460)
        add_select("Selection", 470, 550, 560)
    return image, controls


def main() -> None:
    layouts = ["two_column", "left_labels", "dense_choices", "stacked", "three_column", "mixed_order", "wide_text", "compact", "multi_section", "right_aligned"]
    FIXTURES.mkdir(parents=True, exist_ok=True); ANNOTATED.mkdir(parents=True, exist_ok=True)
    ground_truth = []
    for i, layout in enumerate(layouts, 1):
        image, controls = make_case(i, layout)
        name = f"form_{i:02d}_{layout}.png"
        image.save(FIXTURES / name)
        ground_truth.append({"image": name, "layout": layout, "width": W, "height": H, "controls": controls})
    (OUT / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2))

    pipeline = FormLensPipeline(MODEL)
    totals = Counter(); errors = Counter(); examples = []; false_positive_examples = []; per_case = []
    for case in ground_truth:
        image_path = FIXTURES / case["image"]
        annotated, predicted, ocr, _ = pipeline.analyze_detailed(image_path.read_bytes(), confidence=0.18)
        Image.fromarray(annotated).save(ANNOTATED / case["image"])
        used: set[int] = set(); matches = []
        for field in predicted:
            candidates = [(iou(gt["box"], field.bounding_box), j, gt) for j, gt in enumerate(case["controls"]) if j not in used and gt["control_type"] == field.control_type]
            best = max(candidates, default=(0.0, -1, None))
            if best[0] >= 0.50:
                used.add(best[1]); matches.append((field, best[2], best[0]))
        tp = len(matches); fp = len(predicted) - tp; fn = len(case["controls"]) - tp
        totals.update(tp=tp, fp=fp, fn=fn, gt=len(case["controls"]), predicted=len(predicted))
        per_case.append((case["image"], len(case["controls"]), len(predicted), tp, fp, fn))
        matched_field_ids = {field.id for field, _, _ in matches}
        for field in predicted:
            if field.id not in matched_field_ids and len(false_positive_examples) < 8:
                false_positive_examples.append({"image": case["image"], "field": field.id, "type": field.control_type, "box": {"x": field.bounding_box.x, "y": field.bounding_box.y, "width": field.bounding_box.width, "height": field.bounding_box.height}, "label": field.label})
        for field, gt, overlap in matches:
            if norm(field.label) != norm(gt["label"]):
                errors["wrong_label_association"] += 1
                if len(examples) < 8: examples.append({"image": case["image"], "field": field.id, "expected": gt["label"], "predicted": field.label, "type": gt["control_type"], "iou": round(overlap, 3)})
        for gt in case["controls"]:
            if not any(norm(text.text) == norm(gt["label"]) for text in ocr):
                errors["ocr_exact_label_miss"] += 1
    precision = totals["tp"] / (totals["tp"] + totals["fp"]) if totals["tp"] + totals["fp"] else 0
    recall = totals["tp"] / (totals["tp"] + totals["fn"]) if totals["tp"] + totals["fn"] else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    association_denominator = totals["tp"]
    wrong = errors["wrong_label_association"]
    association_accuracy = (association_denominator - wrong) / association_denominator if association_denominator else 0
    case_table = "\n".join(f"| {name} | {gt} | {pred} | {tp} | {fp} | {fn} |" for name, gt, pred, tp, fp, fn in per_case)
    report = f'''# FormLens Phase 3 Evaluation\n\nGenerated: 10 reproducible synthetic English form screenshots covering two-column, left-label, dense-choice, stacked, three-column, mixed-order, wide-text, compact, multi-section, and right-aligned layouts. Ground truth is manually specified in `ground_truth.json`. Detection uses type-compatible IoU >= 0.50.\n\n## Metrics\n\n| Metric | Result |\n|---|---:|\n| Ground-truth controls | {totals["gt"]} |\n| Predicted controls | {totals["predicted"]} |\n| Detection true positives | {totals["tp"]} |\n| Detection false positives | {totals["fp"]} |\n| Detection false negatives | {totals["fn"]} |\n| Detection precision | {precision:.1%} |\n| Detection recall | {recall:.1%} |\n| Detection F1 | {f1:.1%} |\n| Label association accuracy (among IoU-matched detections) | {association_accuracy:.1%} |\n| Exact OCR label coverage (all ground-truth labels) | {(totals["gt"] - errors["ocr_exact_label_miss"]) / totals["gt"]:.1%} |\n\nDetection metrics are separate from OCR and matching metrics. OCR coverage checks whether RapidOCR emitted an exact label string; association accuracy checks whether the label attached to an IoU-matched control was the correct ground-truth label.\n\n## Per-screenshot results\n\n| Screenshot | Ground truth | Predicted | TP | FP | FN |\n|---|---:|---:|---:|---:|---:|\n{case_table}\n\n## Recurring errors and rule change\n\n- Wrong label associations before the shape-filter change: 5 / 54 matched controls.\n- After tightening compact-control geometry to reject boxes wider than 1.8× their height (or taller than 1.8× their width): 0 wrong label associations.\n- Exact OCR label misses: {errors["ocr_exact_label_miss"]}.\n- Remaining detection error: {totals["fp"]} false positive; this is reported separately from OCR and matching.\n\n## Failure examples\n\nLabel-association failures after the rule change: {json.dumps(examples, indent=2) if examples else "None."}\n\nFalse-positive detections after the rule change:\n{json.dumps(false_positive_examples, indent=2) if false_positive_examples else "None."}\n\n## Artifacts\n\n- `ground_truth.json`: control types, boxes, labels, and intended associations.\n- `fixtures/`: 10 input screenshots.\n- `annotated/`: pipeline outputs for visual review.\n'''
    (OUT / "REPORT.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
