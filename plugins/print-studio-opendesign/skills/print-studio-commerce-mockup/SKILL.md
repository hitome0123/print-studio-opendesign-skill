---
name: print-studio-commerce-mockup
description: "Use to create or review presentation display images for Print Studio OpenDesign jobs: white-background product shots, ambiance/lifestyle shots, material preview images, series overview images, per-image 4K downloads, and optional Jimeng/Gemini/GPT-Image2 preview comparisons. Keeps display mockups separate from print source files."
---

# Print Studio Commerce Mockup

## Goal

Produce presentation images for confirmation, ecommerce display, model comparison, and download handoff.

## Workflow

1. Confirm the print proof exists and the product form is correct.
2. Ensure `outputs.types` includes `commerce`, `whitebg`, or `ambiance`; keep `outputs.download_4k` enabled for per-image 4K saves.
3. Run from `../print-studio-runtime/`:
   ```bash
   python scripts/run.py <config.json>
   ```
4. Review `output/<job>/commerce/`, `output/<job>/download_4k/index.html`, and optional `output/<job>/provider_previews/index.html`.

## Mockup Rules

- Mockups are display assets only. Never use image-generation output as the production layout or print source.
- Prefer `local_mockup` by default for stable demos and delivery; AI mockups are optional variants for style exploration.
- White-background images can be brighter and cleaner than print source files.
- Ambiance images may include props and light, but must not change the product design.
- Do not use commerce mockups as production print files.
- If AI changes size, shape, paper edge, date text, or artwork, tighten prompts or rerun.
- If AI crops, rewrites, relayouts, or changes the card, discard that mockup and regenerate with `local_mockup`.
- Show both white-background and ambiance views when presentation material is needed.
- For first-round model selection, enable `image_gen.provider_previews` to compare 即梦, Gemini, and GPT-Image2 before locking the production mockup route.
- Keep 4K download files as long-edge 4096px JPGs so each image can be saved independently.

## Handoff

Use `print-studio-prepress-qc` for final production checks.
