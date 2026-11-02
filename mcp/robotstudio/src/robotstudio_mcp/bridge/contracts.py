from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class BridgeMethod:
    name: str
    side_effect: str
    description: str


READ_ONLY_METHODS: tuple[BridgeMethod, ...] = (
    BridgeMethod("environment.ping", "none", "Return the live Add-In and RobotStudio version."),
    BridgeMethod("capabilities.get", "none", "Return the bridge's fixed method registry."),
    BridgeMethod("station.active", "none", "Return the active Station identity."),
    BridgeMethod("station.summary", "none", "Return a Station object and task summary."),
    BridgeMethod("station.components", "none", "List Station project objects."),
    BridgeMethod("station.robots", "none", "List mechanical units and mechanisms."),
    BridgeMethod("station.robot", "none", "Read one robot or mechanical unit."),
    BridgeMethod("station.tools", "none", "List RsToolData declarations."),
    BridgeMethod("station.workobjects", "none", "List RsWorkObject declarations."),
    BridgeMethod("station.targets", "none", "List Station targets and target declarations."),
    BridgeMethod("station.target", "none", "Read one target in full."),
    BridgeMethod("station.paths", "none", "List path procedures."),
    BridgeMethod("station.path", "none", "Read path instructions and references."),
    BridgeMethod("controller.scan", "controller_read", "Classify discovered controllers without connecting."),
    BridgeMethod("controller.status", "controller_read", "Read the active virtual controller state."),
    BridgeMethod("controller.program_pointer", "controller_read", "Read task program pointers."),
    BridgeMethod("rapid.tasks", "controller_read", "List RAPID tasks from the active virtual controller."),
    BridgeMethod("rapid.modules", "controller_read", "List RAPID module metadata."),
    BridgeMethod("controller.eventlog", "controller_read", "Read real controller Event Log entries."),
    BridgeMethod("controller.io", "controller_read", "List I/O signals from the active virtual controller."),
    BridgeMethod("controller.io_signal", "controller_read", "Read one I/O signal."),
)

METHOD_NAMES = frozenset(method.name for method in READ_ONLY_METHODS)


def capability_document() -> dict[str, Any]:
    return {
        "release_phase": ["phase_0", "phase_1"],
        "read_only": True,
        "controller_scope": "virtual_only",
        "methods": [
            {"name": method.name, "side_effect": method.side_effect, "description": method.description}
            for method in READ_ONLY_METHODS
        ],
        "not_exposed": [
            "arbitrary command or script execution",
            "Station writes",
            "RAPID upload/load/write",
            "I/O writes",
            "program pointer reset",
            "RAPID start/stop",
            "real controller connection or write",
        ],
    }
