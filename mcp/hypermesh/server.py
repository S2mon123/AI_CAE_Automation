from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_repo_src_on_path() -> None:
    for parent in Path(__file__).resolve().parents:
        src = parent / "src"
        if (src / "ai_cae_lab").exists():
            sys.path.insert(0, str(src))
            return


def build_server():
    os.environ.setdefault("AI_CAE_MCP_SOLVERS", "hypermesh")
    _ensure_repo_src_on_path()
    from ai_cae_lab.mcp_server import build_server as build_core_server
    from hypermesh_profile import register_hypermesh_profile

    return register_hypermesh_profile(build_core_server("hypermesh"))


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
