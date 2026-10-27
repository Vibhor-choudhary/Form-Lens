# FormLens

FormLens is a simple tool that looks at a picture of a blank form and finds the fields on it.

It can find text boxes, checkboxes, radio buttons, select fields, and nearby labels.

## Try the live demo

[Open FormLens](https://form-lens-hgjz9cdsynkxf9ogf2xdow.streamlit.app/)

Upload a blank form screenshot and FormLens will show the marked-up form, a list of detected fields, confidence information, and a downloadable JSON file.

## Why it was built

Forms are easy for people to understand but difficult for software to read from an image. FormLens turns a form screenshot into structured information that other software can use later.

## How it works

1. A pretrained detector finds the visual controls.
2. OCR reads the words on the form.
3. A matching step connects controls with nearby labels.

The project uses existing pretrained tools. It was not trained from scratch.

## Run it on your computer

```bash
cd /Users/vibhor/Downloads/MLP
source .venv/bin/activate
streamlit run app.py
```

Then open the local address shown in the terminal and upload a PNG, JPG, or WebP image.

## Privacy

The local version processes images on your computer. The live demo processes images on its hosted Streamlit server, so avoid uploading private or sensitive forms there.

## Project files

- `app.py` — the Streamlit interface.
- `formlens/pipeline.py` — detection, OCR, and label matching.
- `models/ScreenParser/best.pt` — the pretrained detector.
- `evaluation/` — test results and reports.
- `docs/VIVA_QUESTIONS.md` — project presentation questions and answers.

## Current limitations

FormLens works best with clear, digital-looking forms. Dense scanned forms, handwriting, long instructions, and unusual layouts may produce extra detections or require human review.
