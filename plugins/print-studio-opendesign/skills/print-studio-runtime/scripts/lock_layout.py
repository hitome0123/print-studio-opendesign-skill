#!/usr/bin/env python3
"""Lock a selected layout candidate back into a job config."""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HERE / "output"


def absolutize_illustrations_dir(cfg, config_path):
    illustrations = Path(cfg.get("illustrations_dir", "example_illustrations")).expanduser()
    if illustrations.is_absolute():
        return
    local_candidate = (config_path.parent / illustrations).resolve()
    bundled_candidate = (HERE / illustrations).resolve()
    cfg["illustrations_dir"] = str(local_candidate if local_candidate.exists() else bundled_candidate)


def main():
    if len(sys.argv) < 3:
        raise SystemExit("用法: python scripts/lock_layout.py <config.json> <candidate_id> [out_config.json]")
    config_path = Path(sys.argv[1])
    candidate_id = sys.argv[2].upper()
    out_config = Path(sys.argv[3]) if len(sys.argv) >= 4 else config_path.with_name(config_path.stem + f".locked-{candidate_id}.json")

    config_path = config_path.expanduser().resolve()
    out_config = out_config.expanduser().resolve()
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    theme = cfg.get("theme")
    candidates_path = OUTPUT_ROOT / theme / "layout_candidates" / "layout_candidates.json"
    if not candidates_path.exists():
        raise SystemExit(f"找不到候选文件: {candidates_path}\n请先运行 scripts/generate_layout_candidates.py {config_path}")
    payload = json.loads(candidates_path.read_text(encoding="utf-8"))
    match = next((item for item in payload.get("candidates", []) if item.get("candidate_id") == candidate_id), None)
    if not match:
        raise SystemExit(f"候选 {candidate_id} 不存在，可选: " + ", ".join(item.get("candidate_id", "?") for item in payload.get("candidates", [])))

    cfg["layout_lock"] = match["locked_layout"]
    cfg["ai_layout"] = False
    absolutize_illustrations_dir(cfg, config_path)
    if out_config != config_path:
        shutil.copy2(config_path, config_path.with_suffix(config_path.suffix + ".bak"))
    out_config.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"locked {candidate_id} -> {out_config}")
    print(match["name"] + "：" + match["reason"])


if __name__ == "__main__":
    main()
