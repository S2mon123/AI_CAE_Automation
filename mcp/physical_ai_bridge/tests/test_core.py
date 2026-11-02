from __future__ import annotations

import hashlib
import json
import math
import time
from itertools import pairwise

import pytest

from physical_ai.models import CHECKS, TaskSpec, cube_geometry, digest, evaluate_report, rapid_source
from physical_ai.service import Service
from physical_ai.storage import Store
from physical_ai.tc2 import inspect_tsm


@pytest.fixture
def spec():
    return {
        "mode": "C",
        "context": {
            "controller_identity": "offline-fixture-only",
            **{
                field: digest({"fixture": field})
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
            "anchor": {
                "translation_mm": [400.0, 100.0, 500.0],
                "quaternion": [1.0, 0.0, 0.0, 0.0],
                "configuration": [0, 0, 0, 0],
                "external_axes": [9e9] * 6,
            },
        },
        "completion_timeout_s": 600.0,
    }


def test_cube_real_geometry(spec):
    parsed = TaskSpec.model_validate(spec)
    geometry = cube_geometry(parsed)
    vertices = geometry["vertices_mm"]
    distances = [math.dist(a, b) for a, b in pairwise(vertices)]
    assert distances == [200.0] * 16
    assert sum(distances) == 3200
    assert len({tuple(sorted((tuple(a), tuple(b)))) for a, b in pairwise(vertices)}) == 12
    assert vertices[-1] == vertices[0]
    assert geometry["nominal_duration_s"] == pytest.approx(213.333333)


@pytest.mark.parametrize(
    "field,value",
    [
        ("completion_timeout_s", 120.0),
        ("side_length_mm", float("nan")),
        ("side_length_mm", -1.0),
        ("override_percent", 0.0),
        ("override_percent", True),
        ("mode", "D"),
    ],
)
def test_reject_bad_task(spec, field, value):
    spec[field] = value
    with pytest.raises(ValueError):
        TaskSpec.model_validate(spec)


def test_frozen_rapid_and_injection(spec):
    parsed = TaskSpec.model_validate(spec)
    module, source = rapid_source(parsed, "a" * 32)
    assert len(module) <= 32 and source.count("MoveL ") == 16
    assert "CRobT" not in source and "SetDO" not in source and "PROC main" not in source
    assert "400,100,500" in source and source.count("\\WObj:=wobj0") == 16
    spec["context"]["tool"] = "tool0; Start;"
    with pytest.raises(ValueError):
        TaskSpec.model_validate(spec)


def test_A_never_overwrites(spec):
    spec.update(mode="A", existing_module="Production", existing_routine="Cube", existing_source_sha256="a" * 64)
    with pytest.raises(ValueError, match="A_TASK"):
        rapid_source(TaskSpec.model_validate(spec), "a" * 32)


def test_store_escape_and_no_overwrite(tmp_path):
    store = Store(tmp_path)
    for path in ("../outside", str(tmp_path.parent / "outside")):
        with pytest.raises(ValueError):
            store.write_new(path, "bad")
    store.write_new("AI_existing.mod", "production")
    with pytest.raises(FileExistsError):
        store.write_new("AI_existing.mod", "replacement")
    assert store.read_bytes("AI_existing.mod") == b"production"


@pytest.mark.parametrize("check", CHECKS)
@pytest.mark.parametrize("state", ["UNKNOWN", "NOT_CONFIGURED", "FAIL", "STALE", None])
def test_unknown_simulation_never_passes(check, state):
    report = {
        **{key: "PASS" for key in CHECKS},
        "source": "ROBOTSTUDIO_VC",
        "report_id": "fixture",
        "issued_at": 100,
        "expires_at": 200,
        "task_id": "fixture",
    }
    report[check] = state
    result = evaluate_report(report, {"task_id": "fixture"}, 150)
    assert result["status"] == "INCOMPLETE" and not result["real_motion_authorized"]


def test_evidence_binding_expiry_and_non_authority():
    report = {
        **{key: "PASS" for key in CHECKS},
        "source": "ROBOTSTUDIO_VC",
        "report_id": "fixture",
        "issued_at": 100,
        "expires_at": 200,
        "context_hash": "a",
    }
    assert evaluate_report(report, {"context_hash": "a"}, 150)["status"] == "PASS"
    assert not evaluate_report(report, {"context_hash": "a"}, 150)["auto_deployable"]
    for now in (99, 200, 201):
        assert evaluate_report(report, {"context_hash": "a"}, now)["status"] == "INCOMPLETE"
    assert evaluate_report(report, {"context_hash": "b"}, 150)["status"] == "INCOMPLETE"
    report["issued_at"] = float("nan")
    assert evaluate_report(report, {"context_hash": "a"}, 150)["status"] == "INCOMPLETE"


def test_task_workflow_and_tamper(tmp_path, spec):
    service = Service(tmp_path)
    task = service.task_create(spec)
    rendered = service.task_render(task["task_id"])
    data = service.store.read_bytes(rendered["artifact"]["relative_path"])
    assert hashlib.sha256(data).hexdigest() == rendered["binding"]["source_hash"]
    assert service.task_validate(task["task_id"])["status"] == "INCOMPLETE"
    assert service.prepare_execute(task["task_id"])["state"] == "BLOCKED"
    file = service.store.path(f"tasks/{task['task_id']}/task.json")
    record = json.loads(file.read_text())
    record["spec"]["context"]["anchor"]["translation_mm"][0] += 1
    file.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="TASK_CONTENT_CHANGED"):
        service.task_render(task["task_id"])


