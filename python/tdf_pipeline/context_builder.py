python import json from pathlib import Path from typing import Dict, Any from .retrieval import top_k_snippets

def build_context(test_id: str, mapping_json_path: str, requirements_json_path: str, code_index_path: str | None, k: int, out_path: str | None) -> str: mapping = json.loads(Path(mapping_json_path).read_text(encoding="utf-8")) reqs = json.loads(Path(requirements_json_path).read_text(encoding="utf-8"))

rid = mapping.get(test_id, {}).get("requirement")
req = next((r for r in reqs.get("requirements", []) if r.get("id") == rid), None)
# current block body must be supplied by caller if needed; for simplicity, context contains only requirement + code
snippets = top_k_snippets(rid, code_index_path, k or 3)

bundle: Dict[str, Any] = {
    "testId": test_id,
    "requirement": req or {"id": rid, "title": "", "text": ""},
    "codeSnippets": snippets,
    "constraints": {
        "immutables": ["TESTID", "comments", "fieldOrder", "indentation", "blankLines", "trailingWhitespace"],
        "replaceMode": "block-body"
    }
}
out = out_path or str(Path(f"artifacts/contexts/TESTID_{test_id}.json"))
Path(out).parent.mkdir(parents=True, exist_ok=True)
Path(out).write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
return out

