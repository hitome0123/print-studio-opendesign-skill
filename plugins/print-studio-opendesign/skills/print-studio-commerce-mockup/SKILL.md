---
name: print-studio-commerce-mockup
description: "Use to create or review user-facing commerce display images for Print Studio OpenDesign jobs: white-background product shots, ambiance/lifestyle shots, material preview images, and sales confirmation visuals. Keeps commerce mockups separate from print source files."
---

# Print Studio Commerce Mockup

## Goal

Produce presentation images for sales, confirmation, and ecommerce display.

## Workflow

1. Confirm the print proof exists and the product form is correct.
2. Ensure `outputs.types` includes `commerce`, `whitebg`, or `ambiance`.
3. Run from `../print-studio-runtime/`:
   ```bash
   python scripts/run.py <config.json>
   ```
4. Review `output/<job>/commerce/`.

## Mockup Rules

- White-background images can be brighter and cleaner than print source files.
- Ambiance images may include props and light, but must not change the product design.
- Do not use commerce mockups as production print files.
- If AI changes size, shape, paper edge, date text, or artwork, tighten prompts or rerun.
- Show both white-background and ambiance views when presentation material is needed.

## Handoff

Use `print-studio-prepress-qc` for final production checks.

