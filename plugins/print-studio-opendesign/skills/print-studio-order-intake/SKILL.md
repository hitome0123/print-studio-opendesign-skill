---
name: print-studio-order-intake
description: "Use for print-shop order intake and configuration planning before rendering: clarify product type, series structure, size, paper/material, finishing, double-sided needs, output types, and create or update a Print Studio OpenDesign config JSON. Applies to greeting cards, postcards, calendars, bookmarks, gift tags, packaging inserts, card sets, seasonal sets, and custom N-card print jobs."
---

# Print Studio Order Intake

## Goal

Turn a print request into a runnable Print Studio OpenDesign config.

## Workflow

1. If images are available, run the image-first advisor before asking for choices:
   ```bash
   cd ../print-studio-runtime
   python scripts/advise_project.py <illustrations_dir>
   ```
2. Use the advisor report to explain product, size, material, layout, typography, model-preview, and print-check recommendations.
3. Identify the product type: card, postcard, desk calendar, wall calendar, bookmark, tag, insert, card set, or custom.
4. Identify the series: single, monthly, quarterly, seasonal, festival set, or custom `N` cards.
5. Select production specs: size, material, bleed, safe margin, double-sided, round corners, binding, finishing.
6. Select outputs: `screen`, `print`, `commerce`, `single`, `grid`, `whitebg`, `ambiance`, `back`, `download_4k`.
7. Copy `../print-studio-runtime/config.example.json` or an example from `../print-studio-runtime/examples/`.
8. Save a job-specific config next to the project assets.

## Choice Style

- Always provide choices with reasons.
- Explain what each choice is good for and what risk it has.
- Recommend one default option based on the supplied images.
- Do not ask the user to decide typography, layout, material, or model route blindly.

## Required Fields

- `job.client_name`
- `job.job_name`
- `preset.product_type`
- `preset.size`
- `preset.material`
- `series.type`
- `series.count`
- `outputs.types`
- `assets.illustrations_dir`

## Handoff

- Use `print-studio-material-selector` when paper/material selection is needed paper/material.
- Use `print-studio-layout-proof` for generic cards and small print products.
- Use `print-studio-calendar-series` for monthly/quarterly/date-based layouts.
- Use `print-studio-prepress-qc` before final delivery.

## Wall Calendar Defaults

- Use `preset.product_type: wall_calendar`.
- Start from `../print-studio-runtime/examples/wall-calendar-8x12.json`.
- Recommended bindings: `top_wire`, `top_hanger_hole`, or `top_clip`.
- Set `production.binding_reserved_mm` when the print shop has exact coil, hook, or clip-strip specs.
