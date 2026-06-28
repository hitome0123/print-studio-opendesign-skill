# Lessons

## 2026-06-22 · Plugin Should Be Modular

- When packaging a broad client workflow as a Codex Plugin, avoid one giant user-facing Skill.
- Use one suite plugin as the product entry, then split capabilities into small triggerable skills.
- Keep deterministic scripts and heavy assets in a shared runtime skill so task skills stay lightweight.
- For print-shop workflows, separate intake, material selection, layout proofing, commerce mockups, and prepress QC.

## 2026-06-23 · Cross-Agent Delivery

- When the user asks for Claude Code support, provide a direct `~/.claude/skills` installation path, not only Codex plugin metadata.
- Keep one canonical runtime shape and sync it into both Codex and Claude-facing skill packages.
- Product status tables must match actual implementation; do not leave “planned” labels after adding functional presets and renderer rules.

## 2026-06-23 · Image-First Guided Intake

- For print design guidance, do not ask users to fully specify product, size, material, layout, and typography upfront.
- Analyze supplied images first, then recommend choices with reasons, risks, and a default option.
- Ground choices in image traits: orientation, brightness, saturation, contrast, detail density, subject position, subject coverage, and series consistency.

## 2026-06-27 · Model Mockup Safety

- Do not ask image models to place the final card layout into white-background or ambiance scenes when text/layout fidelity matters.
- Image models may crop, rewrite text, redraw details, or recompose even when prompts forbid it.
- Safer workflow: generate blank white/lifestyle backgrounds only, then composite the deterministic card output as a separate layer.
- Treat direct model mockups with final card images as disposable experiments, never as print or delivery sources.

## 2026-06-28 · Generalize Visual Fixes

- When a visual issue is found in one case, first decide whether it is a template rule, a product rule, or a one-off asset issue.
- Prefer engine-level quality rules over case-specific tweaks: text layer spacing, safe margins, series-grid balance, and font consistency should apply across products.
- Add QC checks for newly discovered visual risks so the same issue is caught in greeting cards, postcards, bookmarks, gift tags, and calendars.
