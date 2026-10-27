# FormLens Real-World Robustness Check (separate from Phase 3 holdout)

Five publicly accessible blank government forms were downloaded and rendered locally. They were not part of the synthetic development or synthetic holdout sets. The existing frozen pipeline was run with the same configuration (`confidence=0.18`, `imgsz=1280`, detector IoU `0.30`, compact aspect filter `1.8`, matching acceptance `0.45`, uncertain below `0.70`). No rule, threshold, model, or dependency was changed after inspecting these forms.

Ground truth is a manual, representative annotation of controls visible on page 1, recorded in `ground_truth.json`; it is not an exhaustive annotation of all continuation pages. Detection matching uses same type and IoU >= 0.50.

## Aggregate results

| Metric | Result |
|---|---:|
| Forms | 5 |
| Manually annotated controls | 37 |
| Predicted controls | 88 |
| True positives | 35 |
| False positives | 53 |
| False negatives | 2 |
| Detection precision | 39.8% |
| Detection recall | 94.6% |
| Detection F1 | 56.0% |
| Label-association accuracy | 42.9% |
| Exact OCR label coverage | 51.4% |

## Per-form results

| Form image | GT | Predicted | TP | FP | FN | association errors |
|---|---:|---:|---:|---:|---:|---:|
| w4-1.png | 4 | 4 | 4 | 0 | 0 | 2 |
| i9-1.png | 9 | 19 | 9 | 10 | 0 | 5 |
| w9-1.png | 7 | 17 | 7 | 10 | 0 | 2 |
| f1040-1.png | 7 | 20 | 5 | 15 | 2 | 2 |
| i765-1.png | 10 | 28 | 10 | 18 | 0 | 9 |

## Failures and observations

[
  {
    "image": "w4-1.png",
    "kind": "association",
    "expected": "Head of household",
    "predicted": "]Head of household (Check only if you're unmarried and pay more than half the costs of keeping up a home for yourself and a qualifying individual.)",
    "status": "Matched"
  },
  {
    "image": "w4-1.png",
    "kind": "association",
    "expected": "Exempt from withholding",
    "predicted": "2026. See Exemption from withholding on page 2. I understand I will need to submit a new Form W-4 for 2027.",
    "status": "Matched"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "List B"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "List C"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "authorized by the Secretary of DHS, documentation from List A OR a combination of documentation from List B and List C. Enter any additional"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Section 2. Employer Review and Verification: Employers or their authorized representative must complete and sign Section 2 within three"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Document Number (if any)"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "AND"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Expiration Date (if any)"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Additional Information"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Middle Initial (if any)"
  },
  {
    "image": "i9-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "1Check here if you used an alternative procedure authorized by DHS to examine documents."
  },
  {
    "image": "i9-1.png",
    "kind": "association",
    "expected": "Date of Birth",
    "predicted": "Date of Birth (mm/dd/yyyy)",
    "status": "Matched"
  },
  {
    "image": "i9-1.png",
    "kind": "association",
    "expected": "A citizen of the United States",
    "predicted": "1. A citizen of the United States",
    "status": "Matched"
  },
  {
    "image": "i9-1.png",
    "kind": "association",
    "expected": "A noncitizen national of the United States",
    "predicted": "2. A noncitizen national of the United States (See Instructions.)",
    "status": "Matched"
  },
  {
    "image": "i9-1.png",
    "kind": "association",
    "expected": "A lawful permanent resident",
    "predicted": "3. A lawful permanent resident (Enter USCIS or A-Number.)",
    "status": "Matched"
  },
  {
    "image": "i9-1.png",
    "kind": "association",
    "expected": "An alien authorized to work until",
    "predicted": "4. An alien authorized to work until",
    "status": "Matched"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Exempt payee code (if any)"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "outside the United States.)"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Enter your TIN in the appropriate box. The TIN provided must match the name given on line 1 to avoid"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Social security number"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "backup withholding. For individuals, this is generally your social security number (SSN). However, for a"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "resident alien, sole proprietor, or disregarded entity, see the instructions for Part I, later. For other"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Employer identification number"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "or"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "entities, it is your employer identification number (EIN). If you do not have a number, see How to get a"
  },
  {
    "image": "w9-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "Note: If the account is in more than one name, see the instructions for line 1. See also What Name and"
  },
  {
    "image": "w9-1.png",
    "kind": "association",
    "expected": "LLC",
    "predicted": "LLC. Enter the tax classification (C = C corporation, S = S corporation, P = Partnership)",
    "status": "Matched"
  },
  {
    "image": "w9-1.png",
    "kind": "association",
    "expected": "Other",
    "predicted": "Other (see instructions)",
    "status": "Matched"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Qualifying surviving spouse (QSS)"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Married filing separately (MFS). Enter spouse's SSN above"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "and full name here:"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "If treating a nonresident alien or dual-status alien spouse as a U.S. resident for the entire tax year, check the box and enter their"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "text_input",
    "label": "exchange, or otherwise dispose of a\u2019 digital asset (or a financial interest in a digital asset)? (See instructions.)"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Full-time"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Permanently"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Child tax"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Child tax"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Check if your filing status is MFS or HOH and you lived apart from your spouse for the last 6 months of 2025, or you are legally"
  },
  {
    "image": "f1040-1.png",
    "kind": "false_positive",
    "type": "checkbox",
    "label": "Line 3b"
  }
]

