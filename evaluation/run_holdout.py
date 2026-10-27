"""Create and evaluate an untouched Phase 3.1 holdout set.

This script is intentionally separate from the development-set evaluator. Do not
change pipeline rules based on this output; make a new holdout if tuning resumes.
"""

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

OUT = ROOT / "evaluation" / "holdout"
FIXTURES = OUT / "fixtures"
ANNOTATED = OUT / "annotated"
MODEL = ROOT / "models" / "ScreenParser" / "best.pt"
W, H = 1280, 860


def norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def iou(a: dict, b: Box) -> float:
    ax2, ay2 = a["x"] + a["width"], a["y"] + a["height"]
    ix1, iy1 = max(a["x"], b.x), max(a["y"], b.y)
    ix2, iy2 = min(ax2, b.x2), min(ay2, b.y2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = a["width"] * a["height"] + b.width * b.height - inter
    return inter / union if union else 0.0


def render_case(index: int) -> tuple[Image.Image, list[dict]]:
    image = Image.new("RGB", (W, H), "#f6f8fb")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 21)
    title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 31)
    draw.rounded_rectangle((28, 22, W - 28, H - 22), 16, fill="white", outline="#c8d3e0", width=2)
    draw.text((68, 53), f"Independent Holdout Form {index:02d}", fill="#172b4d", font=title)
    draw.text((68, 103), "New screenshot reserved for final validation.", fill="#64748b", font=font)
    controls: list[dict] = []

    def input_field(label: str, x: int, y: int, width: int, height: int = 52, kind: str = "text_input"):
        draw.text((x, y), label, fill="#172b4d", font=font)
        cy = y + 31
        draw.rounded_rectangle((x, cy, x + width, cy + height), 6, fill="white", outline="#8296ad", width=3)
        controls.append({"id": f"c{len(controls)+1}", "control_type": kind, "label": label, "box": {"x": x, "y": cy, "width": width, "height": height}})

    def compact(label: str, x: int, y: int, radio: bool = False):
        if radio:
            draw.ellipse((x, y, x + 27, y + 27), fill="white", outline="#72859c", width=3); kind = "radio"
        else:
            draw.rectangle((x, y, x + 27, y + 27), fill="white", outline="#72859c", width=3); kind = "checkbox"
        draw.text((x + 39, y - 2), label, fill="#172b4d", font=font)
        controls.append({"id": f"c{len(controls)+1}", "control_type": kind, "label": label, "box": {"x": x, "y": y, "width": 27, "height": 27}})

    def select(label: str, x: int, y: int, width: int):
        input_field(label, x, y, width, 52, "select")
        cy = y + 31
        draw.text((x + 15, cy + 12), "Select one", fill="#8492a6", font=font)
        draw.polygon([(x + width - 34, cy + 20), (x + width - 14, cy + 20), (x + width - 24, cy + 34)], fill="#53677f")

    layout = index % 10
    if layout == 1:
        input_field("Applicant name", 80, 185, 500); input_field("Contact email", 680, 185, 500); select("Application type", 80, 335, 500); compact("I accept the policy", 680, 380)
    elif layout == 2:
        input_field("Building number", 370, 185, 760); input_field("Street name", 370, 295, 760); input_field("Town", 370, 405, 760); compact("Mailing address is current", 115, 565)
    elif layout == 3:
        select("Service category", 80, 190, 1060); compact("Email", 80, 355, True); compact("Phone", 250, 355, True); compact("Either", 420, 355, True); input_field("Notes", 80, 485, 1060, 100)
    elif layout == 4:
        input_field("Given name", 80, 190, 330); input_field("Family name", 475, 190, 330); input_field("Identifier", 870, 190, 330); compact("Verified", 80, 390); select("Status", 475, 360, 330); compact("Keep me informed", 870, 390)
    elif layout == 5:
        compact("Option alpha", 110, 205, True); compact("Option beta", 110, 285, True); compact("Option gamma", 110, 365, True); input_field("Response", 450, 205, 650); select("Priority", 450, 355, 650)
    elif layout == 6:
        input_field("Organization", 90, 190, 1000); input_field("Project title", 90, 310, 1000); input_field("Project summary", 90, 430, 1000, 120); compact("Publish summary", 90, 625)
    elif layout == 7:
        select("Language", 90, 185, 330); select("Timezone", 475, 185, 330); select("Format", 860, 185, 330); compact("I need assistance", 90, 365); compact("Send confirmation", 400, 365)
    elif layout == 8:
        input_field("Reference", 560, 180, 560); input_field("Description", 560, 300, 560, 110); compact("Urgent request", 560, 485); select("Department", 560, 560, 560)
    elif layout == 9:
        input_field("Email", 90, 195, 500); compact("Daily digest", 90, 330); compact("Weekly digest", 270, 330); select("Digest format", 90, 430, 500); compact("Agree", 90, 570)
    else:
        input_field("Name", 95, 190, 1090); select("Region", 95, 325, 520); input_field("Date", 665, 325, 520); compact("Terms accepted", 95, 485); compact("Contact me", 420, 485)
    return image, controls


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True); ANNOTATED.mkdir(parents=True, exist_ok=True)
    ground_truth = []
    for index in range(11, 21):
        image, controls = render_case(index)
        name = f"holdout_{index:02d}.png"
        image.save(FIXTURES / name)
        ground_truth.append({"image": name, "width": W, "height": H, "controls": controls})
    (OUT / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2))

    pipeline = FormLensPipeline(MODEL)
    totals = Counter(); association_wrong = []; ocr_misses = []; rows = []; false_positives = []
    for case in ground_truth:
        annotated, predicted, ocr, _ = pipeline.analyze_detailed((FIXTURES / case["image"]).read_bytes(), confidence=0.18)
        Image.fromarray(annotated).save(ANNOTATED / case["image"])
        used: set[int] = set(); matches = []
        for field in predicted:
            candidates = [(iou(gt["box"], field.bounding_box), j, gt) for j, gt in enumerate(case["controls"]) if j not in used and gt["control_type"] == field.control_type]
            best = max(candidates, default=(0.0, -1, None))
            if best[0] >= 0.50:
                used.add(best[1]); matches.append((field, best[2], best[0]))
            else:
                if len(false_positives) < 10: false_positives.append({"image": case["image"], "field": field.id, "type": field.control_type, "label": field.label})
        tp, fp, fn = len(matches), len(predicted) - len(matches), len(case["controls"]) - len(matches)
        totals.update(gt=len(case["controls"]), predicted=len(predicted), tp=tp, fp=fp, fn=fn)
        rows.append((case["image"], len(case["controls"]), len(predicted), tp, fp, fn))
        for field, gt, overlap in matches:
            if norm(field.label) != norm(gt["label"]):
                association_wrong.append({"image": case["image"], "field": field.id, "expected": gt["label"], "predicted": field.label, "iou": round(overlap, 3)})
        for gt in case["controls"]:
            if not any(norm(text.text) == norm(gt["label"]) for text in ocr): ocr_misses.append({"image": case["image"], "label": gt["label"]})
    precision = totals["tp"] / (totals["tp"] + totals["fp"]) if totals["tp"] + totals["fp"] else 0
    recall = totals["tp"] / (totals["tp"] + totals["fn"]) if totals["tp"] + totals["fn"] else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    assoc = (totals["tp"] - len(association_wrong)) / totals["tp"] if totals["tp"] else 0
    ocr = (totals["gt"] - len(ocr_misses)) / totals["gt"] if totals["gt"] else 0
    config = {"set": "phase3.1_holdout", "screenshots": 10, "detector_confidence": 0.18, "detector_imgsz": 1280, "detector_iou": 0.30, "compact_control_aspect_ratio_max": 1.8, "association_acceptance_score": 0.45, "association_uncertain_below": 0.70, "detection_iou_match": 0.50, "pipeline_commit_state": "working tree after Phase 3 development-set tuning; no holdout-driven changes"}
    (OUT / "config.json").write_text(json.dumps(config, indent=2))
    table = "\n".join(f"| {n} | {gt} | {p} | {tp} | {fp} | {fn} |" for n, gt, p, tp, fp, fn in rows)
    report = f'''# FormLens Phase 3.1 Independent Holdout Validation\n\nThis set was generated after the original 10-image evaluation was used for development tuning. It was not used to modify the pipeline, thresholds, or matching rules. No changes were made after inspecting these holdout results.\n\n## Frozen configuration\n\nSee `config.json`. Detection uses ScreenParser at confidence 0.18, `imgsz=1280`, NMS IoU 0.30, compact-control aspect ratio maximum 1.8, association acceptance score 0.45, uncertain association below 0.70, and evaluation IoU 0.50.\n\n## Metric definitions\n\n- Detection precision = TP / (TP + FP). TP requires a predicted control and ground-truth control with the same normalized type and IoU >= 0.50. Extra predictions are FP.\n- Detection recall = TP / (TP + FN). A ground-truth control without a matched prediction is FN.\n- Detection F1 = harmonic mean of precision and recall.\n- Label-association accuracy = correctly associated normalized label / IoU-matched detections. Unmatched or wrong labels count as incorrect; uncertain status does not receive credit unless the underlying label is correct.\n- Exact OCR label coverage = ground-truth labels emitted exactly by OCR after normalization / all ground-truth labels. Missing OCR text counts as a miss, independently of detector matching.\n\n## Holdout results\n\n| Metric | Result |\n|---|---:|\n| Ground-truth controls | {totals["gt"]} |\n| Predicted controls | {totals["predicted"]} |\n| True positives | {totals["tp"]} |\n| False positives | {totals["fp"]} |\n| False negatives | {totals["fn"]} |\n| Detection precision | {precision:.1%} |\n| Detection recall | {recall:.1%} |\n| Detection F1 | {f1:.1%} |\n| Label-association accuracy | {assoc:.1%} |\n| Exact OCR label coverage | {ocr:.1%} |\n\n## Per-screenshot results\n\n| Screenshot | Ground truth | Predicted | TP | FP | FN |\n|---|---:|---:|---:|---:|---:|\n{table}\n\n## Failures\n\nAssociation failures:\n{json.dumps(association_wrong, indent=2) if association_wrong else "None."}\n\nOCR misses:\n{json.dumps(ocr_misses, indent=2) if ocr_misses else "None."}\n\nFalse positives:\n{json.dumps(false_positives, indent=2) if false_positives else "None."}\n\n## Limitations\n\nThis is a synthetic holdout, not a sample of production web pages. It tests layout variation and reproducibility, but does not establish performance on scanned paper forms, native applications, handwriting, severe compression, or unseen languages. The original development-set results must not be presented as independent generalization results.\n'''
    (OUT / "REPORT.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
