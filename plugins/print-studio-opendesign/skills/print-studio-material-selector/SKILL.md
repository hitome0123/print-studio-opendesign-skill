---
name: print-studio-material-selector
description: "Use to generate or explain Print Studio OpenDesign material selection previews for paper, card stock, textured paper, pearl paper, blue-core/black-core/white-core stock, and PVC. Produces customer-facing material selector HTML/cards and sales notes such as suitable use cases, small-text cautions, gloss/matte simulation, and color compensation hints."
---

# Print Studio Material Selector

## Goal

Help a print shop show customers selectable material options before final design proofing.

## Workflow

1. Start from a valid Print Studio config.
2. Ensure `preset.material` is set to the currently recommended material.
3. Run from `../print-studio-runtime/`:
   ```bash
   python scripts/preview_config.py <config.json> --all-materials
   ```
4. Open `output/<job>/preview/materials.html`.
5. Explain that material effects are screen simulations, not physical proof guarantees.

## Must Show

- White card / kraft / pearl / textured paper / PVC / white-core / blue-core / black-core.
- Blue-core and black-core side color hints.
- PVC gloss or matte cues.
- Pearl paper subtle reflection cue.
- Stronger visible texture for linen, eggshell, wrinkle, and tree-like papers.
- Sales warning: shallow text, low contrast, and pale colors may print weakly.

## Handoff

After material selection, use `print-studio-layout-proof` or `print-studio-calendar-series`.

