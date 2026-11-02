from __future__ import annotations

import hashlib
import platform
import sys
import time
from pathlib import Path

from physical_ai.adapters import AbbReader, BridgeReader
from physical_ai.models import CHECKS, TaskSpec, cube_geometry, digest, evaluate_report, rapid_source
from physical_ai.storage import Store
from physical_ai.tc2 import inspect_tsm, link_proposal


class Service:
    def __init__(self, workspace: Path, config: dict | None = None):
        self.store = Store(workspace)
        self.config = config or {}

    def capabilities(self) -> dict:
        implemented = (
            "task_create",
            "task_render",
            "task_validate",
            "task_get_validation",
            "tc2_inspect",
            "tc2_stage_link_proposal",
            "plc_read_alias",
            "abb_read",
        )
        return {
            "version": "0.4.0",
            "phase": "P0-P2_DEVELOPMENT",
            "protocol": "physical-ai/4.0",
            "capabilities": [
                {
                    "capability": name,
                    "implemented": True,
                    "adapter_loaded": name not in ("plc_read_alias", "abb_read"),
                    "probed_on_target": False,
                    "commissioned": False,
                    "authorized_now": False,
                    "target_identity": None,
                    "observed_at": None,
                    "evidence_id": None,
                }
                for name in implemented
            ],
            "field_status": "UNKNOWN",
            "motion_enabled": False,
            "engineering_activation_enabled": False,
            "not_implemented": [
                "automatic_simulation",
                "motion_approval_issuer",
                "device_writes",
                "deployment",
                "process_stop",
                "persistent_motion_supervisor",
                "tc2_com_stage",
            ],
            "note": "Capabilities are implementation inventory, not live health or operator authorization.",
        }

    def discover(self) -> dict:
        return {
            "source": "HOST_LOCAL",
            "observed_at": time.time(),
            "platform": platform.platform(),
            "python": sys.version,
            "workspace": str(self.store.root),
            "bridge_configured": bool(self.config.get("bridge")),
            "abb_configured": bool(self.config.get("abb")),
            "target_network_scanned": False,
            "field_status": "UNKNOWN",
        }

    def plc_read(self, alias: str) -> dict:
        if alias not in ("start", "done"):
            raise ValueError("ALIAS_NOT_ALLOWED")
        if not self.config.get("bridge"):
            return {"ok": False, "code": "BRIDGE_NOT_CONFIGURED", "quality": "UNKNOWN"}
        return BridgeReader(self.config["bridge"]).call("plc.read_bool", {"alias": alias})

    def bridge_status(self) -> dict:
        if not self.config.get("bridge"):
            return {"ok": False, "code": "BRIDGE_NOT_CONFIGURED", "quality": "UNKNOWN"}
        return BridgeReader(self.config["bridge"]).call("plc.state")

    def abb_read(self, operation: str, signal: str | None = None) -> dict:
        if not self.config.get("abb"):
            return {"ok": False, "code": "ABB_NOT_CONFIGURED", "quality": "UNKNOWN"}
        return AbbReader(self.config["abb"]).call(operation, signal)

    def task_create(self, spec: dict) -> dict:
        parsed = TaskSpec.model_validate(spec)
        task_id = self.store.new_id()
        record = {
            "task_id": task_id,
            "spec": parsed.model_dump(),
            "spec_hash": digest(parsed.model_dump()),
            "created_at": time.time(),
            "state": "DRAFT",
            "real_motion_authorized": False,
        }
        artifact = self.store.write_new(f"tasks/{task_id}/task.json", record)
        return {**record, "artifact": artifact, "geometry": cube_geometry(parsed)}

    def _load(self, task_id: str) -> tuple[dict, TaskSpec]:
        record = self.store.task(task_id)
        parsed = TaskSpec.model_validate(record["spec"])
        if record["task_id"] != task_id or digest(parsed.model_dump()) != record["spec_hash"]:
            raise ValueError("TASK_CONTENT_CHANGED")
        return record, parsed

    def task_render(self, task_id: str) -> dict:
        record, spec = self._load(task_id)
        module, source = rapid_source(spec, task_id)
        artifact = self.store.write_new(f"tasks/{task_id}/drafts/{self.store.new_id()}/{module}.mod", source)
        binding = self.binding(task_id)
        manifest = self.store.write_new(
            artifact["relative_path"] + ".manifest.json",
            {
                **binding,
                "artifact": artifact,
                "module": module,
                "entry": "RunCube",
                "state": "LOCAL_DRAFT",
                "ownership": "LOCAL_FILE_ONLY",
                "controller_inventory_checked": False,
                "loaded_on_controller": False,
                "program_pointer_selected": False,
                "dependencies": [spec.context.tool, spec.context.wobj],
                "real_motion_authorized": False,
            },
        )
        return {
            "artifact": artifact,
            "manifest": manifest,
            "binding": binding,
            "state": "LOCAL_DRAFT",
            "rapid_compiled": False,
            "real_motion_authorized": False,
        }

    def binding(self, task_id: str) -> dict:
        record, spec = self._load(task_id)
        if spec.mode == "A":
            source_hash = spec.existing_source_sha256
        else:
            _, source = rapid_source(spec, task_id)
            source_hash = hashlib.sha256(source.encode()).hexdigest()
        return {
            "task_id": task_id,
            "spec_hash": record["spec_hash"],
            "source_hash": source_hash,
            "context_hash": digest(spec.context.model_dump()),
        }

    def task_validate(self, task_id: str, report_path: str | None = None) -> dict:
        record, spec = self._load(task_id)
        binding = self.binding(task_id)
        if report_path:
            result = evaluate_report(self.store.read(report_path), binding, time.time())
        else:
            result = {
                "status": "INCOMPLETE",
                "blockers": ["SIMULATION_EVIDENCE_MISSING"],
                "auto_deployable": False,
                "real_motion_authorized": False,
            }
        report = {
            **result,
            **binding,
            "geometry": cube_geometry(spec),
            "static_geometry_check": "PASS",
            "controller_compilation": "UNKNOWN",
            "checked_at": time.time(),
            "checks_required": list(CHECKS),
            "input_report_path": report_path,
        }
        artifact = self.store.write_new(f"tasks/{task_id}/validations/{self.store.new_id()}.json", report)
        return {**report, "artifact": artifact}

    def task_get_validation(self, task_id: str, report_path: str) -> dict:
        # Reevaluate original evidence at read time, never reuse a cached PASS after expiry/context changes.
        record = self.store.read(report_path)
        if record.get("task_id") != task_id or "checked_at" not in record:
            raise ValueError("VALIDATION_REPORT_MISMATCH")
        for key, value in self.binding(task_id).items():
            if record.get(key) != value:
                raise ValueError("VALIDATION_BINDING_CHANGED")
        return self.task_validate(task_id, record.get("input_report_path"))

    def prepare_execute(self, task_id: str) -> dict:
        self._load(task_id)
        return {
            "task_id": task_id,
            "state": "BLOCKED",
            "real_motion_authorized": False,
            "blockers": [
                "EXECUTION_BACKEND_NOT_IMPLEMENTED",
                "STOP_NOT_COMMISSIONED",
                "PERSISTENT_SUPERVISOR_NOT_IMPLEMENTED",
                "LIVE_ENTRY_AND_POSE_NOT_VERIFIED",
                "OPERATOR_APPROVAL_NOT_ISSUED",
            ],
            "binding": self.binding(task_id),
        }

    def tc2_inspect(self, path: str) -> dict:
        return inspect_tsm(self.store.read_bytes(path))

    def tc2_stage(self, path: str, from_path: str, to_path: str, bit_count: int) -> dict:
        data = self.store.read_bytes(path)
        proposal = link_proposal(data, from_path, to_path, bit_count)
        run = self.store.new_id()
        # Snapshot exact bytes, preserving encoding. No XML reserialization or speculative link mutation.
        snapshot = self.store.path(f"engineering/{run}/source.tsm")
        snapshot.parent.mkdir(parents=True)
        with snapshot.open("xb") as handle:
            handle.write(data)
        proposal["snapshot"] = str(snapshot)
        proposal["artifact"] = self.store.write_new(f"engineering/{run}/proposal.json", proposal.copy())
        return proposal

    def export_report(self) -> dict:
        return self.store.write_new(
            f"reports/{self.store.new_id()}.json", {"capabilities": self.capabilities(), "host": self.discover()}
        )
