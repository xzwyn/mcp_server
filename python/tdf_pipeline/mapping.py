import json import re from pathlib import Path from typing import Dict, Any, List

def map_testids(parsed_tdf_path: str, requirements_json_path: str, code_index_path: str | None, out_path: str | None) -> str: parsed = json.loads(Path(parsed_tdf_path).read_text(encoding="utf-8")) reqs_data = json.loads(Path(requirements_json_path).read_text(encoding="utf-8")) id_list = [r["id"] for r in reqs_data.get("requirements", [])] id_set = set(id_list)

mapping: Dict[str, Dict[str, Any]] = {}
# naive scan for IDs in each block body
for b in parsed.get("blocks", []):
    tid = b["testid"]
    body_txt = "".join(b.get("body_lines", []))
    chosen = None
    # direct reference
    for rid in id_list:
        if rid in body_txt:
            chosen = rid
            break
    # fallback: first requirement
    if not chosen and id_list:
        chosen = id_list[0]
    mapping[tid] = {
        "requirement": chosen,
        "confidence": 0.5 if chosen else 0.0,
        "evidence": []
    }

out = out_path or str(Path("artifacts/mapping/mapping.json"))
Path(out).parent.mkdir(parents=True, exist_ok=True)
Path(out).write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
return out

