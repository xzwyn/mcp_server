import re import json from pathlib import Path from typing import Dict, Any, List, Optional

FUNC_RE = re.compile(r'^\s(?:[\w:<>,~*\&\s]+)\s+([A-Za-z_]\w)\s([^;])\s{?', re.MULTILINE) 
CLASS_RE = re.compile(r'^\sclass\s+([A-Za-z_]\w)', re.MULTILINE) 
COMMENT_RE = re.compile(r'//.?$|/*[\s\S]*?*/', re.MULTILINE)

def analyze_cpp(src_root: str, ids_json_path: Optional[str], include_glob: Optional[str], exclude_glob: Optional[str], out_path: Optional[str]) -> str: 
    root = Path(src_root) 
    if not root.exists(): raise FileNotFoundError(f"src root not found: {src_root}")

id_set = set()
if ids_json_path and Path(ids_json_path).exists():
    j = json.loads(Path(ids_json_path).read_text(encoding="utf-8"))
    for r in j.get("requirements", []):
        rid = r.get("id")
        if rid:
            id_set.add(rid)

files = list(root.rglob("*.cpp")) + list(root.rglob("*.hpp")) + list(root.rglob("*.h")) + list(root.rglob("*.cc"))
# simplistic include/exclude handling
if include_glob:
    from fnmatch import fnmatch
    files = [p for p in files if fnmatch(str(p), include_glob)]
if exclude_glob:
    from fnmatch import fnmatch
    files = [p for p in files if not fnmatch(str(p), exclude_glob)]

symbols: List[Dict[str, Any]] = []
for p in files:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    # extract comments and IDs
    comments = COMMENT_RE.findall(txt) or []
    tags = []
    for c in comments:
        # match exact IDs in id_set
        for rid in id_set:
            if rid in c:
                tags.append({"id": rid, "snippet": c.strip()[:200]})
    # extract symbols
    funcs = FUNC_RE.findall(txt)
    classes = CLASS_RE.findall(txt)
    for name in funcs:
        symbols.append({"kind": "function", "name": name, "file": str(p), "tags": tags})
    for name in classes:
        symbols.append({"kind": "class", "name": name, "file": str(p), "tags": tags})

# simple summaries: name + file + first comment if any
index = {
    "files": [str(p) for p in files],
    "symbols": symbols
}

out_file = out_path or str(Path("artifacts/cache/code_index.json"))
Path(out_file).parent.mkdir(parents=True, exist_ok=True)
Path(out_file).write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
return out_file

