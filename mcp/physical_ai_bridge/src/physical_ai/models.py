from __future__ import annotations

import hashlib
import json
import math
import re
from itertools import pairwise
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    ).hexdigest()


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Anchor(StrictModel):
    translation_mm: list[float] = Field(min_length=3, max_length=3)
    quaternion: list[float] = Field(min_length=4, max_length=4)
    configuration: list[int] = Field(min_length=4, max_length=4)
    external_axes: list[float] = Field(min_length=6, max_length=6)

    @field_validator("translation_mm")
    @classmethod
    def finite_engineering_coordinates(cls, value: list[float]) -> list[float]:
        if any(abs(x) > 1_000_000 for x in value):
            raise ValueError("coordinate exceeds offline generator range; this is not a robot safety limit")
        return value

    @field_validator("quaternion")
    @classmethod
    def unit_quaternion(cls, value: list[float]) -> list[float]:
        if abs(sum(x * x for x in value) - 1) > 1e-6:
            raise ValueError("quaternion must already be normalized")
        return value


class Context(StrictModel):
    controller_identity: str = Field(min_length=1, max_length=200)
    robotware_and_options_hash: str
    profile_hash: str
    station_hash: str
    configuration_hash: str
    tool_load_wobj_hash: str
    dependencies_hash: str
    tool: str
    wobj: str
    anchor: Anchor
    source: Literal["OPERATOR_PROVIDED", "ROBOTSTUDIO_VC", "ABB_LIVE"] = "OPERATOR_PROVIDED"

    @field_validator("tool", "wobj")
    @classmethod
    def identifier(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", value):
            raise ValueError("RAPID identifier required")
        return value

    @field_validator(
        "robotware_and_options_hash",
        "profile_hash",
        "station_hash",
        "configuration_hash",
        "tool_load_wobj_hash",
        "dependencies_hash",
    )
    @classmethod
    def hash_value(cls, value: str) -> str:
        if not re.fullmatch("[a-f0-9]{64}", value):
            raise ValueError("SHA-256 lowercase hex required; do not invent missing context")
        return value


class TaskSpec(StrictModel):
    mode: Literal["A", "B", "C"]
    context: Context
    side_length_mm: float = Field(default=200.0, gt=0, le=1000)
    programmed_speed_mm_s: Literal[50] = 50
    override_percent: float = Field(default=30.0, gt=0, le=100)
    completion_timeout_s: float = Field(default=600.0, gt=0, le=86400)
    existing_module: str | None = None
    existing_routine: str | None = None
    existing_source_sha256: str | None = None

    @model_validator(mode="after")
    def task_contract(self) -> TaskSpec:
        # A task is an inventory reference, never a generated replacement.
        if self.mode == "A":
            for value in (self.existing_module, self.existing_routine):
                Context.identifier(value or "")
            Context.hash_value(self.existing_source_sha256 or "")
        elif any(x is not None for x in (self.existing_module, self.existing_routine, self.existing_source_sha256)):
            raise ValueError("generated task cannot claim an existing module")
        nominal = 16 * self.side_length_mm / (50 * self.override_percent / 100)
        if self.completion_timeout_s <= nominal:
            raise ValueError("completion timeout must exceed nominal path time; it is not a Stop timeout")
        return self


CUBE_VERTICES = (
    "000",
    "100",
    "110",
    "010",
    "000",
    "001",
    "101",
    "111",
    "011",
    "001",
    "101",
    "100",
    "110",
    "111",
    "011",
    "010",
    "000",
)


def cube_geometry(spec: TaskSpec) -> dict:
    anchor = spec.context.anchor.translation_mm
    vertices = [[anchor[i] + int(bits[i]) * spec.side_length_mm for i in range(3)] for bits in CUBE_VERTICES]
    edges = {tuple(sorted((a, b))) for a, b in pairwise(CUBE_VERTICES)}
    return {
        "vertices_mm": vertices,
        "segments": 16,
        "unique_edges": len(edges),
        "length_mm": 16 * spec.side_length_mm,
        "coordinate_frame": spec.context.wobj,
        "nominal_duration_s": 16 * spec.side_length_mm / (50 * spec.override_percent / 100),
        "completion_timeout_s": spec.completion_timeout_s,
        "orientation_policy": "keep_tcp_orientation",
        "closed": vertices[0] == vertices[-1],
        "mechanical_reachability": "UNKNOWN",
        "collision_check": "NOT_CONFIGURED",
    }


def rapid_source(spec: TaskSpec, task_id: str) -> tuple[str, str]:
    if spec.mode == "A":
        raise ValueError("A_TASK_USES_EXISTING_CODE")
    if not re.fullmatch(r"[a-f0-9]{32}", task_id):
        raise ValueError("invalid task id")
    module = "AI_Cube_" + task_id[:20]
    anchor = spec.context.anchor

    def array(values: list) -> str:
        return "[" + ",".join(format(x, ".12g") for x in values) + "]"

    target = (
        "["
        + ",".join(
            array(v) for v in (anchor.translation_mm, anchor.quaternion, anchor.configuration, anchor.external_axes)
        )
        + "]"
    )
    lines = [
        f"MODULE {module}",
        "    ! OFFLINE DRAFT. No automatic approach, handshake, or Stop implementation.",
        "    ! Entry requires separately verified pose/configuration, tool/load/wobj and Stop channel.",
        "    ! Nominal duration assumes operator override; this module does not set override.",
        f"    CONST robtarget pAnchor := {target};",
        "    PROC RunCube()",
    ]
    for bits in CUBE_VERTICES[1:]:
        offsets = ",".join(format(int(bit) * spec.side_length_mm, ".12g") for bit in bits)
        lines.append(f"        MoveL Offs(pAnchor,{offsets}),v50,fine,{spec.context.tool}\\WObj:={spec.context.wobj};")
    lines += ["    ENDPROC", "ENDMODULE", ""]
    return module, "\n".join(lines)


CHECKS = (
    "rapid_check",
    "path_reachability",
    "joint_limits",
    "collision_check",
    "singularity_and_configuration_review",
    "speed_review",
    "model_coverage",
    "whole_path_check",
)


def evaluate_report(report: dict, binding: dict, now: float) -> dict:
    """Assess supplied evidence only. Never creates an approval or trusts the submitter."""
    blockers = []
    if report.get("source") not in ("ROBOTSTUDIO_VC", "OPERATOR_ROBOTSTUDIO_REVIEW"):
        blockers.append("INVALID_EVIDENCE_SOURCE")
    for key, expected in binding.items():
        if report.get(key) != expected:
            blockers.append("BINDING_MISMATCH:" + key)
    for key in CHECKS:
        if report.get(key) != "PASS":
            blockers.append("CHECK_NOT_PASS:" + key)
    for key in ("issued_at", "expires_at"):
        value = report.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            blockers.append("INVALID_TIME:" + key)
    if not any(x.startswith("INVALID_TIME") for x in blockers):
        if not report["issued_at"] <= now < report["expires_at"]:
            blockers.append("STALE_OR_FUTURE_EVIDENCE")
    if not report.get("report_id"):
        blockers.append("MISSING_REPORT_ID")
    return {
        "status": "PASS" if not blockers else "INCOMPLETE",
        "blockers": blockers,
        "evidence_authenticity": "UNVERIFIED",
        "auto_deployable": False,
        "real_motion_authorized": False,
        "note": "Structural evidence assessment only; operator/adapter provenance is not authenticated.",
    }
