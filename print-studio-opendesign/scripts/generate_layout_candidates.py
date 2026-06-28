#!/usr/bin/env python3
"""Generate 3 layout candidates for user selection.

This is the safe API/AI handoff shape:
AI may suggest a constrained plan, but rendering is deterministic.
"""
import json
import html
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


def build_candidates(api_seed):
    seed = api_seed or ai_planner.default_plan()
    seeded_plan = {
        "subject_position": seed.get("subject_position", "center"),
        "density": seed.get("density", "medium"),
        "dominant_hue": seed.get("dominant_hue", "warm"),
        "accent": seed.get("accent", "#b07a5a"),
        "vbias": seed.get("vbias", "center"),
        "source": seed.get("source", "default"),
    }
    candidates = json.loads(json.dumps(CANDIDATES))
    candidates[0]["name"] = "API/规则推荐版"
    candidates[0]["reason"] = f"根据首张图的主体位置、细节密度和主色建议生成；来源: {seeded_plan['source']}。"
    candidates[0]["plan"] = seeded_plan
    candidates[1]["plan"]["dominant_hue"] = seeded_plan["dominant_hue"]
    candidates[1]["plan"]["accent"] = seeded_plan["accent"]
    return candidates


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


def write_candidate_html(out_dir, payload):
    cards = []
    config = payload.get("config", "config.json")
    for item in payload["candidates"]:
        preview = Path(item["preview"]).name
        cid = item["candidate_id"]
        command = f"python scripts/lock_layout.py {config} {cid} {Path(config).with_suffix('').name}.locked-{cid}.json"
        cards.append(f"""
        <article class="card">
          <img src="{html.escape(preview)}" alt="候选 {html.escape(cid)}">
          <div class="body">
            <h2>{html.escape(cid)} · {html.escape(item['name'])}</h2>
            <p>{html.escape(item['reason'])}</p>
            <pre>{html.escape(command)}</pre>
          </div>
        </article>""")
    page = f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>{html.escape(payload['theme'])} · 版式候选</title>
<style>
body{{margin:0;background:#f6f0e8;color:#302920;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;padding:30px}}
main{{max-width:1280px;margin:auto}} h1{{font-size:30px;margin:0 0 8px}} p{{color:#6d6258;line-height:1.65}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:22px}}
.card{{background:#fff;border:1px solid #e2d8ca;border-radius:18px;overflow:hidden;box-shadow:0 10px 30px rgba(62,47,31,.08)}}
img{{width:100%;display:block;background:#fbf7ef}} .body{{padding:14px 16px 16px}} h2{{font-size:18px;margin:0 0 8px}}
pre{{white-space:pre-wrap;background:#2d261f;color:#f6eadb;border-radius:12px;padding:12px;line-height:1.5;font-size:12px;overflow:auto}}
.note{{background:#fff7e8;border:1px solid #ead9b9;border-radius:14px;padding:14px 16px;margin-top:16px}}
</style><main>
<h1>{html.escape(payload['theme'])} · 选择一个版式</h1>
<p>先看 A/B/C 的视觉方向。选中后复制对应命令，生成 locked 配置，再用 locked 配置批量输出。模型只参与建议，最终排版由规则引擎稳定执行。</p>
<div class="note">建议：如果要稳定批量出图，先锁定一版，不要每张重新让模型自由发挥。当前顾问来源：{html.escape(payload.get('planner_seed', {}).get('source', 'default'))}</div>
<section class="grid">{''.join(cards)}</section>
</main></html>"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


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

    layout_ai = resolved.get("layout_ai", {})
    api_seed = ai_planner.plan_for(str(image_path), enabled=True, options=layout_ai)
    candidates = build_candidates(api_seed)
    out_root = Path(os.environ.get("PRINT_STUDIO_OUTPUT_ROOT", HERE / "output"))
    out_dir = out_root / resolved["theme"] / "layout_candidates"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "theme": resolved["theme"],
        "config": str(cfg_path),
        "prepared_config": str(prepared_config),
        "source_image": str(image_path),
        "planner_seed": api_seed,
        "layout_ai": layout_ai,
        "selection_instruction": "选择 candidate_id 后运行 scripts/lock_layout.py <config> <candidate_id>",
        "candidates": [],
    }
    for candidate in candidates:
        plan = {**candidate["plan"], "candidate_id": candidate["candidate_id"]}
        plan["source"] = f"candidate:{candidate['candidate_id']}:{candidate['plan'].get('source', 'preset')}"
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
    write_candidate_html(out_dir, payload)
    print(f"done -> {out_dir}")
    print(f"打开选择页: {out_dir / 'index.html'}")
    print(f"顾问来源: {api_seed.get('source')}")
    print("候选: " + " / ".join(f"{c['candidate_id']}={c['name']}" for c in candidates))


if __name__ == "__main__":
    main()
