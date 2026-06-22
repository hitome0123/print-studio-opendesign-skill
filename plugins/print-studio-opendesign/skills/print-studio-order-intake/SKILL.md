---
name: print-studio-order-intake
description: "Use for print-shop order intake and configuration planning before rendering: clarify product type, series structure, size, paper/material, finishing, double-sided needs, output types, and create or update a Print Studio OpenDesign config JSON. Applies to greeting cards, postcards, calendars, bookmarks, gift tags, packaging inserts, card sets, seasonal sets, and custom N-card print jobs."
---

# Print Studio Order Intake

## Goal

Turn a customer request into a runnable Print Studio OpenDesign config.

## Workflow

1. Identify the product type: card, postcard, calendar, bookmark, tag, insert, card set, or custom.
2. Identify the series: single, monthly, quarterly, seasonal, festival set, or custom `N` cards.
3. Select production specs: size, material, bleed, safe margin, double-sided, round corners, binding, finishing.
4. Select outputs: `screen`, `print`, `commerce`, `single`, `grid`, `whitebg`, `ambiance`, `back`.
5. Copy `../print-studio-runtime/config.example.json` or an example from `../print-studio-runtime/examples/`.
6. Save a job-specific config next to the customer assets.

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

- Use `print-studio-material-selector` when the customer needs to choose paper/material.
- Use `print-studio-layout-proof` for generic cards and small print products.
- Use `print-studio-calendar-series` for monthly/quarterly/date-based layouts.
- Use `print-studio-prepress-qc` before final delivery.

