---
name: print-studio-runtime
description: "Shared runtime for the Print Studio OpenDesign plugin. Use this when another print-studio skill needs to execute the bundled deterministic renderer, preview generator, material selector, print export, commerce mockup workflow, QC report, or zipped delivery package. This is the implementation layer, not the preferred user-facing planning skill."
---

# Print Studio OpenDesign

## Core Positioning

Use this skill as a **print shop AI proofing assistant**, not a one-off calendar tool.

The job: import images, choose production specs, and quickly create a proofing package for confirmation, design review, ecommerce display, and print handoff.

## Activation Response

Whenever this skill is loaded for a user-facing task, start by guiding the user step by step. Do not begin with JSON or a long command list.

First response template:

```text
我会一步步带你完成印刷品打样。你不用写 JSON，也不用先学命令。

你可以直接把图片文件夹拖进 Codex，或者发图片文件夹路径，然后用人类语言告诉我想做什么。

例如你可以说：
“使用 Print Studio OpenDesign。这些图片想做一套 12 张月历卡，请先推荐尺寸、材质和版式，再生成材质预览和 A/B/C 候选。”

接下来我会：
1. 先理解图片风格、颜色、主体位置和系列统一性。
2. 推荐适合的产品、尺寸、材质、张数和版式，并说明理由。
3. 生成材质预览和 A/B/C 版式候选。
4. 你选中一版后，我会锁版并批量生成预览图、印刷文件、白底图、氛围图、系列总览、4K 下载图和交付包。

你现在只要发图片，或者说“先用演示案例跑一遍”也可以。
```

If the user has already supplied an image folder, skip asking for it again and proceed to image-first analysis. If the user asks to run a demo, use the bundled `demo/xiaotuzi-calendar-5x7.json` when available. Always offer a recommended next action, not a menu with too many equal choices.

Also include 2-3 copyable prompt templates whenever the user seems unsure what to say. Keep them short and tailored to the situation.

Default templates:

```text
使用 Print Studio OpenDesign。
我给你图片，你先推荐做什么，再生成材质预览、版式候选和完整交付包。
```

```text
使用 Print Studio OpenDesign。
我要用这组图片做一套 12 张月历卡，请推荐尺寸、材质和版式，并生成预览图、印刷文件、白底图、氛围图、系列总览和 4K 下载图。
```

```text
使用 Print Studio OpenDesign。
请先不要批量输出，先根据这组图片生成 A/B/C 三个版式候选，并说明每个候选的优点和风险。
```

For the full prompt library, refer to `../../../../user-workflow/prompt-templates.zh-CN.md` if available in the repository.

## What Is Bundled

- `config.example.json`: editable job configuration.
- `examples/`: ready-to-copy configs for greeting cards, postcards, bookmarks, and gift tags.
- `scripts/run_project_flow.py`: guided one-command flow from image folder to final delivery package.
- `scripts/start_project.py`: interactive project wizard for users who should not edit JSON by hand.
- `scripts/advise_project.py`: image-first guided advisor that analyzes supplied images and recommends products, sizes, materials, layouts, typography, provider previews, and print checks with reasons.
- `scripts/generate_layout_candidates.py`: generate A/B/C constrained layout candidates plus a visual `layout_candidates/index.html` selection page.
- `scripts/lock_layout.py`: write the selected candidate into `layout_lock` so batch rendering stays stable.
- `scripts/preview_config.py`: fast no-AI preview and 24-material selector page.
- `scripts/run.py`: full delivery run through the bundled calendar-series engine.
- `assets/calendar_series/`: bundled print template engine, including calendar and generic-card renderers.
- `assets/calendar_series/design_presets.json`: typography, layout, and color preset library with reasons and risks.
- `../../../../user-workflow/prompt-templates.zh-CN.md`: copyable user prompt templates for common print jobs.
- `references/operator-guide.md`: sales/operator notes and V1 boundaries.

## MVP Workflow

1. For the smooth first-run experience, prefer:
   - `python scripts/run_project_flow.py`
   - Or non-interactive: `python scripts/run_project_flow.py --images <illustrations_dir> --theme <project_name>`
   - This runs image advice, material preview, A/B/C candidates, layout lock, full delivery, and prints the final delivery homepage path.
2. If the user only wants to create a config first, run:
   - `python scripts/start_project.py`
   - This creates a runnable config by asking for image folder, project name, product type, series count, material, and year.
3. Start image-first when images are available:
   - `python scripts/advise_project.py <illustrations_dir>`
   - Use the report to explain choices before asking for product/size/material decisions.
