python import os import json import time from typing import Dict, Any, Optional import urllib.request

def _openai_like_request(base_url: str, model: str, messages: list, temperature: float = 0.2, max_tokens: int = 800, json_mode: bool = True, timeout: int = 120, api_key: Optional[str] = None) -> str: url = base_url.rstrip("/") + "/chat/completions" payload = { "model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens } if json_mode: payload["response_format"] = {"type": "json_object"} data = json.dumps(payload).encode("utf-8") req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}) if api_key: req.add_header("Authorization", f"Bearer {api_key}") with urllib.request.urlopen(req, timeout=timeout) as resp: body = resp.read().decode("utf-8") j = json.loads(body) return j["choices"][0]["message"]["content"]

def propose_update(test_id: str, context_json_path: str, llm_config_path: Optional[str], no_llm: bool = False, out_path: Optional[str] = None) -> str: ctx = json.loads(open(context_json_path, "r", encoding="utf-8").read()) requirement = ctx.get("requirement", {}) rid = requirement.get("id", "") # Placeholder "current block body" not included; the LLM can propose a new body based on requirement + code snippets.

if no_llm:
    proposal = {
        "testId": test_id,
        "updatedBody": f"# Auto-generated placeholder for {test_id} mapped to {rid}\n# Replace this with steps reflecting requirement and code.\n",
        "confidence": 0.3,
        "rationale": "No-LLM mode placeholder."
    }
else:
    cfg = {}
    if llm_config_path and os.path.exists(llm_config_path):
        cfg = json.loads(open(llm_config_path, "r", encoding="utf-8").read())
    base_url = cfg.get("baseUrl") or os.environ.get("LLM_BASE_URL")
    model = cfg.get("model") or os.environ.get("LLM_MODEL") or "local-model"
    temperature = float(cfg.get("temperature", 0.2))
    max_tokens = int(cfg.get("maxOutputTokens", 800))
    json_mode = bool(cfg.get("jsonOutput", True))
    timeout = int(cfg.get("timeoutSec", 120))
    api_key = os.environ.get("LLM_API_KEY")

    system = {
        "role": "system",
        "content": "You update test case bodies to align with the requirement and code snippets. Keep TESTID and comments intact. Output JSON with fields: updatedBody, confidence (0..1), rationale."
    }
    user = {
        "role": "user",
        "content": json.dumps({
            "testId": test_id,
            "requirement": {"id": rid, "title": requirement.get("title"), "text": requirement.get("text")},
            "codeSnippets": ctx.get("codeSnippets", []),
            "constraints": ctx.get("constraints", {})
        }, ensure_ascii=False)
    }
    try:
        content = _openai_like_request(base_url, model, [system, user], temperature, max_tokens, json_mode, timeout, api_key)
        parsed = json.loads(content)
        proposal = {
            "testId": test_id,
            "updatedBody": parsed.get("updatedBody", ""),
            "confidence": float(parsed.get("confidence", 0.5)),
            "rationale": parsed.get("rationale", "")
        }
    except Exception as e:
        # Fallback to placeholder on error
        proposal = {
            "testId": test_id,
            "updatedBody": f"# Fallback placeholder for {test_id} (error)\n",
            "confidence": 0.2,
            "rationale": f"LLM error: {e}"
        }

out = out_path or f"artifacts/proposals/TESTID_{test_id}.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(json.dumps(proposal, indent=2, ensure_ascii=False))
return out

