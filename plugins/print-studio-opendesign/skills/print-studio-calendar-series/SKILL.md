---
name: print-studio-calendar-series
description: "Use for date-based Print Studio OpenDesign products: 12-month calendar cards, quarterly cards, seasonal cards, solar-term/holiday sets, desk-calendar cards, and wall-calendar proofing. Handles real calendar dates, month labels, date readability, layout rhythm, bleed/safe margins, wall-calendar top binding zones, and print-aware color rules."
---

# Print Studio Calendar Series

## Goal

Create printable calendar or date-based card series from illustrations.

## Workflow

1. Confirm `content.year`, language, week-start convention, and series count.
2. Use `monthly_calendar` for 12-month layouts; use quarterly or seasonal structure when requested.
3. Confirm if the output is a desk calendar, wall calendar, loose card set, or product insert.
4. Run from `../print-studio-runtime/`:
   ```bash
   python scripts/preview_config.py <config.json> --all-materials
   python scripts/run.py <config.json>
   ```
5. Check date accuracy and readability before handoff.

## Date Rules

- Never invent dates manually when deterministic date generation is available.
- Date numbers must not be sacrificed for aesthetics.
- Week labels and month names must remain readable after print.
- Thin decorative lines must not fall below printable visibility.
- If the product is bound, reserve extra safe space near binding.
- For wall calendars, use `preset.product_type: wall_calendar` and one of `production.binding: top_wire/top_hanger_hole/top_clip`.
- If binding specs are unknown, default to 12mm top reserved area and flag it for physical proofing.

## Wall Calendar Example

Use:

```bash
python scripts/run.py examples/wall-calendar-8x12.json
```

## Handoff

Use `print-studio-prepress-qc` for print-readiness and package review.
