#!/usr/bin/env python3
"""Run the bundled print-studio calendar-series engine from a skill config."""
import json
import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = SKILL_ROOT / "assets" / "calendar_series"


def _prepare_config(config_path: Path) -> Path:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    illustrations = Path(cfg.get("illustrations_dir", "example_illustrations"))
    if not illustrations.is_absolute():
        local_candidate = (config_path.parent / illustrations).resolve()
        bundled_candidate = (ENGINE_ROOT / illustrations).resolve()
        if local_candidate.exists():
            cfg["illustrations_dir"] = str(local_candidate)
        elif bundled_candidate.exists():
            cfg["illustrations_dir"] = str(bundled_candidate)
        else:
            cfg["illustrations_dir"] = str(local_candidate)
    tmp_dir = SKILL_ROOT / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    prepared = tmp_dir / "resolved_config.json"
    prepared.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return prepared


def main():
    config_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SKILL_ROOT / "config.example.json"
    prepared = _prepare_config(config_path)
    os.environ["PRINT_STUDIO_OUTPUT_ROOT"] = str(SKILL_ROOT / "output")
    sys.path.insert(0, str(ENGINE_ROOT))
    sys.argv = [str(ENGINE_ROOT / "run.py"), str(prepared)]
    namespace = {"__name__": "__main__", "__file__": str(ENGINE_ROOT / "run.py")}
    exec((ENGINE_ROOT / "run.py").read_text(encoding="utf-8"), namespace)


if __name__ == "__main__":
    main()
