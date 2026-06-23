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
