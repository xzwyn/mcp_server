#!/usr/bin/env node
// Minimal MCP stdio server exposing granular tools that spawn Python CLI.

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import path from "node:path";
import { spawnCli } from "./src/util/processSpawner.js";

// Resolve Python CLI path
const ROOT = path.resolve(path.join(import.meta.url.replace("file:///", "/"), "../../")).replace(/\/mcp-server$/, "");
const PYTHON_CLI = path.join(ROOT, "python", "tdf_pipeline", "cli.py");

// Helper to define a tool that calls the Python CLI with a subcommand
function toolDef(name, description, inputSchema, subcommand) {
  return {
    def: { name, description, inputSchema },
    handler: async (args) => {
      const cliArgs = [subcommand, ...Object.entries(args || {}).flatMap(([k, v]) => {
        if (v === undefined || v === null || v === "") return [];
        if (typeof v === "boolean") return v ? [`--${k}`] : [];
        return [`--${k}`, String(v)];
      })];
      return await spawnCli(PYTHON_CLI, cliArgs);
    }
  };
}

const transport = new StdioServerTransport();
const server = new Server({
  name: "tdf-updater",
  version: "0.1.0",
  description: "Local MCP server for TDF updates (skeleton)",
  transport
});

// Register granular tools
const tools = [
  toolDef("parse_requirements_csv", "Parse requirements CSV into normalized JSON", {
    type: "object",
    properties: {
      csv: { type: "string" },
      mapping: { type: "string" },
      out: { type: "string" }
    },
    required: ["csv"],
    additionalProperties: false
  }, "parse-requirements-csv"),

  toolDef("analyze_cpp_source", "Analyze C++ source files", {
    type: "object",
    properties: {
      src: { type: "string" },
      idsJson: { type: "string" },
      include: { type: "string" },
      exclude: { type: "string" },
      out: { type: "string" }
    },
    required: ["src"],
    additionalProperties: false
  }, "analyze-cpp-source"),

  toolDef("parse_tdf", "Parse .tdf preserving formatting", {
    type: "object",
    properties: {
      tdf: { type: "string" },
      out: { type: "string" }
    },
    required: ["tdf"],
    additionalProperties: false
  }, "parse-tdf"),

  toolDef("map_testids_to_requirements", "Map TESTIDs to requirements", {
    type: "object",
    properties: {
      parsedTdf: { type: "string" },
      requirements: { type: "string" },
      codeIndex: { type: "string" },
      out: { type: "string" }
    },
    required: ["parsedTdf", "requirements"],
    additionalProperties: false
  }, "map-testids-to-requirements"),

  toolDef("build_context_for_testid", "Build context bundle for a TESTID", {
    type: "object",
    properties: {
      testId: { type: "string" },
      mapping: { type: "string" },
      requirements: { type: "string" },
      codeIndex: { type: "string" },
      k: { type: "number" },
      out: { type: "string" }
    },
    required: ["testId", "mapping", "requirements"],
    additionalProperties: false
  }, "build-context-for-testid"),

  toolDef("propose_update_for_testid", "Use local LLM to propose update", {
    type: "object",
    properties: {
      testId: { type: "string" },
      context: { type: "string" },
      llmConfig: { type: "string" },
      out: { type: "string" },
      noLlm: { type: "boolean" }
    },
    required: ["testId", "context"],
    additionalProperties: false
  }, "propose-update-for-testid"),

  toolDef("apply_updates_to_tdf", "Merge proposals and write updated .tdf", {
    type: "object",
    properties: {
      tdf: { type: "string" },
      parsedTdf: { type: "string" },
      proposalsDir: { type: "string" },
      outTdf: { type: "string" },
      diffsOut: { type: "string" },
      backup: { type: "boolean" }
    },
    required: ["tdf", "parsedTdf", "proposalsDir", "outTdf"],
    additionalProperties: false
  }, "apply-updates-to-tdf"),

  toolDef("generate_report", "Generate Markdown report of changes", {
    type: "object",
    properties: {
      proposalsDir: { type: "string" },
      diffs: { type: "string" },
      mapping: { type: "string" },
      out: { type: "string" }
    },
    required: ["proposalsDir", "diffs", "out"],
    additionalProperties: false
  }, "generate-report"),

  toolDef("orchestrate_update_all", "Run full pipeline end-to-end", {
    type: "object",
    properties: {
      csv: { type: "string" },
      src: { type: "string" },
      tdf: { type: "string" },
      outTdf: { type: "string" },
      report: { type: "string" },
      mappingCfg: { type: "string" },
      k: { type: "number" },
      llmConfig: { type: "string" },
      noLlm: { type: "boolean" },
      backup: { type: "boolean" }
    },
    required: ["csv", "src", "tdf", "outTdf", "report"],
    additionalProperties: false
  }, "orchestrate-update-all")
];

for (const t of tools) server.addTool(t.def, t.handler);

await server.start();
