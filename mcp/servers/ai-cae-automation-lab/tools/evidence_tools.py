from __future__ import annotations

from typing import Any

from ai_cae_lab.evidence import scan_evidence
from ai_cae_lab.report import generate_report


def scan_run_evidence(run_dir: str) -> dict[str, Any]:
    return scan_evidence(run_dir, write=True)


def generate_run_report(run_dir: str) -> dict[str, Any]:
    return generate_report(run_dir)
