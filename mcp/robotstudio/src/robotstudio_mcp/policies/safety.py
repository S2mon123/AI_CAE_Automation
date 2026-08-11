from __future__ import annotations

from typing import Any


def safety_policy() -> dict[str, Any]:
    return {
        "release": "0.1.0-phase0-phase1",
        "level": "LEVEL_0_READ_ONLY",
        "controller_scope": "virtual_only",
        "real_controller": {
            "discovery": "classification_only",
            "connect": "not_exposed",
            "read": "not_exposed",
            "write": "prohibited",
        },
        "station_write": "not_exposed",
        "rapid_write": "not_exposed",
        "virtual_execution": "not_exposed",
        "io_write": "not_exposed",
        "arbitrary_execution": "prohibited",
        "bridge": {
            "bind": "127.0.0.1",
            "authentication": "random user-private token",
            "framing": "4-byte network-order length + UTF-8 JSON",
            "method_dispatch": "fixed allowlist; no reflection dispatch",
        },
        "implemented_side_effects": ["none", "filesystem_read", "filesystem_write", "controller_read"],
    }
