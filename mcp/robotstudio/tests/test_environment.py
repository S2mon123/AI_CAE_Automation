from __future__ import annotations

from pathlib import Path

from robotstudio_mcp.environment import SDK_FILES, EnvironmentProbe


def test_override_requires_real_executable_for_active_installation(tmp_path: Path) -> None:
    probe = EnvironmentProbe(tmp_path)
    assert probe.active_installation() is None
    bin_dir = tmp_path / "Bin"
    bin_dir.mkdir()
    (bin_dir / "RobotStudio.exe").write_bytes(b"not-an-exe")
    for name in SDK_FILES:
        (bin_dir / name).write_bytes(b"not-a-dll")
    assert probe.active_installation() is not None
    report = probe.inspect()
    assert report["robotstudio"]["path"] == str(tmp_path)
    assert all(item["present"] for item in report["sdk_assemblies"])
