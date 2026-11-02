"""Build a complete local draft/evidence bundle using explicitly synthetic data."""

import argparse
import json
from pathlib import Path

from physical_ai.models import digest
from physical_ai.service import Service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    context = {
        "controller_identity": "SYNTHETIC_DEMO_NOT_A_REAL_CONTROLLER",
        **{
            field: digest({"synthetic_fixture": field})
            for field in (
                "robotware_and_options_hash",
                "profile_hash",
                "station_hash",
                "configuration_hash",
                "tool_load_wobj_hash",
                "dependencies_hash",
            )
        },
        "tool": "tool0",
        "wobj": "wobj0",
        "source": "OPERATOR_PROVIDED",
        "anchor": {
            "translation_mm": [400.0, 100.0, 500.0],
            "quaternion": [1.0, 0.0, 0.0, 0.0],
            "configuration": [0, 0, 0, 0],
            "external_axes": [9e9] * 6,
        },
    }
    service = Service(args.workspace)
    task = service.task_create({"mode": "C", "context": context})
    task_id = task["task_id"]
    summary = {
        "source": "SYNTHETIC_OFFLINE_DEMO",
        "task": task,
        "draft": service.task_render(task_id),
        "validation": service.task_validate(task_id),
        "execute_preparation": service.prepare_execute(task_id),
    }
    artifact = service.store.write_new("demo-" + task_id + ".json", summary)
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
