#!/usr/bin/env python3
"""Guided one-command flow for Print Studio OpenDesign.

Runs the first-user path end to end:
images -> config -> advice -> material preview -> layout candidates -> lock -> delivery.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HERE / "output"
PRESETS = json.loads((HERE / "assets/calendar_series/presets.json").read_text(encoding="utf-8"))

PRODUCTS = {
    "calendar": ("calendar_card", "monthly_calendar", "calendar_series", "desk_cal_5x7", "single_card", 12),
    "greeting": ("greeting_card", "custom_cards", "generic_card", "greeting_5x7", "single_card", 1),
    "postcard": ("postcard", "custom_cards", "generic_card", "postcard_7x5", "postcard", 6),
    "bookmark": ("bookmark", "custom_cards", "generic_card", "bookmark_2x6", "single_card", 4),
    "tag": ("gift_tag", "custom_cards", "generic_card", "gift_tag_2x3_5", "single_card", 8),
    "wall_calendar": ("wall_calendar", "monthly_calendar", "calendar_series", "wall_cal_8x12", "wall_coil", 12),
}

MATERIAL_SHORTLIST = [
    "white_card_300g",
    "pearl_ice_white_300g",
    "fine_linen_superwhite_300g",
    "linen_ivory_300g",
    "eggshell_ivory_300g",
    "wrinkle_ivory_300g",
    "blue_core_300g",
    "black_core_330g",
]


def ask(prompt, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def slugify(value):
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value.strip())
    return value or "print-studio-project"


def choose_product(raw):
    aliases = {
        "1": "calendar", "月历": "calendar", "月历卡": "calendar", "calendar_card": "calendar",
        "2": "greeting", "贺卡": "greeting", "card": "greeting",
        "3": "postcard", "明信片": "postcard",
        "4": "bookmark", "书签": "bookmark",
        "5": "tag", "吊牌": "tag",
        "6": "wall_calendar", "挂历": "wall_calendar",
    }
    key = aliases.get(str(raw).strip(), str(raw).strip() or "calendar")
    if key not in PRODUCTS:
        raise SystemExit(f"未知产品类型: {raw}; 可选 calendar/greeting/postcard/bookmark/tag/wall_calendar")
    return key


def choose_material(raw):
    materials = PRESETS["materials"]
    if not raw:
        return "white_card_300g"
    if str(raw).isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(MATERIAL_SHORTLIST):
            return MATERIAL_SHORTLIST[idx]
    if raw in materials:
        return raw
    raise SystemExit(f"未知材质: {raw}; 可输入 white_card_300g 或 1-{len(MATERIAL_SHORTLIST)}")


def interactive_args(args):
    if not args.images:
        print("Print Studio OpenDesign · 一键引导流程")
        print("我会自动跑：图片理解 → 材质预览 → 版式候选 → 锁版 → 完整交付。")
        args.images = ask("图片文件夹路径")
    image_dir = Path(args.images).expanduser().resolve()
    if not image_dir.exists():
        raise SystemExit(f"图片文件夹不存在: {image_dir}")
    if not args.theme:
        args.theme = ask("项目名称", image_dir.name)
    if not args.product:
        print("产品类型：1 月历卡  2 贺卡  3 明信片  4 书签  5 吊牌  6 挂历")
        args.product = ask("请选择", "1")
    product_key = choose_product(args.product)
    if args.count is None:
        args.count = int(ask("系列张数", str(PRODUCTS[product_key][5])))
    if not args.material:
        print("材质推荐：")
        for idx, key in enumerate(MATERIAL_SHORTLIST, start=1):
            item = PRESETS["materials"][key]
            print(f"{idx}. {item['label']} —— {item.get('use_case', '')}")
        args.material = ask("请选择材质", "1")
    args.product = product_key
    args.material = choose_material(args.material)
    if not args.candidate:
        args.candidate = ask("锁定候选 A/B/C", "B")
    return image_dir


def write_config(args, image_dir):
    product_type, series_type, template, size_key, product_form, _ = PRODUCTS[args.product]
    config = json.loads((HERE / "config.example.json").read_text(encoding="utf-8"))
    config["theme"] = args.theme
    config["illustrations_dir"] = str(image_dir)
    config["job"]["job_name"] = args.theme
    config["series"].update({"type": series_type, "count": args.count, "template": template})
    config["preset"].update({
        "product_type": product_type,
        "size": size_key,
        "material": args.material,
        "product_form": product_form,
    })
    config["content"]["year"] = args.year
    config["content"]["real_dates"] = template == "calendar_series"
    if product_type == "wall_calendar":
        config["production"]["binding"] = "top_wire"
        config["production"]["binding_reserved_mm"] = 12
        config["production"]["finishing"] = ["top_wire"]
    config["outputs"]["download_4k"] = True
    config["image_gen"]["backend"] = "local_mockup"
    flow_dir = HERE / ".tmp" / "guided_flow"
    flow_dir.mkdir(parents=True, exist_ok=True)
    config_path = flow_dir / f"{slugify(args.theme)}.config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return config_path


def run_step(label, command):
    print(f"\n▶ {label}", flush=True)
    print("  " + " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], cwd=HERE, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run a guided Print Studio proofing flow end to end.")
    parser.add_argument("--images", help="图片文件夹路径")
    parser.add_argument("--theme", help="项目名称")
    parser.add_argument("--product", help="calendar/greeting/postcard/bookmark/tag/wall_calendar 或 1-6")
    parser.add_argument("--count", type=int, help="系列张数")
    parser.add_argument("--material", help="材质 key 或推荐编号")
    parser.add_argument("--year", type=int, default=2027)
    parser.add_argument("--candidate", choices=["A", "B", "C", "a", "b", "c"], help="自动锁定的候选版式")
    args = parser.parse_args()

    image_dir = interactive_args(args)
    args.candidate = args.candidate.upper()
    config_path = write_config(args, image_dir)
    out_dir = OUTPUT_ROOT / args.theme
    reports_dir = out_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    advice_md = reports_dir / "print_studio_advice.md"
    advice_json = reports_dir / "print_studio_advice.json"
    locked_path = config_path.with_name(f"{config_path.stem}.locked-{args.candidate}.json")

    print(f"\n已生成配置: {config_path}", flush=True)
    run_step("1/5 图片理解与推荐", [sys.executable, "scripts/advise_project.py", str(image_dir), "--out", advice_md, "--json", advice_json])
    run_step("2/5 材质与尺寸预览", [sys.executable, "scripts/preview_config.py", config_path, "--all-materials"])
    run_step("3/5 生成 A/B/C 版式候选", [sys.executable, "scripts/generate_layout_candidates.py", config_path])
    run_step(f"4/5 锁定候选 {args.candidate}", [sys.executable, "scripts/lock_layout.py", config_path, args.candidate, locked_path])
    run_step("5/5 生成完整交付包", [sys.executable, "scripts/run.py", locked_path])

    print("\n✅ 一键流程完成", flush=True)
    print(f"交付首页: {out_dir / '交付说明.html'}", flush=True)
    print(f"版式候选: {out_dir / 'layout_candidates/index.html'}", flush=True)
    print(f"材质预览: {out_dir / 'preview/materials.html'}", flush=True)
    print(f"交付 ZIP: {out_dir / (args.theme + '_交付包.zip')}", flush=True)
    print("建议先打开交付首页，再检查 QC WARN/FAIL。", flush=True)


if __name__ == "__main__":
    main()
