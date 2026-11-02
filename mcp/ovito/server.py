from __future__ import annotations

import os
import sys
from pathlib import Path


PROFILE = "ovito"


def _ensure_repo_src_on_path() -> None:
    for parent in Path(__file__).resolve().parents:
        src = parent / "src"
        if (src / "ai_cae_lab").exists():
            sys.path.insert(0, str(src))
            return


def main() -> None:
    os.environ.setdefault("AI_CAE_MCP_SOLVERS", PROFILE)
    _ensure_repo_src_on_path()
    from ai_cae_lab.mcp_server import main as run_server

    run_server()


if __name__ == "__main__":
    main()
