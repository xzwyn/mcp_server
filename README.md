# Local MCP TDF Updater (Skeleton)

Overview
- Local-only, free MCP server and Python pipeline to:
  - Parse requirements CSV (you supply mapping).
  - Analyze C++ source for explicit tags and lexical relevance.
  - Parse legacy .tdf in a round-trip fashion preserving formatting.
  - Use a local LLM (your API) to propose updates per TESTID.
  - Merge updates into a fully rewritten .tdf.
  - Generate a Markdown report.

Quick start (Windows)
1) Python env:
   - Create venv:
     - py -3.11 -m venv .venv
     - .\.venv\Scripts\activate
   - Install requirements:
     - pip install -r python\requirements.txt

2) Node MCP server:
   - cd mcp-server
   - npm install
   - Launch (for manual test): node mcp-tdf-server.mjs
   - Typically your VS Code MCP client launches this file.

3) Orchestrate (manual, without MCP):
   - .\.venv\Scripts\python.exe python\tdf_pipeline\cli.py orchestrate-update-all ^
       --csv testdata\requirements.csv ^
       --src testdata\src ^
       --tdf testdata\sample.tdf ^
       --out-tdf artifacts\outputs\updated.tdf ^
       --report artifacts\reports\update_report.md

Artifacts
- artifacts\cache: cached parsed CSV, code index, parsed TDF
- artifacts\mapping: TESTID → requirement mapping JSON
- artifacts\contexts: per-TESTID context bundles
- artifacts\proposals: per-TESTID LLM proposals
- artifacts\diffs: diffs for updated fields/regions
- artifacts\outputs: updated.tdf and a backup of the original

Notes
- Wire your local LLM endpoint in python\tdf_pipeline\llm_orchestrator.py (OpenAI-compatible stub included).
- TDF parsing anchors on lines beginning: "TESTID:"; comments (# ...) are preserved.
- Field names are not required; this skeleton replaces the editable body within each TESTID block while preserving the header and comments.
