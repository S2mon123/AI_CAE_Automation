from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_src_on_path() -> None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        src = parent / "src"
        if (src / "ai_cae_lab").exists():
            sys.path.insert(0, str(src))
            return
        repo_src = parent.parent.parent / "src"
        if (repo_src / "ai_cae_lab").exists():
            sys.path.insert(0, str(repo_src))
            return


_ensure_repo_src_on_path()

from ai_cae_lab.mcp_server import main  # noqa: E402


if __name__ == "__main__":
    main()
