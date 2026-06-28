#!/usr/bin/env python3
"""Interactive project starter for Print Studio OpenDesign.

Creates a runnable config without asking users to edit JSON by hand.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PRESETS = json.loads((HERE / "assets/calendar_series/presets.json").read_text(encoding="utf-8"))

PRODUCTS = {
    "1": ("calendar_card", "monthly_calendar", "calendar_series", "desk_cal_5x7", "single_card", "12"),
    "2": ("greeting_card", "custom_cards", "generic_card", "greeting_5x7", "single_card", "1"),
    "3": ("postcard", "custom_cards", "generic_card", "postcard_7x5", "postcard", "6"),
    "4": ("bookmark", "custom_cards", "generic_card", "bookmark_2x6", "single_card", "4"),
    "5": ("gift_tag", "custom_cards", "generic_card", "gift_tag_2x3_5", "single_card", "8"),
    "6": ("wall_calendar", "monthly_calendar", "calendar_series", "wall_cal_8x12", "wall_coil", "12"),
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


def choose_material():
    materials = PRESETS["materials"]
    print("\n材质推荐：")
    choices = {}
    for idx, key in enumerate(MATERIAL_SHORTLIST, start=1):
        item = materials[key]
        choices[str(idx)] = key
        print(f"{idx}. {item['label']} —— {item.get('use_case', '')}")
    print("也可以直接输入 presets.json 里的材质 key，例如 pvc_30c / blue_core_300g")
    raw = ask("请选择材质", "1")
    material = choices.get(raw, raw)
    if material not in materials:
        valid = ", ".join(MATERIAL_SHORTLIST)
        raise SystemExit(f"材质不存在: {material}\n可选示例: {valid}")
    return material


def main():
    print("Print Studio OpenDesign · 项目向导")
    print("把图片放到一个文件夹里，文件名建议数字开头：01.jpg, 02.jpg ...")
    image_dir = ask("图片文件夹路径")
    if not image_dir:
        raise SystemExit("需要图片文件夹路径")
    image_dir = str(Path(image_dir).expanduser().resolve())
    if not Path(image_dir).exists():
        raise SystemExit(f"图片文件夹不存在: {image_dir}")

    theme = ask("项目名称", Path(image_dir).name)
    print("\n产品类型：1 月历卡  2 贺卡  3 明信片  4 书签  5 吊牌  6 挂历")
    product_choice = ask("请选择", "1")
    product_type, series_type, template, size_key, product_form, default_count = PRODUCTS.get(product_choice, PRODUCTS["1"])
    count = int(ask("系列张数", default_count))

    material = choose_material()
    year = int(ask("年份", "2027"))
    out_name = ask("输出配置文件名", f"{theme}.config.json")

    base = json.loads((HERE / "config.example.json").read_text(encoding="utf-8"))
    base["theme"] = theme
    base["illustrations_dir"] = image_dir
    base["job"]["job_name"] = theme
    base["series"].update({"type": series_type, "count": count, "template": template})
    base["preset"].update({
        "product_type": product_type,
        "size": size_key,
        "material": material,
        "product_form": product_form,
    })
    base["content"]["year"] = year
    base["content"]["real_dates"] = template == "calendar_series"
    if product_type == "wall_calendar":
        base["production"]["binding"] = "top_wire"
        base["production"]["binding_reserved_mm"] = 12
        base["production"]["finishing"] = ["top_wire"]
    base["outputs"]["download_4k"] = True
    base["image_gen"]["backend"] = "local_mockup"

    out_path = Path(out_name).expanduser()
    if not out_path.is_absolute():
        out_path = HERE / out_path
    out_path.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
    locked_path = out_path.with_name(f"{out_path.stem}.locked-B.json")
    print(f"\n已生成配置: {out_path}")
    print("\n下一步建议：")
    print(f"1. python scripts/preview_config.py {out_path} --all-materials")
    print(f"2. python scripts/generate_layout_candidates.py {out_path}")
    print(f"3. python scripts/lock_layout.py {out_path} B {locked_path}")
    print(f"4. python scripts/run.py {locked_path}")


if __name__ == "__main__":
    main()
