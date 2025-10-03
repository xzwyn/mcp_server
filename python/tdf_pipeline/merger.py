python import json from pathlib import Path from typing import Dict, Any, Tuple from .tdf_parser import reconstruct_from_parsed

def apply_updates(tdf_path: str, parsed_tdf_json_path: str, proposals_dir: str, out_tdf_path: str, diffs_out_path: str | None, backup: bool) -> Tuple[str, str | None]: parsed = json.loads(Path(parsed_tdf_json_path).read_text(encoding="utf-8")) # Load proposals proposals: Dict[str, Dict[str, Any]] = {} for b in parsed.get("blocks", []): tid = b["testid"] prop_file = Path(proposals_dir) / f"TESTID_{tid}.json" if prop_file.exists(): proposals[tid] = json.loads(prop_file.read_text(encoding="utf-8")) # Build updated bodies map updated_bodies: Dict[str, Dict[str, Any]] = {} diffs: Dict[str, Dict[str, Any]] = {} for b in parsed.get("blocks", []): tid = b["testid"] orig_body = "".join(b.get("body_lines", [])) updated = proposals.get(tid, {}).get("updatedBody") if updated is not None and updated != "": updated_bodies[tid] = {"body": updated} diffs[tid] = { "changed": True, "before": orig_body[:1000], "after": (updated[:1000] if isinstance(updated, str) else str(updated)) } else: diffs[tid] = {"changed": False}

new_text = reconstruct_from_parsed(parsed_tdf_json_path, updated_bodies)

outp = Path(out_tdf_path)
outp.parent.mkdir(parents=True, exist_ok=True)

if backup:
    bak = Path(out_tdf_path + ".bak")
    if Path(tdf_path).exists():
        bak.write_text(Path(tdf_path).read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

outp.write_text(new_text, encoding="utf-8")

diffs_path = None
if diffs_out_path:
    diffs_path = diffs_out_path
    Path(diffs_path).parent.mkdir(parents=True, exist_ok=True)
    Path(diffs_path).write_text(json.dumps(diffs, indent=2, ensure_ascii=False), encoding="utf-8")

return str(outp), diffs_path

