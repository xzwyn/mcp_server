import json from pathlib import Path from typing import Dict, Any, List

def generate_report_md(proposals_dir: str, diffs_path: str | None, mapping_path: str | None, out_md_path: str) -> str: props = [] pdir = Path(proposals_dir) if pdir.exists(): for f in sorted(pdir.glob("TESTID_*.json")): props.append(json.loads(f.read_text(encoding="utf-8"))) diffs = {} if diffs_path and Path(diffs_path).exists(): diffs = json.loads(Path(diffs_path).read_text(encoding="utf-8")) mapping = {} if mapping_path and Path(mapping_path).exists(): mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))

lines: List[str] = []
lines.append("# TDF Update Report\n\n")
lines.append(f"- Proposals: {len(props)}\n")
lines.append(f"- Diffs available: {'yes' if diffs else 'no'}\n\n")

for pr in props:
    tid = pr.get("testId")
    rid = mapping.get(tid, {}).get("requirement") if mapping else None
    lines.append(f"## TESTID: {tid}\n\n")
    if rid:
        lines.append(f"- Requirement: {rid}\n")
    lines.append(f"- Confidence: {pr.get('confidence')}\n")
    lines.append(f"- Rationale: {pr.get('rationale')}\n\n")
    if tid in diffs and diffs[tid].get("changed"):
        lines.append("### Diff (truncated)\n")
        lines.append("Before:\n")
        lines.append("```\n")
        lines.append((diffs[tid].get("before") or "") + "\n")
        lines.append("```\n")
        lines.append("After:\n")
        lines.append("```\n")
        lines.append((diffs[tid].get("after") or "") + "\n")
        lines.append("```\n")
    else:
        lines.append("_No change_\n\n")

outp = Path(out_md_path)
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text("".join(lines), encoding="utf-8")
return str(outp)

