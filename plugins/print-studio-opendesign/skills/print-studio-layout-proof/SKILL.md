---
name: print-studio-layout-proof
description: "Use to create constrained AI layout proofs for non-calendar print products in Print Studio OpenDesign: greeting cards, postcards, bookmarks, thank-you cards, invitations, packaging inserts, gift tags, card sets, and custom illustration series. Keeps AI layout choices inside deterministic print rules for size, bleed, safe margins, readable text, and material-aware color."
---

# Print Studio Layout Proof

## Goal

Create beautiful but controlled proofs for generic print products.

## Workflow

1. Confirm the config uses a non-date product or `series.template: generic_card`.
2. Put project images into the configured `assets.illustrations_dir`.
3. Use examples in `../print-studio-runtime/examples/` when starting:
   - `greeting-card-5x7.json`
   - `postcard-7x5-set.json`
   - `bookmark-2x6-set.json`
   - `gift-tag-custom.json`
4. Run from `../print-studio-runtime/`:
   ```bash
   python scripts/run.py <config.json>
   ```
5. Review `screen/`, `print/`, and `qc_report.json`.

## Layout Rules

- Do not place important text near trim edges.
- Keep small text readable after print.
- Increase print-version saturation and contrast, but keep backgrounds restrained.
- Use warm white / ivory backgrounds instead of dirty gray.
- Avoid pure black for soft illustration styles; prefer deep brown or warm dark gray.
- For pale pink, yellow, and light green, check contrast carefully.

## Handoff

Use `print-studio-commerce-mockup` for white-background and ambiance display images, then `print-studio-prepress-qc`.

