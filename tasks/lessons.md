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

## 2026-06-28 · Productize the First-Run Experience

- Do not make users edit JSON as the first contact with a skill; add a guided starter that creates a runnable config.
- Any visual decision step should have an HTML review surface, not just a JSON artifact.
- If a generated review page influences delivery, include it in the final ZIP and link it from the delivery homepage.
- Keep material choices backed by actual preset keys; never offer friendly labels that cannot run.

## 2026-06-28 · API Is Advisor, Renderer Is Authority

- Direct API calls improve consistency over chatbot copy-paste, but do not make image models safe as final layout renderers.
- Keep provider output constrained to a small JSON design plan and clamp every field into preset enums before rendering.
- Always persist provider/source metadata in candidates and locked configs so results can be explained and reproduced.
- Locked configs should write absolute asset paths when saved outside the source config folder.

## 2026-06-28 · Skills Need a First-Run Script

- A user-facing skill should not assume the user knows the workflow after loading it.
- Always start with a guided first response: ask for the image folder, explain the 4-step path, and recommend the next action.
- Keep commands and JSON behind the guided flow; expose them only when the user is ready to run or customize.
