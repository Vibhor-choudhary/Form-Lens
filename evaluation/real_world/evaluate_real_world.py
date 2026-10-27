"""Frozen real-world robustness check for five public blank forms.

This evaluator is intentionally separate from the synthetic development and
holdout evaluators.  The ground truth below was recorded manually from the
rendered first page of each public PDF; no pipeline rule was changed for this
experiment.
"""
from __future__ import annotations

import json, re, sys
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))
from formlens.pipeline import Box, FormLensPipeline  # noqa: E402

OUT = ROOT / "evaluation" / "real_world"
IMAGES = OUT / "images"
ANNOTATED = OUT / "outputs"
MODEL = ROOT / "models" / "ScreenParser" / "best.pt"

# Manually recorded representative controls on page 1. Coordinates are in the
# 1275x1650 PNG renders. This is a robustness sample, not a claim of exhaustive
# annotation of every continuation-page field.
CASES = [
    {"image":"w4-1.png", "source":"https://www.irs.gov/pub/irs-pdf/fw4.pdf", "controls":[
      {"id":"w4-c1","control_type":"checkbox","label":"Single or Married filing separately","box":{"x":238,"y":327,"width":20,"height":20}},
      {"id":"w4-c2","control_type":"checkbox","label":"Married filing jointly or Qualifying surviving spouse","box":{"x":238,"y":352,"width":20,"height":20}},
      {"id":"w4-c3","control_type":"checkbox","label":"Head of household","box":{"x":238,"y":376,"width":20,"height":20}},
      {"id":"w4-c4","control_type":"checkbox","label":"Exempt from withholding","box":{"x":1172,"y":1360,"width":22,"height":22}}
    ]},
    {"image":"i9-1.png", "source":"https://www.uscis.gov/sites/default/files/document/forms/i-9.pdf", "controls":[
      {"id":"i9-c1","control_type":"text_input","label":"Date of Birth","box":{"x":310,"y":445,"width":226,"height":25}},
      {"id":"i9-c2","control_type":"text_input","label":"U.S. Social Security Number","box":{"x":310,"y":469,"width":226,"height":29}},
      {"id":"i9-c3","control_type":"checkbox","label":"A citizen of the United States","box":{"x":378,"y":539,"width":21,"height":22}},
      {"id":"i9-c4","control_type":"checkbox","label":"A noncitizen national of the United States","box":{"x":378,"y":563,"width":21,"height":23}},
      {"id":"i9-c5","control_type":"checkbox","label":"A lawful permanent resident","box":{"x":378,"y":590,"width":21,"height":21}},
      {"id":"i9-c6","control_type":"checkbox","label":"An alien authorized to work until","box":{"x":378,"y":614,"width":21,"height":22}},
      {"id":"i9-c7","control_type":"text_input","label":"USCIS A-Number","box":{"x":575,"y":674,"width":225,"height":28}},
      {"id":"i9-c8","control_type":"text_input","label":"Form I-94 Admission Number","box":{"x":575,"y":700,"width":225,"height":26}},
      {"id":"i9-c9","control_type":"text_input","label":"Foreign Passport Number and Country of Issuance","box":{"x":825,"y":700,"width":375,"height":26}}
    ]},
    {"image":"w9-1.png", "source":"https://www.irs.gov/pub/irs-pdf/fw9.pdf", "controls":[
      {"id":"w9-c1","control_type":"checkbox","label":"Individual/sole proprietor","box":{"x":151,"y":374,"width":20,"height":20}},
      {"id":"w9-c2","control_type":"checkbox","label":"C corporation","box":{"x":373,"y":374,"width":20,"height":20}},
      {"id":"w9-c3","control_type":"checkbox","label":"S corporation","box":{"x":523,"y":374,"width":20,"height":20}},
      {"id":"w9-c4","control_type":"checkbox","label":"Partnership","box":{"x":673,"y":374,"width":20,"height":20}},
      {"id":"w9-c5","control_type":"checkbox","label":"Trust/estate","box":{"x":808,"y":374,"width":20,"height":20}},
      {"id":"w9-c6","control_type":"checkbox","label":"LLC","box":{"x":151,"y":402,"width":20,"height":20}},
      {"id":"w9-c7","control_type":"checkbox","label":"Other","box":{"x":151,"y":478,"width":20,"height":20}}
    ]},
    {"image":"f1040-1.png", "source":"https://www.irs.gov/pub/irs-pdf/f1040.pdf", "controls":[
      {"id":"1040-c1","control_type":"checkbox","label":"You","box":{"x":1003,"y":404,"width":21,"height":19}},
      {"id":"1040-c2","control_type":"checkbox","label":"Spouse","box":{"x":1093,"y":404,"width":21,"height":19}},
      {"id":"1040-c3","control_type":"checkbox","label":"Single","box":{"x":202,"y":428,"width":20,"height":19}},
      {"id":"1040-c4","control_type":"checkbox","label":"Married filing jointly","box":{"x":202,"y":452,"width":20,"height":20}},
      {"id":"1040-c5","control_type":"checkbox","label":"Head of household","box":{"x":727,"y":428,"width":20,"height":20}},
      {"id":"1040-c6","control_type":"checkbox","label":"Yes","box":{"x":1080,"y":619,"width":20,"height":20}},
      {"id":"1040-c7","control_type":"checkbox","label":"No","box":{"x":1153,"y":619,"width":20,"height":20}}
    ]},
    {"image":"i765-1.png", "source":"https://www.uscis.gov/sites/default/files/document/forms/i-765.pdf", "controls":[
      {"id":"i765-c1","control_type":"checkbox","label":"Authorization/Extension Valid From","box":{"x":155,"y":192,"width":22,"height":22}},
      {"id":"i765-c2","control_type":"checkbox","label":"Authorization/Extension Valid Through","box":{"x":155,"y":280,"width":22,"height":22}},
      {"id":"i765-c3","control_type":"checkbox","label":"Select this box if Form G-28 is attached","box":{"x":350,"y":526,"width":23,"height":23}},
      {"id":"i765-c4","control_type":"checkbox","label":"Initial permission to accept employment","box":{"x":126,"y":776,"width":23,"height":23}},
      {"id":"i765-c5","control_type":"checkbox","label":"Replacement of lost, stolen, or damaged employment authorization document","box":{"x":126,"y":813,"width":23,"height":23}},
      {"id":"i765-c6","control_type":"text_input","label":"Family Name","box":{"x":836,"y":848,"width":365,"height":41}},
      {"id":"i765-c7","control_type":"text_input","label":"Given Name","box":{"x":836,"y":898,"width":365,"height":41}},
      {"id":"i765-c8","control_type":"text_input","label":"Middle Name","box":{"x":836,"y":948,"width":365,"height":41}},
      {"id":"i765-c9","control_type":"text_input","label":"Family Name","box":{"x":248,"y":1336,"width":366,"height":41}},
      {"id":"i765-c10","control_type":"text_input","label":"Given Name","box":{"x":249,"y":1386,"width":365,"height":41}}
    ]}
]

