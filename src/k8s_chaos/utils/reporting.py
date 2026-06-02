"""Write chaos and GameDay reports to disk."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def write_report(report: Dict[str, Any], output_dir: Path, basename: str = "latest") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    latest = output_dir / f"{basename}.json"
    ts = report.get("timestamp", datetime.now(timezone.utc).isoformat())
    stamped = output_dir / f"{basename}-{ts.replace(':', '-')}.json"
    payload = json.dumps(report, indent=2)
    latest.write_text(payload, encoding="utf-8")
    stamped.write_text(payload, encoding="utf-8")
    return latest


def print_experiment_summary(report: Dict[str, Any], report_path: Path) -> None:
    print("")
    print("=" * 50)
    print("  Chaos Experiment Report (SLO)")
    print("=" * 50)
    print(f"  Experiment:  {report.get('experiment')}")
    if report.get("hypothesis"):
        print(f"  Hypothesis:  {report['hypothesis']}")
    print(f"  Replicas:    recovery {report.get('recovery_seconds')}s")
    print(f"  Verdict:     {report.get('verdict')}")
    for probe in report.get("probes", []):
        print(f"    - [{probe['verdict']}] {probe['name']}: {probe['message']}")
    print(f"  Report:      {report_path}")
    print("=" * 50)
    print("")


def print_gameday_summary(report: Dict[str, Any], report_path: Path) -> None:
    print("")
    print("=" * 50)
    print(f"  GameDay Report: {report.get('gameday')}")
    print("=" * 50)
    for step in report.get("steps", []):
        print(f"  [{step.get('verdict', '?')}] {step.get('id')}: {step.get('description', '')}")
    print(f"  Overall:     {report.get('verdict')}")
    print(f"  Report:      {report_path}")
    print("=" * 50)
    print("")
