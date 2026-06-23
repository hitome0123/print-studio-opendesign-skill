# Print Studio OpenDesign · Claude Code Notes

This repository can be used by both Codex and Claude Code.

## Claude Code Support

- Standalone skills can be copied into `~/.claude/skills/`.
- The OpenDesign-style plugin suite is under `plugins/print-studio-opendesign/skills/`.
- Install for Claude Code with:

```bash
bash claude-code/install.sh
```

## Recommended Claude Workflow

For a first-time user simulation, start with:

- `user-workflow/user-order-form.zh-CN.md`
- `user-workflow/conversation-examples.zh-CN.md`
- `user-workflow/user-acceptance-sop.zh-CN.md`

1. Use `print-studio-order-intake` to create a job config.
2. Use `print-studio-material-selector` to generate material previews.
3. Use `print-studio-layout-proof` or `print-studio-calendar-series` to render proofs.
4. Use `print-studio-commerce-mockup` for white-background and ambiance images.
5. Use `print-studio-prepress-qc` before delivery.

Keep generated `output/`, `.tmp/`, and `__pycache__/` files out of commits.
