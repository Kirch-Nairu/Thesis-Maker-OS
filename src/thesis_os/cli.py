from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .audit import audit_manuscript
from .gates import validate_research_model
from .ingest import extract_text
from .models import load_research_model
from .report import render_markdown
from .workspace import bootstrap_workspace


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    created = bootstrap_workspace(args.path)
    print(f"Workspace ready: {Path(args.path).resolve()}")
    print(f"Created {len(created)} paths")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    model = load_research_model(args.model)
    gates = validate_research_model(model)
    print(json.dumps({"gates": [gate.to_dict() for gate in gates]}, indent=2))
    return 2 if any(gate.status == "BLOCK" for gate in gates) else 0


def _cmd_audit(args: argparse.Namespace) -> int:
    text = extract_text(args.manuscript)
    audit = audit_manuscript(text)
    gates = None
    if args.model:
        model = load_research_model(args.model)
        gates = validate_research_model(model)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "audit.json"
    report_path = out_dir / "REVIEW.md"

    payload = dict(audit)
    if gates is not None:
        payload["research_model_gates"] = [gate.to_dict() for gate in gates]
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_markdown(audit, gates), encoding="utf-8")

    blocking = audit["summary"]["blocking"]
    if gates:
        blocking += sum(g.status == "BLOCK" for g in gates)
    print(f"Audit written: {report_path}")
    print(f"Machine report: {json_path}")
    return 2 if blocking else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="thesis-os")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap", help="Create a governed thesis workspace")
    bootstrap.add_argument("path")
    bootstrap.set_defaults(func=_cmd_bootstrap)

    validate = sub.add_parser("validate", help="Validate a research_model.json")
    validate.add_argument("model")
    validate.set_defaults(func=_cmd_validate)

    audit = sub.add_parser("audit", help="Audit a manuscript")
    audit.add_argument("manuscript")
    audit.add_argument("--model", help="Optional research_model.json")
    audit.add_argument("--out", default=".audit", help="Output directory")
    audit.set_defaults(func=_cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
