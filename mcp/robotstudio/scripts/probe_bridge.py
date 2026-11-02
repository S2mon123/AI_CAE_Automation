from __future__ import annotations

import json

from robotstudio_mcp.bridge.client import BridgeClient
from robotstudio_mcp.settings import Settings


def main() -> int:
    status = BridgeClient(Settings.from_env()).status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["online"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