4. Read or create a config based on `config.example.json`.
5. Confirm the four decision layers:
   - `job`: project metadata.
   - `preset`: size, material, product form, visual style, language.
   - `series`: monthly, quarterly, seasonal, custom N-card set.
   - `outputs`: screen, print, commerce, single/grid/whitebg/ambiance.
6. For quick review confirmation, run:
   - `python scripts/preview_config.py config.example.json --all-materials`
7. If the user wants to choose a layout before batch output, run:
   - `python scripts/generate_layout_candidates.py config.example.json`
   - Open `output/<theme>/layout_candidates/index.html` and select A/B/C with visible reasons.
   - `python scripts/lock_layout.py config.example.json B config.locked-B.json`
   - Then use the locked config for batch output.
8. For full delivery, run:
   - `python scripts/run.py config.example.json`
9. Inspect:
   - `output/<theme>/交付说明.html` delivery homepage for all generated assets.
   - `output/<theme>/preview/` job config/material preview.
   - `output/<theme>/screen/` preview files.
   - `output/<theme>/print/` 300dpi print files with bleed.
   - `output/<theme>/commerce/` white-background, ambiance, and series overview product shots.
   - `output/<theme>/download_4k/` per-image 4K long-edge JPG files and download page.
   - `output/<theme>/provider_previews/` optional Jimeng / Gemini / GPT-Image2 comparison page.
   - `output/<theme>/design_plan.json` CreatiPoster-style structured layer/preset plan.
   - `output/<theme>/qc_report.json` machine-readable QC result.
   - `output/<theme>/prepress_report.zh-CN.md` Chinese print-readiness report: why it can proceed and what needs manual confirmation.
   - `output/<theme>/reports/` report files included in the ZIP.
   - `output/<theme>/*_交付包.zip`.
10. Report whether the result is fit for: proposal preview, sample proof, or final print handoff.

## Guided Advisor Rules

- Do not force the user to provide a complete spec upfront.
- When images are available, analyze image orientation, brightness, saturation, contrast, detail density, subject position, subject coverage, and series consistency first.
- Recommend product, size, material, layout, typography, and model-preview choices with a reason and caution.
- Offer a default recommendation, but keep alternatives visible.
- Ground every recommendation in the supplied images plus print constraints.
- Emit `design_plan.json` so typography/layout/color choices are explicit, reusable, and reviewable.
- Emit `prepress_report.zh-CN.md` so every run explains print-readiness and manual confirmation points.
- If `layout_ai` is enabled, API providers may analyze the first/source image and suggest a constrained JSON layout seed. This seed may influence candidates, but it must not render or alter the final artwork.

## Configuration Rules

- Relative `illustrations_dir` is resolved against the config file first, then the bundled sample folder.
- For project work, prefer a copied config per job and an image folder with numbered filenames: `1.png`, `2.png`, ...
- `monthly_calendar` uses the calendar renderer. `custom_cards`, `quarterly`, `seasonal`, and `festival_set` can use the bundled `generic_card` renderer with configurable `series.count`.
- Use `preview_config.py` before full AI/mockup generation; it is fast, deterministic, and does not call image generation.

## Delivery Rules

- Never ask ChatGPT / image-generation models to create the final layout from a layout prompt. Generative models may crop, recompose, rewrite text, or alter artwork. Final layout must come from the deterministic renderer (`screen/`, `print/`, `design_plan.json`).
- API layout providers are advisor-only. They may return `subject_position`, `density`, `dominant_hue`, `confidence`, and `reason`; all values are clamped to the preset design system before rendering.
- Keep AI layout constrained. AI may choose visual emphasis, title accent, and layout hints. Rendering, date accuracy, bleed, safe margins, and print sizing must remain deterministic.
- Keep print files separate from commerce mockups. Product mockups are for visual confirmation and presentation; print files are the production source.
- Default commerce mockups should use `local_mockup` unless the user explicitly wants model comparison. This keeps the full card visible and prevents accidental AI cropping during demos or delivery.
- Treat all non-tested paper compensation as estimated. Recommend physical proofing before batch print.
- Do not promise CMYK/ICC-perfect color unless a real ICC workflow is added and tested.
- Material selector previews are screen simulations only: paper core colors, PVC gloss, pearl reflections, and texture strength are visual aids, not production guarantees.
- If white-background or ambiance mockups drift in product form, tighten product-form prompts before delivery.
- If AI white-background or ambiance mockups crop, rewrite, or change the card, discard those mockups and regenerate with `local_mockup` or deterministic layout files.

## Read When Needed

- For operator workflow and usage language: `references/operator-guide.md`.
- For paper/material keys: `assets/calendar_series/presets.json`.
- For print compensation behavior: `assets/calendar_series/engine/profiles.py`.
