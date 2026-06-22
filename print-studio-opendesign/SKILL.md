---
name: print-studio-opendesign
description: "印刷厂 AI 系列设计打样 Skill。Use when Codex needs to help a print shop turn client-provided illustrations/images into configurable print-ready product mockups and delivery packages: choose product type, series structure, size, material/paper, basic production specs, then generate customer previews, print files, white-background product shots, ambiance shots, QC reports, zipped handoff packages, and material selector previews. Applies to greeting cards, postcards, desk/wall calendars, monthly or quarterly cards, card sets, bookmarks, thank-you cards, invitation cards, packaging inserts, gift tags, sticker cards, and custom illustration series."
---

# Print Studio OpenDesign

## Core Positioning

Use this skill as a **print shop AI proofing assistant**, not a one-off calendar tool.

The job: a print shop receives client images, chooses production specs, and quickly creates a proofing package for sales confirmation, design review, and print handoff.

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
   - `job`: client/job metadata.
   - `preset`: size, material, product form, visual style, language.
   - `series`: monthly, quarterly, seasonal, custom N-card set.
   - `outputs`: screen, print, commerce, single/grid/whitebg/ambiance.
3. For quick customer confirmation, run:
   - `python scripts/preview_config.py config.example.json --all-materials`
4. For full delivery, run:
   - `python scripts/run.py config.example.json`
5. Inspect:
   - `output/<theme>/preview/` customer config/material preview.
   - `output/<theme>/screen/` customer preview files.
   - `output/<theme>/print/` 300dpi print files with bleed.
   - `output/<theme>/commerce/` white-background and ambiance product shots.
   - `output/<theme>/qc_report.json`.
   - `output/<theme>/*_交付包.zip`.
6. Report whether the result is fit for: customer proposal, sample proof, or final print handoff.

## Configuration Rules

- Relative `illustrations_dir` is resolved against the config file first, then the bundled sample folder.
- For customer work, prefer a copied config per job and an image folder with numbered filenames: `1.png`, `2.png`, ...
- `monthly_calendar` uses the calendar renderer. `custom_cards`, `quarterly`, `seasonal`, and `festival_set` can use the bundled `generic_card` renderer with configurable `series.count`.
- Use `preview_config.py` before full AI/mockup generation; it is fast, deterministic, and does not call image generation.

## Delivery Rules

- Keep AI layout constrained. AI may choose visual emphasis, title accent, and layout hints. Rendering, date accuracy, bleed, safe margins, and print sizing must remain deterministic.
- Keep print files separate from commerce mockups. Product mockups are for selling and presentation; print files are the production source.
- Treat all non-tested paper compensation as estimated. Recommend physical proofing before batch print.
- Do not promise CMYK/ICC-perfect color unless a real ICC workflow is added and tested.
- Material selector previews are screen simulations only: paper core colors, PVC gloss, pearl reflections, and texture strength are visual aids, not production guarantees.
- If white-background or ambiance mockups drift in product form, tighten product-form prompts before delivery.

## Read When Needed

- For operator workflow and sales language: `references/operator-guide.md`.
- For paper/material keys: `assets/calendar_series/presets.json`.
- For print compensation behavior: `assets/calendar_series/engine/profiles.py`.
