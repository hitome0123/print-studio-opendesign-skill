---
name: print-studio-order-intake
description: "Use for print-shop order intake and configuration planning before rendering: clarify product type, series structure, size, paper/material, finishing, double-sided needs, output types, and create or update a Print Studio OpenDesign config JSON. Applies to greeting cards, postcards, calendars, bookmarks, gift tags, packaging inserts, card sets, seasonal sets, and custom N-card print jobs."
---

# Print Studio Order Intake

## Goal

Turn a print request into a runnable Print Studio OpenDesign config.

## Activation Response

When this skill is loaded, first guide the user instead of asking them to fill a full form.

Start with:

```text
我们先从最简单的开始：你可以直接把图片文件夹拖进 Codex，或者把图片文件夹路径发给我。

你不用填完整表格，也不用先学命令。你只要用人类语言告诉我想做什么，比如：
“我想用这些图做一套月历卡”
“我想做贺卡，但尺寸和材质你先推荐”
“我还没想好，你先看图帮我判断”

接下来我会按 4 步走：
1. 理解图片：风格、颜色、主体位置、复杂度、系列统一性。
2. 推荐产品：贺卡、月历卡、明信片、书签、吊牌、挂历或自定义套装。
3. 推荐规格：尺寸、材质、张数、圆角/装订/单双面，并说明为什么。
4. 生成结果：先出材质预览和版式候选，选定后再锁版批量输出。

你现在只需要发图片，或者发图片文件夹路径；如果已经知道要做什么，也可以一起告诉我。
```

If the image folder is already known, proceed directly to the image-first advisor and explain the first recommendation with reasons.

If the user is unsure how to ask, offer copyable templates:

```text
使用 Print Studio OpenDesign。
我给你图片，你先推荐做什么，再生成材质预览、版式候选和完整交付包。
```

```text
使用 Print Studio OpenDesign。
我要做 5×7 英寸贺卡，300g 超白白卡纸。请先生成 A/B/C 版式候选，我确认后再批量输出。
```

For every product type, follow the generalized guidance flow:

1. Collect images.
2. Understand image traits.
3. Recommend a default product/spec with reasons.
4. Offer 2-3 alternatives with risks.
5. Generate material preview and A/B/C candidates.
6. Lock the chosen candidate.
7. Generate delivery package and explain where to look.

Ask one small question at a time. If the user is unsure, recommend a default and continue. Full protocol: `../../../../user-workflow/guided-conversation-flow.zh-CN.md`.

## Windows Install Safety

If the user reports a Windows / PowerShell popup that says `Invoke-WebRequest` may run webpage scripts, pause installation guidance and say:

```text
先点“否”，不要继续用这个下载命令。
这个弹窗通常是 Windows PowerShell 下载网页时的通用安全提醒，不代表项目文件报毒。
建议改用 GitHub 页面里的 Code → Download ZIP，或者用 git clone 下载仓库。
```

If the popup appears again after clicking either **Yes** or **No**, treat this as an installer retry loop:

```text
这个不是你点错了，而是当前安装流程在循环调用 Invoke-WebRequest。
请关闭这个弹窗和当前安装窗口，不要继续点。
接下来不要再走这个一键安装/skill-installer 下载方式。
请用浏览器打开 GitHub，点 Code → Download ZIP 下载，解压后从本地文件夹安装。
```

Do not retry `Invoke-WebRequest` in this case. Prefer manual ZIP download and local folder install.

If PowerShell download is unavoidable, use `Invoke-WebRequest -UseBasicParsing` only:

```powershell
$url = "https://github.com/hitome0123/print-studio-opendesign-skill/archive/refs/heads/main.zip"
$zip = "$env:TEMP\print-studio-opendesign-skill.zip"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath "$env:USERPROFILE\Downloads" -Force
```

Detailed note: `../../../../WINDOWS_SAFE_INSTALL.zh-CN.md`.

## Workflow

1. For a smooth end-to-end first run, prefer the guided flow:
   ```bash
   cd ../print-studio-runtime
   python scripts/run_project_flow.py --images <illustrations_dir> --theme <project_name>
   ```
   This creates the config, writes the image advice report, renders material preview, generates A/B/C candidates, locks one candidate, and builds the delivery package.
2. If images are available and the user only wants advice before rendering, run the image-first advisor:
   ```bash
   cd ../print-studio-runtime
   python scripts/advise_project.py <illustrations_dir>
   ```
3. Use the advisor report to explain product, size, material, layout, typography, model-preview, and print-check recommendations.
4. Identify the product type: card, postcard, desk calendar, wall calendar, bookmark, tag, insert, card set, or custom.
5. Identify the series: single, monthly, quarterly, seasonal, festival set, or custom `N` cards.
6. Select production specs: size, material, bleed, safe margin, double-sided, round corners, binding, finishing.
7. Select outputs: `screen`, `print`, `commerce`, `single`, `grid`, `whitebg`, `ambiance`, `back`, `download_4k`.
8. Copy `../print-studio-runtime/config.example.json` or an example from `../print-studio-runtime/examples/`.
9. Save a job-specific config next to the project assets.

## Choice Style

- Always provide choices with reasons.
- Explain what each choice is good for and what risk it has.
- Recommend one default option based on the supplied images.
- Do not ask the user to decide typography, layout, material, or model route blindly.

## Required Fields

- `job.client_name`
- `job.job_name`
- `preset.product_type`
- `preset.size`
- `preset.material`
- `series.type`
- `series.count`
- `outputs.types`
- `assets.illustrations_dir`

## Handoff

- Use `print-studio-material-selector` when paper/material selection is needed paper/material.
- Use `print-studio-layout-proof` for generic cards and small print products.
- Use `print-studio-calendar-series` for monthly/quarterly/date-based layouts.
- Use `print-studio-prepress-qc` before final delivery.

## Wall Calendar Defaults

- Use `preset.product_type: wall_calendar`.
- Start from `../print-studio-runtime/examples/wall-calendar-8x12.json`.
- Recommended bindings: `top_wire`, `top_hanger_hole`, or `top_clip`.
- Set `production.binding_reserved_mm` when the print shop has exact coil, hook, or clip-strip specs.
