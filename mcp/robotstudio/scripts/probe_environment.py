from __future__ import annotations

import json

from robotstudio_mcp.environment import EnvironmentProbe
from robotstudio_mcp.settings import Settings


def main() -> int:
    settings = Settings.from_env()
    probe = EnvironmentProbe(settings.installation_override)
    print(
        json.dumps(
            {"environment": probe.inspect(), "compatibility": probe.compatibility()}, ensure_ascii=False, indent=2
        )
    )
    return 0 if probe.active_installation() else 2


if __name__ == "__main__":
    raise SystemExit(main())
