python import re import json from pathlib import Path from typing import List, Dict, Any

Blocks begin with lines like: TESTID:
BLOCK_START = re.compile(r'^(TESTID)\s:\s(?P[^\r\n#]+)\s*$', re.IGNORECASE) COMMENT_PREFIX = "#"

def parse_tdf(tdf_path: str, out_path: str | None) -> str: p = Path(tdf_path) if not p.exists(): raise FileNotFoundError(f"TDF not found: {tdf_path}") raw = p.read_text(encoding="utf-8", errors="ignore")

lines = raw.splitlines(keepends=True)
blocks: List[Dict[str, Any]] = []
i = 0
current = None

while i < len(lines):
    line = lines[i]
    m = BLOCK_START.match(line.strip("\r\n"))
    if m:
        # close existing
        if current:
            current["end_line"] = i
            blocks.append(current)
        # start new
        tid = m.group("id").strip()
        current = {
            "testid": tid,
            "start_line": i,
            "end_line": None,
            "header_line": line,
            "body_lines": []
        }
    else:
        if current:
            current["body_lines"].append(line)
    i += 1

if current:
    current["end_line"] = len(lines)
    blocks.append(current)

parsed = {
    "path": str(p),
    "line_ending": "\r\n" if "\r\n" in raw else "\n",
    "blocks": blocks,
    "non_block_prefix": [] if (blocks and blocks[0]["start_line"] == 0) else lines[: blocks[0]["start_line"]] if blocks else lines
}

out = out_path or str(Path("artifacts/cache/tdf_parsed.json"))
Path(out).parent.mkdir(parents=True, exist_ok=True)
Path(out).write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
return out

def reconstruct_from_parsed(parsed_json_path: str, updated_blocks: Dict[str, Dict[str, Any]]) -> str: parsed = json.loads(Path(parsed_json_path).read_text(encoding="utf-8")) # Rebuild preserving original order/whitespace except for updated bodies out_lines: List[str] = [] prefix = parsed.get("non_block_prefix") or [] if prefix: out_lines.extend(prefix)

for b in parsed["blocks"]:
    tid = b["testid"]
    out_lines.append(b["header_line"])
    # Body: preserve comments; replace non-comment lines with proposed content if available
    proposed = updated_blocks.get(tid, {}).get("body", None)
    if proposed is None:
        out_lines.extend(b["body_lines"])
    else:
        # preserve comment lines from original
        preserved_comments = [ln for ln in b["body_lines"] if ln.lstrip().startswith(COMMENT_PREFIX)]
        # normalize proposed to have original line endings
        eol = parsed.get("line_ending", "\n")
        proposed_lines = [ln if ln.endswith("\n") or ln.endswith("\r\n") else (ln + eol) for ln in proposed.splitlines()]
        # Merge: comments first in their original positions if possible, then proposed
        # Simple approach: output preserved comments, then proposed body
        out_lines.extend(preserved_comments + proposed_lines)

return "".join(out_lines)