def test_validation_rechecks_staleness(tmp_path, spec):
    service = Service(tmp_path)
    task = service.task_create(spec)["task_id"]
    report = {
        **service.binding(task),
        **{key: "PASS" for key in CHECKS},
        "source": "ROBOTSTUDIO_VC",
        "report_id": "fixture",
        "issued_at": time.time() - 5,
        "expires_at": time.time() + 60,
    }
    path = service.store.write_new("inputs/report.json", report)["relative_path"]
    result = service.task_validate(task, path)
    assert result["status"] == "PASS"
    report["expires_at"] = time.time() - 1
    service.store.path(path).write_text(json.dumps(report))
    assert service.task_get_validation(task, result["artifact"]["relative_path"])["status"] == "INCOMPLETE"


def test_tsm_proposal_preserves_source(tmp_path):
    data = b'<TcSmProject><Mappings><OwnerA Name="PLC"><Link VarA="start" VarB="Output0" Size="8"/></OwnerA></Mappings></TcSmProject>'
    service = Service(tmp_path)
    service.store.path("source.tsm").write_bytes(data)
    before = inspect_tsm(data)
    assert before["free_bits"] == "UNKNOWN" and before["runtime_consistency"] == "UNKNOWN"
    proposal = service.tc2_stage("source.tsm", "PLC^Stop", "IO^Output0[4]", 1)
    assert not proposal["applied_to_copy"] and not proposal["activation_authorized"]
    assert service.store.path("source.tsm").read_bytes() == data
    assert "BYTE_AND_ARRAY_OVERLAPS_UNCHECKED" in proposal["blockers"]


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
def test_dtd_rejected(encoding):
    with pytest.raises(ValueError, match="DTD"):
        inspect_tsm('<!DOCTYPE x [<!ENTITY leak SYSTEM "file:///secret">]><x/>'.encode(encoding))


def test_no_configuration_no_connection(tmp_path):
    service = Service(tmp_path)
    assert service.bridge_status()["quality"] == "UNKNOWN"
    assert service.plc_read("done")["code"] == "BRIDGE_NOT_CONFIGURED"
    assert service.abb_read("status")["code"] == "ABB_NOT_CONFIGURED"
    with pytest.raises(ValueError):
        service.plc_read("force")
