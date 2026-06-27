#!/usr/bin/env python3
"""Generate 3 layout candidates for user selection.

This is the safe API/AI handoff shape:
AI may suggest a constrained plan, but rendering is deterministic.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ENGINE = HERE / "assets" / "calendar_series"
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ENGINE / "engine"))

from config_schema import resolve_config  # noqa: E402
from layout_engine import render_page  # noqa: E402
import ai_planner  # noqa: E402


CANDIDATES = [
    {
        "candidate_id": "A",
        "name": "稳妥居中版",
        "reason": "主体居中、上下结构清晰，适合需要稳定批量输出的卡片/月历。",
        "plan": {
            "subject_position": "center",
            "density": "medium",
            "dominant_hue": "warm",
            "accent": "#b07a5a",
            "vbias": "center",
        },
    },
    {
        "candidate_id": "B",
        "name": "主视觉放大版",
        "reason": "让插画成为第一视觉，适合主体可爱、装饰细节丰富的系列。",
        "plan": {
            "subject_position": "top-heavy",
            "density": "airy",
            "dominant_hue": "red",
            "accent": "#c1604f",
            "vbias": "top-heavy",
        },
    },
    {
        "candidate_id": "C",
        "name": "高级留白版",
        "reason": "颜色和标题更克制，适合礼品卡、文具套装、需要高级感的展示。",
        "plan": {
            "subject_position": "center",
            "density": "airy",
            "dominant_hue": "neutral",
            "accent": "#a8806a",
            "vbias": "center",
        },
    },
]


def prepare_config(config_path):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    illustrations = Path(cfg.get("illustrations_dir", "example_illustrations"))
    if not illustrations.is_absolute():
        local_candidate = (config_path.parent / illustrations).resolve()
        bundled_candidate = (ENGINE / illustrations).resolve()
        if local_candidate.exists():
            cfg["illustrations_dir"] = str(local_candidate)
        elif bundled_candidate.exists():
            cfg["illustrations_dir"] = str(bundled_candidate)
        else:
            cfg["illustrations_dir"] = str(local_candidate)
    tmp_dir = HERE / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    prepared = tmp_dir / "layout_candidates.resolved.json"
    prepared.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return prepared


def find_first_illustration(folder):
    folder = Path(folder)
    if not folder.is_absolute():
        folder = (HERE / folder).resolve()
    if not folder.exists():
        raise SystemExit(f"illustrations_dir 不存在: {folder}")
    found = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in (".png", ".jpg", ".jpeg") and re.match(r"\s*(\d+)", path.name):
            found.append((int(re.match(r"\s*(\d+)", path.name).group(1)), path))
    if not found:
        raise SystemExit(f"{folder} 没找到数字开头的图片")
    return sorted(found, key=lambda item: item[0])[0]


def main():
    cfg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "config.example.json"
    prepared_config = prepare_config(cfg_path.resolve())
    resolved = resolve_config(prepared_config)
    if resolved["errors"]:
        raise SystemExit("\n".join(resolved["errors"]))

    month, image_path = find_first_illustration(resolved["illustrations_dir"])
    size = resolved["size"]
    width, height = size.get("trim_px") or (1500, 2100)
    family = "landscape" if width > height else "portrait"
    content = resolved["content"]
    year = content.get("year", 2027)
    keywords = content.get("month_keywords") or []
    keyword = keywords[month - 1] if month - 1 < len(keywords) else None
    poem_left = content.get("corner_poem_left", "") if content.get("keep_poems", True) else ""
    poem_right = content.get("corner_poem_right", "") if content.get("keep_poems", True) else ""
    seal = content.get("seal_initials", "") if content.get("keep_seal", True) else ""

    api_seed = ai_planner.plan_for(str(image_path), enabled=bool(os.getenv("GEMINI_API_KEY")))
    out_root = Path(os.environ.get("PRINT_STUDIO_OUTPUT_ROOT", HERE / "output"))
    out_dir = out_root / resolved["theme"] / "layout_candidates"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "theme": resolved["theme"],
        "config": str(cfg_path),
        "prepared_config": str(prepared_config),
        "source_image": str(image_path),
        "planner_seed": api_seed,
        "selection_instruction": "选择 candidate_id 后运行 scripts/lock_layout.py <config> <candidate_id>",
        "candidates": [],
    }
    for candidate in CANDIDATES:
        plan = {**candidate["plan"], "source": "candidate", "candidate_id": candidate["candidate_id"]}
        preview_path = out_dir / f"candidate_{candidate['candidate_id']}.jpg"
        render_page(
            width,
            height,
            family,
            year,
            month,
            str(image_path),
            str(preview_path),
            keyword=keyword,
            accent=plan["accent"],
            vbias=plan["vbias"],
            poem_left=poem_left,
            poem_right=poem_right,
            seal=seal,
            week_start=content.get("week_start", "sunday"),
            production=resolved.get("production"),
        )
        payload["candidates"].append({
            **candidate,
            "plan": plan,
            "preview": str(preview_path),
            "locked_layout": {
                "enabled": True,
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "reason": candidate["reason"],
                "plan": plan,
            },
        })

    (out_dir / "layout_candidates.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"done -> {out_dir}")
    print("候选: " + " / ".join(f"{c['candidate_id']}={c['name']}" for c in CANDIDATES))


if __name__ == "__main__":
    main()
