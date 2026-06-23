---
name: print-studio-prepress-qc
description: "Use for final prepress review of Print Studio OpenDesign outputs: bleed, trim, safe area, margins, text readability, date accuracy, contrast, material risk, output completeness, package zip, and whether files are suitable for review preview, sample proof, or print-shop production handoff."
---

# Print Studio Prepress QC

## Goal

Decide whether a proof is ready for review, sample proofing, or production handoff.

## Workflow

1. Run the job from `../print-studio-runtime/` if outputs are missing:
   ```bash
   python scripts/run.py <config.json>
   ```
2. Read `output/<job>/qc_report.json`.
3. Inspect `screen/`, `print/`, and `commerce/` according to requested outputs.
4. Report status as one of:
   - proposal preview ready
   - sample proof ready
   - production handoff ready
   - blocked, needs revision

## Print Rules

- Print source should be more saturated and higher contrast than screen preview.
- Important content must stay inside safe margins.
- Bleed must exist when trim is expected.
- Date numbers and required text must remain readable.
- Pale pink, yellow, and light green require extra contrast checks.
- Decorative micro text, stamps, and thin lines must not fall below printable visibility.
- CMYK/ICC accuracy must not be promised unless a real ICC workflow is added.

## Handoff

When ready, confirm the delivery ZIP and summarize remaining physical proofing risks.

