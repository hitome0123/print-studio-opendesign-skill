---
name: print-studio-runtime
description: "Shared runtime for the Print Studio OpenDesign plugin. Use this when another print-studio skill needs to execute the bundled deterministic renderer, preview generator, material selector, print export, commerce mockup workflow, QC report, or zipped delivery package. This is the implementation layer, not the preferred user-facing planning skill."
---

# Print Studio OpenDesign

## Core Positioning

Use this skill as a **print shop AI proofing assistant**, not a one-off calendar tool.

The job: import images, choose production specs, and quickly create a proofing package for confirmation, design review, ecommerce display, and print handoff.

## What Is Bundled

- `config.example.json`: editable job configuration.
- `examples/`: ready-to-copy configs for greeting cards, postcards, bookmarks, and gift tags.
- `scripts/preview_config.py`: fast no-AI preview and 24-material selector page.
- `scripts/run.py`: full delivery run through the bundled calendar-series engine.
- `assets/calendar_series/`: bundled print template engine, including calendar and generic-card renderers.
- `references/operator-guide.md`: sales/operator notes and V1 boundaries.

## MVP Workflow

1. Read or create a config based on `config.example.json`.
2. Confirm the four decision layers:
   - `job`: project metadata.
   - `preset`: size, material, product form, visual style, language.
   - `series`: monthly, quarterly, seasonal, custom N-card set.
   - `outputs`: screen, print, commerce, single/grid/whitebg/ambiance.
3. For quick review confirmation, run:
   - `python scripts/preview_config.py config.example.json --all-materials`
4. For full delivery, run:
   - `python scripts/run.py config.example.json`
5. Inspect:
   - `output/<theme>/preview/` job config/material preview.
   - `output/<theme>/screen/` preview files.
   - `output/<theme>/print/` 300dpi print files with bleed.
   - `output/<theme>/commerce/` white-background, ambiance, and series overview product shots.
   - `output/<theme>/download_4k/` per-image 4K long-edge JPG files and download page.
   - `output/<theme>/provider_previews/` optional Jimeng / Gemini / GPT-Image2 comparison page.
   - `output/<theme>/qc_report.json`.
   - `output/<theme>/*_交付包.zip`.
6. Report whether the result is fit for: proposal preview, sample proof, or final print handoff.

## Configuration Rules

- Relative `illustrations_dir` is resolved against the config file first, then the bundled sample folder.
- For project work, prefer a copied config per job and an image folder with numbered filenames: `1.png`, `2.png`, ...
- `monthly_calendar` uses the calendar renderer. `custom_cards`, `quarterly`, `seasonal`, and `festival_set` can use the bundled `generic_card` renderer with configurable `series.count`.
- Use `preview_config.py` before full AI/mockup generation; it is fast, deterministic, and does not call image generation.

## Delivery Rules

- Keep AI layout constrained. AI may choose visual emphasis, title accent, and layout hints. Rendering, date accuracy, bleed, safe margins, and print sizing must remain deterministic.
- Keep print files separate from commerce mockups. Product mockups are for visual confirmation and presentation; print files are the production source.
- Treat all non-tested paper compensation as estimated. Recommend physical proofing before batch print.
- Do not promise CMYK/ICC-perfect color unless a real ICC workflow is added and tested.
- Material selector previews are screen simulations only: paper core colors, PVC gloss, pearl reflections, and texture strength are visual aids, not production guarantees.
- If white-background or ambiance mockups drift in product form, tighten product-form prompts before delivery.

## Read When Needed

- For operator workflow and usage language: `references/operator-guide.md`.
- For paper/material keys: `assets/calendar_series/presets.json`.
- For print compensation behavior: `assets/calendar_series/engine/profiles.py`.