def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
def iou(a, b):
    ax2, ay2 = a["x"] + a["width"], a["y"] + a["height"]
    ix1, iy1, ix2, iy2 = max(a["x"],b.x), max(a["y"],b.y), min(ax2,b.x2), min(ay2,b.y2)
    inter = max(0,ix2-ix1)*max(0,iy2-iy1); union = a["width"]*a["height"]+b.width*b.height-inter
    return inter/union if union else 0.0

def main():
    ANNOTATED.mkdir(exist_ok=True)
    (OUT / "ground_truth.json").write_text(json.dumps(CASES, indent=2))
    pipeline = FormLensPipeline(MODEL)
    totals = Counter(); rows=[]; failures=[]; ocr_misses=[]
    for case in CASES:
        annotated, predicted, ocr, _ = pipeline.analyze_detailed((IMAGES/case["image"]).read_bytes(), confidence=0.18)
        Image.fromarray(annotated).save(ANNOTATED / case["image"])
        used=set(); matches=[]
        for field in predicted:
            cands=[(iou(gt["box"],field.bounding_box),j,gt) for j,gt in enumerate(case["controls"]) if j not in used and gt["control_type"]==field.control_type]
            best=max(cands,default=(0,-1,None))
            if best[0]>=0.50: used.add(best[1]); matches.append((field,best[2],best[0]))
            else: failures.append({"image":case["image"],"kind":"false_positive","type":field.control_type,"label":field.label})
        tp,fp,fn=len(matches),len(predicted)-len(matches),len(case["controls"])-len(matches)
        totals.update(gt=len(case["controls"]),predicted=len(predicted),tp=tp,fp=fp,fn=fn)
        wrong=0
        for field,gt,overlap in matches:
            if norm(field.label)!=norm(gt["label"]):
                wrong+=1; failures.append({"image":case["image"],"kind":"association","expected":gt["label"],"predicted":field.label,"status":field.match_status})
        for gt in case["controls"]:
            if not any(norm(t.text)==norm(gt["label"]) for t in ocr): ocr_misses.append({"image":case["image"],"label":gt["label"]})
        rows.append((case["image"],len(case["controls"]),len(predicted),tp,fp,fn,wrong))
    p=totals["tp"]/(totals["tp"]+totals["fp"]) if totals["tp"]+totals["fp"] else 0
    r=totals["tp"]/(totals["tp"]+totals["fn"]) if totals["tp"]+totals["fn"] else 0
    f1=2*p*r/(p+r) if p+r else 0
    assoc=(totals["tp"]-sum(1 for x in failures if x["kind"]=="association"))/totals["tp"] if totals["tp"] else 0
    ocr=(totals["gt"]-len(ocr_misses))/totals["gt"] if totals["gt"] else 0
    table="\n".join(f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} |" for a,b,c,d,e,f,g in rows)
    report=f'''# FormLens Real-World Robustness Check (separate from Phase 3 holdout)\n\nFive publicly accessible blank government forms were downloaded and rendered locally. They were not part of the synthetic development or synthetic holdout sets. The existing frozen pipeline was run with the same configuration (`confidence=0.18`, `imgsz=1280`, detector IoU `0.30`, compact aspect filter `1.8`, matching acceptance `0.45`, uncertain below `0.70`). No rule, threshold, model, or dependency was changed after inspecting these forms.\n\nGround truth is a manual, representative annotation of controls visible on page 1, recorded in `ground_truth.json`; it is not an exhaustive annotation of all continuation pages. Detection matching uses same type and IoU >= 0.50.\n\n## Aggregate results\n\n| Metric | Result |\n|---|---:|\n| Forms | 5 |\n| Manually annotated controls | {totals["gt"]} |\n| Predicted controls | {totals["predicted"]} |\n| True positives | {totals["tp"]} |\n| False positives | {totals["fp"]} |\n| False negatives | {totals["fn"]} |\n| Detection precision | {p:.1%} |\n| Detection recall | {r:.1%} |\n| Detection F1 | {f1:.1%} |\n| Label-association accuracy | {assoc:.1%} |\n| Exact OCR label coverage | {ocr:.1%} |\n\n## Per-form results\n\n| Form image | GT | Predicted | TP | FP | FN | association errors |\n|---|---:|---:|---:|---:|---:|---:|\n{table}\n\n## Failures and observations\n\n{json.dumps(failures[:40], indent=2) if failures else "No recorded failures."}\n\nOCR misses: {json.dumps(ocr_misses, indent=2) if ocr_misses else "None."}\n\nThe detector was strongest on compact checkbox rows and clean text-entry rectangles. It produced extra or geometrically oversized text-input detections on dense tables and barcode/administrative regions (especially I-9, W-9, and I-765). Labels were often technically read by OCR, but nearby instructional prose was sometimes associated with a control; this is a matching limitation, not an OCR coverage claim.\n\n## Environmental limitations\n\n- The forms are official PDFs rendered with the local `pdftoppm` utility at 150 DPI; no cloud conversion or hosted inference was used.\n- Two additional public sources (passport DS-11 and SSA SS-5) were not used because their servers returned HTTP 403 to the local downloader; they were replaced with directly downloadable official IRS/USCIS forms.\n- The ScreenParser checkpoint is trained for screenshot-like UI controls, not paper tax/immigration forms. These results therefore measure out-of-domain robustness, not production accuracy.\n- Only page 1 of each multi-page form was annotated; continuation pages, handwriting, filled forms, and accessibility form-field metadata were not evaluated.\n- The experiment is intentionally separate from the formal synthetic holdout and must not be combined with its metrics.\n\n## Sources\n\n{chr(10).join('- '+c["image"]+': '+c["source"] for c in CASES)}\n'''
    (OUT / "REPORT.md").write_text(report)
    (OUT / "config.json").write_text(json.dumps({"set":"real_world_robustness_check","forms":5,"detector_confidence":0.18,"detector_imgsz":1280,"detector_iou":0.30,"compact_control_aspect_ratio_max":1.8,"association_acceptance_score":0.45,"association_uncertain_below":0.70,"detection_iou_match":0.50,"post_inspection_tuning":False},indent=2))
    print(report)
if __name__ == "__main__": main()
