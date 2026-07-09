from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


MAX_LOG_BYTES = 2 * 1024 * 1024


@dataclass
class LogSignal:
    severity: str
    category: str
    line: int
    text: str


LICENSE_PATTERNS = [
    re.compile(r"license\s+(error|failure|checkout|denied)", re.IGNORECASE),
    re.compile(r"could not (obtain|checkout).*license", re.IGNORECASE),
    re.compile(r"no licenses? (are )?available", re.IGNORECASE),
    re.compile(r"licensed number of users already reached", re.IGNORECASE),
    re.compile(r"flexnet.*(error|denied|failed)", re.IGNORECASE),
    re.compile(r"license.*not.*available", re.IGNORECASE),
    re.compile(r"\u8bb8\u53ef\u8bc1.*(\u9519\u8bef|\u5931\u8d25|\u4e0d\u53ef\u7528|\u62d2\u7edd)", re.IGNORECASE),
]

FAILURE_PATTERNS = [
    re.compile(r"\b(error|failed|failure|fatal|exception)\b", re.IGNORECASE),
    re.compile(r"traceback \(most recent call last\)", re.IGNORECASE),
    re.compile(r"analysis terminated", re.IGNORECASE),
    re.compile(r"terminated due to errors", re.IGNORECASE),
    re.compile(r"floating point exception", re.IGNORECASE),
    re.compile(r"segmentation violation", re.IGNORECASE),
    re.compile(r"\baborted\b", re.IGNORECASE),
    re.compile(r"too many attempts made for this increment", re.IGNORECASE),
    re.compile(r"divergence detected", re.IGNORECASE),
    re.compile(r"reversed flow.*stabilize", re.IGNORECASE),
    re.compile(r"\u6ca1\u6709\u8981\u8fd0\u884c\u7684\u5bf9\u8c61", re.IGNORECASE),
    re.compile(r"\u53d1\u751f\u9519\u8bef", re.IGNORECASE),
    re.compile(r"\u65e0\u6cd5.*(\u6c42\u89e3|\u4fdd\u5b58|\u52a0\u8f7d|\u6253\u5f00)", re.IGNORECASE),
]

SUCCESS_PATTERNS = [
    re.compile(r"analysis has completed successfully", re.IGNORECASE),
    re.compile(r"abaqus job .* completed", re.IGNORECASE),
    re.compile(r"solution completed", re.IGNORECASE),
    re.compile(r"study .* (solved|completed)", re.IGNORECASE),
    re.compile(r"comsol.*(done|completed)", re.IGNORECASE),
    re.compile(r"normal completion", re.IGNORECASE),
    re.compile(r"return_code:\s*0", re.IGNORECASE),
    re.compile(r"\bcompleted\b", re.IGNORECASE),
    re.compile(r"\bconverged\b", re.IGNORECASE),
    re.compile(r"convergence criteria.*met", re.IGNORECASE),
    re.compile(r"fluent.*solution.*complete", re.IGNORECASE),
    re.compile(r"the following model has been saved", re.IGNORECASE),
    re.compile(r"AI_CAE_MPH_LOADABLE", re.IGNORECASE),
    re.compile(r"\u6a21\u578b.*(\u5df2\u4fdd\u5b58|\u4fdd\u5b58\u6210\u529f)", re.IGNORECASE),
]

BENIGN_FAILURE_SUBSTRINGS = [
    "0 error",
    "0 failed",
    "no error",
    "without error",
]


def _trim(text: str, limit: int = 220) -> str:
    compact = " ".join(text.strip().split())
    return compact[:limit]


def _is_benign_failure_line(line: str) -> bool:
    lower = line.lower()
    return any(item in lower for item in BENIGN_FAILURE_SUBSTRINGS)


def analyze_log_text(text: str) -> dict[str, Any]:
    signals: list[LogSignal] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        if any(pattern.search(line) for pattern in LICENSE_PATTERNS):
            signals.append(LogSignal("error", "license", number, _trim(line)))
            continue
        if not _is_benign_failure_line(line) and any(pattern.search(line) for pattern in FAILURE_PATTERNS):
            signals.append(LogSignal("error", "failure", number, _trim(line)))
            continue
        if any(pattern.search(line) for pattern in SUCCESS_PATTERNS):
            signals.append(LogSignal("info", "success", number, _trim(line)))

    categories = {signal.category for signal in signals}
    if "license" in categories:
        status = "license_error"
    elif "failure" in categories:
        status = "failed"
    elif "success" in categories:
        status = "success"
    else:
        status = "unknown"

    return {
        "status": status,
        "signals": [asdict(signal) for signal in signals[:20]],
        "signal_count": len(signals),
    }


def analyze_log_file(path: str | Path) -> dict[str, Any]:
    log_path = Path(path)
    raw = log_path.read_bytes()[:MAX_LOG_BYTES]
    text = raw.decode("utf-8", errors="replace")
    payload = analyze_log_text(text)
    payload["path"] = str(log_path)
    payload["truncated"] = log_path.stat().st_size > MAX_LOG_BYTES
    return payload
