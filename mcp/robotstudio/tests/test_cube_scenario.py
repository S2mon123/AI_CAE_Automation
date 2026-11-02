from types import SimpleNamespace

import pytest

from robotstudio_mcp.errors import RobotStudioMcpError
from robotstudio_mcp.tools.scenario_tools import collect_cube_context


class ScenarioBridge:
    def __init__(self, virtual=True, routine="Cube", change_identity=False):
        self.virtual = virtual
        self.routine = routine
        self.change_identity = change_identity
        self.calls = []

    def call(self, method, params=None):
        self.calls.append(method)
        if method == "controller.status":
            return {"result": {"identity": {"system_id": "fixture"}, "is_virtual": self.virtual}}
        if method == "controller.program_pointer":
            return {"result": {"system_id": "fixture", "tasks": [{"name": "T_ROB1",
                "program_pointer": {"module": "Test", "routine": self.routine}}]}}
        return {"result": {"system_id": "changed" if self.change_identity else "fixture", "value": 1}}


def test_pointer_match_does_not_authorize_or_prove_completion():
    bridge = ScenarioBridge()
    value = collect_cube_context(SimpleNamespace(bridge=bridge), "Test", "Cube")
    assert value["entry_pointer_matches"]
    assert not value["real_motion_authorized"] and not value["waiting_for_start_proven"]
    assert not value["simulation_passed"]
    assert len(bridge.calls) == 5


def test_old_J6_entry_rejected():
    value = collect_cube_context(SimpleNamespace(bridge=ScenarioBridge(routine="J6")), "Test", "Cube")
    assert "EXPECTED_ENTRY_NOT_SELECTED" in value["blockers"]


def test_real_controller_stops_before_io_reads():
    bridge = ScenarioBridge(virtual=False)
    with pytest.raises(RobotStudioMcpError):
        collect_cube_context(SimpleNamespace(bridge=bridge), "Test", "Cube")
    assert bridge.calls == ["controller.status"]


def test_identity_change_between_reads_rejected():
    with pytest.raises(RobotStudioMcpError):
        collect_cube_context(SimpleNamespace(bridge=ScenarioBridge(change_identity=True)), "Test", "Cube")
