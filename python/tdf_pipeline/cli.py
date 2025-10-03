import argparse import json from .requirements_parser import parse_requirements from .cpp_analyzer import analyze_cpp from .tdf_parser import parse_tdf from .mapping import map_testids from .context_builder import build_context from .llm_orchestrator import propose_update from .merger import apply_updates from .reporter import generate_report_md from .orchestrator import orchestrate

def main(): ap = argparse.ArgumentParser(description="TDF pipeline CLI (skeleton)") sub = ap.add_subparsers(dest="cmd", required=True)

s1 = sub.add_parser("parse-requirements-csv")
s1.add_argument("--csv", required=True)
s1.add_argument("--mapping")
s1.add_argument("--out")

s2 = sub.add_parser("analyze-cpp-source")
s2.add_argument("--src", required=True)
s2.add_argument("--idsJson")
s2.add_argument("--include")
s2.add_argument("--exclude")
s2.add_argument("--out")

s3 = sub.add_parser("parse-tdf")
s3.add_argument("--tdf", required=True)
s3.add_argument("--out")

s4 = sub.add_parser("map-testids-to-requirements")
s4.add_argument("--parsedTdf", required=True)
s4.add_argument("--requirements", required=True)
s4.add_argument("--codeIndex")
s4.add_argument("--out")

s5 = sub.add_parser("build-context-for-testid")
s5.add_argument("--testId", required=True)
s5.add_argument("--mapping", required=True)
s5.add_argument("--requirements", required=True)
s5.add_argument("--codeIndex")
s5.add_argument("--k", type=int, default=3)
s5.add_argument("--out")

s6 = sub.add_parser("propose-update-for-testid")
s6.add_argument("--testId", required=True)
s6.add_argument("--context", required=True)
s6.add_argument("--llmConfig")
s6.add_argument("--out")
s6.add_argument("--noLlm", action="store_true")

s7 = sub.add_parser("apply-updates-to-tdf")
s7.add_argument("--tdf", required=True)
s7.add_argument("--parsedTdf", required=True)
s7.add_argument("--proposalsDir", required=True)
s7.add_argument("--outTdf", required=True)
s7.add_argument("--diffsOut")
s7.add_argument("--backup", action="store_true")

s8 = sub.add_parser("generate-report")
s8.add_argument("--proposalsDir", required=True)
s8.add_argument("--diffs", required=True)
s8.add_argument("--mapping")
s8.add_argument("--out", required=True)

s9 = sub.add_parser("orchestrate-update-all")
s9.add_argument("--csv", required=True)
s9.add_argument("--src", required=True)
s9.add_argument("--tdf", required=True)
s9.add_argument("--outTdf", required=True)
s9.add_argument("--report", required=True)
s9.add_argument("--mappingCfg")
s9.add_argument("--k", type=int, default=3)
s9.add_argument("--llmConfig")
s9.add_argument("--noLlm", action="store_true")
s9.add_argument("--backup", action="store_true")

args = ap.parse_args()

if args.cmd == "parse-requirements-csv":
    out = parse_requirements(args.csv, args.mapping, args.out)
    print(out)
elif args.cmd == "analyze-cpp-source":
    out = analyze_cpp(args.src, args.idsJson, args.include, args.exclude, args.out)
    print(out)
elif args.cmd == "parse-tdf":
    out = parse_tdf(args.tdf, args.out)
    print(out)
elif args.cmd == "map-testids-to-requirements":
    out = map_testids(args.parsedTdf, args.requirements, args.codeIndex, args.out)
    print(out)
elif args.cmd == "build-context-for-testid":
    out = build_context(args.testId, args.mapping, args.requirements, args.codeIndex, args.k, args.out)
    print(out)
elif args.cmd == "propose-update-for-testid":
    out = propose_update(args.testId, args.context, args.llmConfig, no_llm=args.noLlm, out_path=args.out)
    print(out)
elif args.cmd == "apply-updates-to-tdf":
    out_tdf, diffs = apply_updates(args.tdf, args.parsedTdf, args.proposalsDir, args.outTdf, args.diffsOut, args.backup)
    print(json.dumps({"updatedTdf": out_tdf, "diffs": diffs}, indent=2))
elif args.cmd == "generate-report":
    out = generate_report_md(args.proposalsDir, args.diffs, args.mapping, args.out)
    print(out)
elif args.cmd == "orchestrate-update-all":
    res = orchestrate(args.csv, args.src, args.tdf, args.outTdf, args.report, args.mappingCfg, args.llmConfig, args.k, args.noLlm, args.backup)
    print(json.dumps(res, indent=2))
else:
    raise SystemExit("Unknown command")

if name == "main": main()

