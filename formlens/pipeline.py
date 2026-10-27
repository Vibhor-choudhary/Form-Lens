"""Local visual field detection, OCR, association, and rendering."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from rapidocr import RapidOCR
from ultralytics import YOLO


CONTROL_TYPES = {
    "Text Input": "text_input",
    "Search Field": "search_input",
    "Search Bar": "search_input",
    "Checkbox": "checkbox",
    "Radiobox": "radio",
    "Select": "select",
    "Date-Time picker": "date_time",
    "Picker": "picker",
    "Switch": "switch",
    "Toggles": "toggle",
}


@dataclass
class Box:
    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


@dataclass
class OcrText:
    text: str
    confidence: float
    box: Box


@dataclass
class DetectedField:
    id: str
    control_type: str
    detector_class: str
    bounding_box: Box
    detector_confidence: float
    label: str | None
    label_box: Box | None
    ocr_confidence: float | None
    match_confidence: float
    confidence: float

    @property
    def match_status(self) -> str:
        if self.label is None:
            return "Unmatched"
        if self.match_confidence < 0.70:
            return "Uncertain"
        return "Matched"

    @property
    def review_required(self) -> bool:
        return self.match_status != "Matched" or self.detector_confidence < 0.40

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["bounding_box"] = asdict(self.bounding_box)
        result["label_box"] = asdict(self.label_box) if self.label_box else None
        result["match_status"] = self.match_status
        result["review_required"] = self.review_required
        return result


class FormLensPipeline:
    """The local-only MVP pipeline; no browser or network calls during inference."""

    def __init__(self, model_path: str | Path) -> None:
        self.detector = YOLO(str(model_path))
        self.ocr = RapidOCR()

    def analyze(self, image_bytes: bytes, confidence: float = 0.20) -> tuple[np.ndarray, list[DetectedField]]:
        annotated, fields, _, _ = self.analyze_detailed(image_bytes, confidence)
        return annotated, fields

    def analyze_detailed(
        self, image_bytes: bytes, confidence: float = 0.20, selected_id: str | None = None
    ) -> tuple[np.ndarray, list[DetectedField], list[OcrText], np.ndarray]:
        image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")

        detections = self._detect_controls(image, confidence)
        ocr_text = self._read_text(image)
        fields = self._associate(detections, ocr_text, image.shape[1], image.shape[0])
        return self._annotate(image, fields, ocr_text, selected_id), fields, ocr_text, cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def _detect_controls(self, image: np.ndarray, confidence: float) -> list[tuple[str, float, Box]]:
        results = self.detector.predict(image, imgsz=1280, conf=confidence, iou=0.30, verbose=False)
        controls: list[tuple[str, float, Box]] = []
        for result in results:
            for xyxy, cls_id, score in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                detector_class = self.detector.names[int(cls_id)]
                if detector_class not in CONTROL_TYPES:
                    continue
                x1, y1, x2, y2 = [int(round(value)) for value in xyxy.tolist()]
                width, height = max(1, x2 - x1), max(1, y2 - y1)
                # ScreenParser occasionally proposes text lines as very shallow inputs or
                # wide checkbox regions. These geometry checks keep the inventory focused
                # on actual control-shaped detections without using OCR-only heuristics.
                if detector_class in {"Text Input", "Search Field", "Search Bar"} and width / height > 20:
                    continue
                if detector_class in {"Checkbox", "Radiobox"} and (width / height > 1.8 or height / width > 1.8):
                    continue
                controls.append(
                    (
                        detector_class,
                        float(score),
                        Box(x=max(0, x1), y=max(0, y1), width=width, height=height),
                    )
                )
        return sorted(controls, key=lambda item: (item[2].y, item[2].x))

    def _read_text(self, image: np.ndarray) -> list[OcrText]:
        output = self.ocr(image)
        if output.boxes is None or output.txts is None or output.scores is None:
            return []

        entries: list[OcrText] = []
        for polygon, text, score in zip(output.boxes, output.txts, output.scores):
            clean_text = text.strip()
            if not clean_text:
                continue
            points = np.asarray(polygon, dtype=float)
            x1, y1 = np.min(points, axis=0)
            x2, y2 = np.max(points, axis=0)
            entries.append(
                OcrText(
                    text=clean_text,
                    confidence=float(score),
                    box=Box(int(x1), int(y1), max(1, int(x2 - x1)), max(1, int(y2 - y1))),
                )
            )
        return entries

    @staticmethod
    def _type_bonus(control_type: str, label: str) -> float:
        label = label.lower()
        if control_type == "date_time" and any(word in label for word in ("date", "birth", "dob", "day")):
            return 0.10
        if control_type == "checkbox" and any(word in label for word in ("agree", "consent", "subscribe", "terms")):
            return 0.08
        if control_type == "select" and any(word in label for word in ("country", "state", "select", "choose")):
            return 0.08
        return 0.0

    def _label_score(self, label: OcrText, control: Box, control_type: str, image_width: int) -> float:
        box = label.box
        horizontal_overlap = max(0, min(box.x2, control.x2) - max(box.x, control.x)) / max(1, min(box.width, control.width))
        vertical_overlap = max(0, min(box.y2, control.y2) - max(box.y, control.y)) / max(1, min(box.height, control.height))

        above_gap = control.y - box.y2
        left_gap = control.x - box.x2
        right_gap = box.x - control.x2
        above = 0.0
        left = 0.0
        if control_type in {"checkbox", "radio", "switch", "toggle"}:
            # For compact controls, the text immediately to the right is the
            # label. Section headings above a group must not consume the match.
            above_gap = 10**9
        if -8 <= above_gap <= max(110, control.height * 3):
            above = 0.45 + 0.35 * min(1.0, horizontal_overlap) + 0.20 * max(0.0, 1 - above_gap / 110)
        if -8 <= left_gap <= max(280, image_width * 0.28):
            center_alignment = max(0.0, 1 - abs(box.center_y - control.center_y) / max(40, control.height * 2))
            left = 0.40 + 0.35 * center_alignment + 0.25 * max(0.0, 1 - left_gap / max(280, image_width * 0.28))

        right = 0.0
        if control_type in {"checkbox", "radio", "switch", "toggle"} and -8 <= right_gap <= max(360, image_width * 0.35):
            center_alignment = max(0.0, 1 - abs(box.center_y - control.center_y) / max(40, control.height * 2))
            right = 0.45 + 0.35 * center_alignment + 0.20 * max(0.0, 1 - right_gap / max(360, image_width * 0.35))

        inside = 0.20 if vertical_overlap > 0.5 and horizontal_overlap > 0.5 else 0.0
        return min(1.0, max(above, left, right, inside) + self._type_bonus(control_type, label.text))

    def _associate(
        self,
        detections: list[tuple[str, float, Box]],
        labels: list[OcrText],
        image_width: int,
        image_height: int,
    ) -> list[DetectedField]:
        fields: list[DetectedField] = []
        used_labels: set[int] = set()
        for index, (detector_class, detector_confidence, box) in enumerate(detections, start=1):
            control_type = CONTROL_TYPES[detector_class]
            candidates = [
                (self._label_score(label, box, control_type, image_width), candidate_index, label)
                for candidate_index, label in enumerate(labels)
                if candidate_index not in used_labels
            ]
            candidates.sort(key=lambda item: item[0], reverse=True)
            score, label_index, label = candidates[0] if candidates else (0.0, -1, None)
            if score < 0.45:
                score, label = 0.0, None
            else:
                used_labels.add(label_index)

            ocr_confidence = label.confidence if label else None
            combined = detector_confidence * (0.60 + 0.40 * score)
            if ocr_confidence is not None:
                combined = 0.55 * detector_confidence + 0.25 * ocr_confidence + 0.20 * score
            fields.append(
                DetectedField(
                    id=f"field_{index:02d}",
                    control_type=control_type,
                    detector_class=detector_class,
                    bounding_box=box,
                    detector_confidence=round(detector_confidence, 3),
                    label=label.text if label else None,
                    label_box=label.box if label else None,
                    ocr_confidence=round(ocr_confidence, 3) if ocr_confidence is not None else None,
                    match_confidence=round(score, 3),
                    confidence=round(min(1.0, combined), 3),
                )
            )
        return fields

    @staticmethod
    def _annotate(image: np.ndarray, fields: list[DetectedField], ocr_text: list[OcrText], selected_id: str | None = None) -> np.ndarray:
        annotated = image.copy()
        for text in ocr_text:
            box = text.box
            for x in range(box.x, box.x2, 8):
                cv2.line(annotated, (x, box.y), (min(x + 4, box.x2), box.y), (220, 170, 20), 1)
                cv2.line(annotated, (x, box.y2), (min(x + 4, box.x2), box.y2), (220, 170, 20), 1)
        for field in fields:
            box = field.bounding_box
            color = (255, 0, 170) if field.id == selected_id else ((0, 140, 255) if field.match_status == "Unmatched" else ((0, 190, 220) if field.match_status == "Uncertain" else (45, 160, 70)))
            thickness = 3 if field.id == selected_id else 2
            cv2.rectangle(annotated, (box.x, box.y), (box.x2, box.y2), color, thickness)
            chip_y = max(0, box.y - 20)
            cv2.rectangle(annotated, (box.x, chip_y), (box.x + 34, min(box.y, chip_y + 20)), color, -1)
            cv2.putText(annotated, field.id.replace("field_", "#"), (box.x + 4, max(14, box.y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
            if field.label_box:
                label = field.label_box
                cv2.line(annotated, (int(label.center_x), int(label.center_y)), (int(box.center_x), int(box.center_y)), color, 1, cv2.LINE_AA)
        return cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
