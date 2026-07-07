from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence import scan_evidence
from .runs import load_run, utc_now


def _table(items: list[dict[str, Any]]) -> list[str]:
    lines = ["| Path | Kind | Size | SHA-256 |", "|---|---:|---:|---|"]
    for item in items:
        digest = item["sha256"] or "not hashed"
        lines.append(f"| `{item['path']}` | {item['kind']} | {item['size_bytes']} | `{digest}` |")
    return lines


def generate_report(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    run = load_run(root)
    evidence = scan_evidence(root, write=True)

    lines = [
        f"# Simulation Run Report: {run['run_id']}",
        "",
        "## Run Metadata",
        "",
        f"- Solver: `{run['solver']}`",
        f"- Case: `{run['case_name']}`",
        f"- Created at: `{run['created_at']}`",
        f"- Report generated at: `{utc_now()}`",
        f"- Objective: {run.get('objective') or 'not provided'}",
        f"- Status: `{run.get('status', 'created')}`",
        "",
        "## Credibility Grade",
        "",
        f"`{evidence['credibility_grade']}`",
        "",
        "## Evidence Summary",
        "",
    ]

    if evidence["counts"]:
        for kind, count in sorted(evidence["counts"].items()):
            lines.append(f"- {kind}: {count}")
    else:
        lines.append("- No evidence files found.")

    lines.extend(["", "## Missing Items For Stronger Evidence", ""])
    if evidence["missing_for_next_grade"]:
        for item in evidence["missing_for_next_grade"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Evidence Inventory", ""])
    lines.extend(_table(evidence["items"]))
    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Confirm solver version, license state, and command line before treating this as engineering evidence.",
            "- Do not publish private model files, licensed manuals, credentials, or large raw solver outputs.",
            "- Promote the run only after logs, exported numeric data, visual checks, and report notes agree.",
            "",
        ]
    )

    report_path = root / "report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "run_id": run["run_id"],
        "run_dir": str(root),
        "report_path": str(report_path),
        "credibility_grade": evidence["credibility_grade"],
    }
