"""Professional Streamlit interface for the local FormLens analyzer."""

from __future__ import annotations

import io
import json
from pathlib import Path

import streamlit as st
from PIL import Image

from formlens.pipeline import FormLensPipeline

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "models" / "ScreenParser" / "best.pt"


@st.cache_resource(show_spinner="Loading local ScreenParser and OCR models…")
def load_pipeline() -> FormLensPipeline:
    return FormLensPipeline(MODEL_PATH)


def png_bytes(image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


st.set_page_config(page_title="FormLens · Local Form Analysis", page_icon="⌁", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    .block-container { max-width: 1420px; padding-top: 4.5rem; padding-bottom: 3rem; }
    .fl-header { display:flex; align-items:flex-start; justify-content:space-between; gap:2rem; margin-bottom:1.75rem; min-height:3.8rem; }
    .fl-brand { font-size:1.7rem; line-height:1.25; font-weight:700; letter-spacing:-.03em; color:#13233a; }
    .fl-brand span { color:#2f6fed; }
    .fl-subtitle { color:#66758a; font-size:.9rem; line-height:1.35; margin-top:.35rem; }
    .metric { border:1px solid #e1e8f0; border-radius:10px; padding:.75rem 1rem; background:#fff; }
    .metric-label { color:#718096; font-size:.78rem; }
    .metric-value { color:#172b4d; font-size:1.55rem; font-weight:700; }
    .legend { color:#64748b; font-size:.82rem; margin:.35rem 0 .8rem; }
    </style>
    <div class="fl-header">
      <div><div class="fl-brand">Form<span>Lens</span></div><div class="fl-subtitle">Local screenshot analysis for form controls and labels</div></div>
      <div class="fl-subtitle">On-device · ScreenParser + RapidOCR · No upload</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("**Analyze a form screenshot**")
    st.caption("Upload a blank form. Processing stays on this Mac; the detector threshold controls which predictions are retained.")
    uploaded = st.file_uploader("Choose a PNG, JPG, JPEG, or WebP image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
    if uploaded:
        image = Image.open(io.BytesIO(uploaded.getvalue()))
        st.caption(f"{uploaded.name} · {image.width} × {image.height}px · {uploaded.size / 1024:.0f} KB")

with st.expander("Settings", expanded=False):
    threshold = st.slider("Detector confidence threshold", 0.10, 0.70, 0.20, 0.05, help="Higher values retain fewer, more confident ScreenParser detections.")
    show_annotations = st.toggle("Show annotations", value=True)

if not uploaded:
    st.info("Upload a screenshot above to see the annotated image and field inventory.")
    st.stop()

pipeline = load_pipeline()
with st.spinner("Detecting controls, reading labels, and associating fields…"):
    _, initial_fields, _, _ = pipeline.analyze_detailed(uploaded.getvalue(), threshold)

field_options = ["None"] + [f"{f.id} · {f.label or 'Unmatched'}" for f in initial_fields]
selected_option = st.selectbox("Highlight a field", field_options)
selected_id = None if selected_option == "None" else selected_option.split(" · ", 1)[0]
annotated, fields, ocr_text, original = pipeline.analyze_detailed(uploaded.getvalue(), threshold, selected_id)

matched = sum(f.match_status == "Matched" for f in fields)
unmatched = sum(f.match_status == "Unmatched" for f in fields)
uncertain = sum(f.match_status == "Uncertain" for f in fields)
review = sum(f.review_required for f in fields)
st.markdown("### Analysis summary")
metrics = st.columns(4)
for column, label, value in zip(metrics, ("Detected controls", "Matched labels", "Unmatched", "Review required"), (len(fields), matched, unmatched, review)):
    column.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
st.caption(f"Matched: {matched} · Unmatched: {unmatched} · Uncertain associations: {uncertain} · Review required includes uncertain matches and low detector confidence.")

st.markdown("### Results")
left, right = st.columns([1.25, 1], gap="large")
with left:
    st.markdown("**Screenshot**")
    st.markdown('<div class="legend">Green = matched · Amber = uncertain/unmatched · Cyan dashed = OCR text · Magenta = selected</div>', unsafe_allow_html=True)
    st.image(annotated if show_annotations else original, use_container_width=True)
    st.download_button("Download annotated PNG", png_bytes(Image.fromarray(annotated)), "formlens_annotated.png", "image/png")
with right:
    st.markdown("**Field inventory**")
    all_types = sorted({f.control_type for f in fields})
    type_filter = st.multiselect("Control type", all_types, default=all_types)
    status_filter = st.multiselect("Match status", ["Matched", "Uncertain", "Unmatched"], default=["Matched", "Uncertain", "Unmatched"])
    visible = [f for f in fields if f.control_type in type_filter and f.match_status in status_filter]
    rows = [{"Field ID": f.id, "Detected label": f.label or "—", "Control type": f.control_type, "Detector confidence": f"{f.detector_confidence:.0%}", "OCR confidence": f"{f.ocr_confidence:.0%}" if f.ocr_confidence is not None else "—", "Match status": f.match_status, "Review required": "Yes" if f.review_required else "No"} for f in visible]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    payload = {"schema_version": "1.1", "image": {"filename": uploaded.name, "width": original.shape[1], "height": original.shape[0]}, "ocr_regions": [{"text": t.text, "confidence": round(t.confidence, 3), "box": {"x": t.box.x, "y": t.box.y, "width": t.box.width, "height": t.box.height}} for t in ocr_text], "fields": [f.to_dict() for f in fields]}
    st.download_button("Download complete JSON", json.dumps(payload, indent=2), "formlens_fields.json", "application/json")

with st.expander("Technical details", expanded=False):
    st.caption("Raw coordinates, OCR regions, detector metadata, and complete confidence values.")
    st.json(payload)