OCR misses: [
  {
    "image": "w4-1.png",
    "label": "Head of household"
  },
  {
    "image": "w4-1.png",
    "label": "Exempt from withholding"
  },
  {
    "image": "i9-1.png",
    "label": "Date of Birth"
  },
  {
    "image": "i9-1.png",
    "label": "A citizen of the United States"
  },
  {
    "image": "i9-1.png",
    "label": "A noncitizen national of the United States"
  },
  {
    "image": "i9-1.png",
    "label": "A lawful permanent resident"
  },
  {
    "image": "i9-1.png",
    "label": "An alien authorized to work until"
  },
  {
    "image": "w9-1.png",
    "label": "LLC"
  },
  {
    "image": "w9-1.png",
    "label": "Other"
  },
  {
    "image": "f1040-1.png",
    "label": "Married filing jointly"
  },
  {
    "image": "f1040-1.png",
    "label": "Head of household"
  },
  {
    "image": "i765-1.png",
    "label": "Authorization/Extension Valid From"
  },
  {
    "image": "i765-1.png",
    "label": "Authorization/Extension Valid Through"
  },
  {
    "image": "i765-1.png",
    "label": "Select this box if Form G-28 is attached"
  },
  {
    "image": "i765-1.png",
    "label": "Replacement of lost, stolen, or damaged employment authorization document"
  },
  {
    "image": "i765-1.png",
    "label": "Family Name"
  },
  {
    "image": "i765-1.png",
    "label": "Middle Name"
  },
  {
    "image": "i765-1.png",
    "label": "Family Name"
  }
]

The detector was strongest on compact checkbox rows and clean text-entry rectangles. It produced extra or geometrically oversized text-input detections on dense tables and barcode/administrative regions (especially I-9, W-9, and I-765). Labels were often technically read by OCR, but nearby instructional prose was sometimes associated with a control; this is a matching limitation, not an OCR coverage claim.

## Environmental limitations

- The forms are official PDFs rendered with the local `pdftoppm` utility at 150 DPI; no cloud conversion or hosted inference was used.
- Two additional public sources (passport DS-11 and SSA SS-5) were not used because their servers returned HTTP 403 to the local downloader; they were replaced with directly downloadable official IRS/USCIS forms.
- The ScreenParser checkpoint is trained for screenshot-like UI controls, not paper tax/immigration forms. These results therefore measure out-of-domain robustness, not production accuracy.
- Only page 1 of each multi-page form was annotated; continuation pages, handwriting, filled forms, and accessibility form-field metadata were not evaluated.
- The experiment is intentionally separate from the formal synthetic holdout and must not be combined with its metrics.

## Sources

- w4-1.png: https://www.irs.gov/pub/irs-pdf/fw4.pdf
- i9-1.png: https://www.uscis.gov/sites/default/files/document/forms/i-9.pdf
- w9-1.png: https://www.irs.gov/pub/irs-pdf/fw9.pdf
- f1040-1.png: https://www.irs.gov/pub/irs-pdf/f1040.pdf
- i765-1.png: https://www.uscis.gov/sites/default/files/document/forms/i-765.pdf
