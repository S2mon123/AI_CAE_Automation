from __future__ import annotations

import ctypes
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import winreg
except ImportError:  # pragma: no cover - Windows is the supported host
    winreg = None  # type: ignore[assignment]


SDK_FILES = (
    "ABB.Robotics.RobotStudio.dll",
    "ABB.Robotics.RobotStudio.Stations.dll",
    "ABB.Robotics.RobotStudio.Controllers.dll",
    "ABB.Robotics.Controllers.PC.dll",
    "ABB.Robotics.Math.dll",
)


@dataclass(slots=True)
class Installation:
    path: Path
    display_name: str
    display_version: str | None
    source: str


def _file_version(path: Path) -> str | None:
    if sys.platform != "win32" or not path.is_file():
        return None
    try:
        size = ctypes.windll.version.GetFileVersionInfoSizeW(str(path), None)
        if not size:
            return None
        buffer = ctypes.create_string_buffer(size)
        if not ctypes.windll.version.GetFileVersionInfoW(str(path), 0, size, buffer):
            return None
        value = ctypes.c_void_p()
        length = ctypes.c_uint()
        if not ctypes.windll.version.VerQueryValueW(buffer, "\\", ctypes.byref(value), ctypes.byref(length)):
            return None

        class VS_FIXEDFILEINFO(ctypes.Structure):
            _fields_ = [
                ("dwSignature", ctypes.c_uint32),
                ("dwStrucVersion", ctypes.c_uint32),
                ("dwFileVersionMS", ctypes.c_uint32),
                ("dwFileVersionLS", ctypes.c_uint32),
                ("dwProductVersionMS", ctypes.c_uint32),
                ("dwProductVersionLS", ctypes.c_uint32),
                ("dwFileFlagsMask", ctypes.c_uint32),
                ("dwFileFlags", ctypes.c_uint32),
                ("dwFileOS", ctypes.c_uint32),
                ("dwFileType", ctypes.c_uint32),
                ("dwFileSubtype", ctypes.c_uint32),
                ("dwFileDateMS", ctypes.c_uint32),
                ("dwFileDateLS", ctypes.c_uint32),
            ]

        info = ctypes.cast(value, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
        return ".".join(
            str(part)
            for part in (
                info.dwFileVersionMS >> 16,
                info.dwFileVersionMS & 0xFFFF,
                info.dwFileVersionLS >> 16,
                info.dwFileVersionLS & 0xFFFF,
            )
        )
    except (AttributeError, OSError, ValueError):
        return None


def _registry_installations() -> list[Installation]:
    if winreg is None:
        return []
    results: list[Installation] = []
    roots = ((winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY), (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY))
    uninstall = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    for hive, view in roots:
        try:
            with winreg.OpenKey(hive, uninstall, 0, winreg.KEY_READ | view) as root:
                count = winreg.QueryInfoKey(root)[0]
                for index in range(count):
                    try:
                        with winreg.OpenKey(root, winreg.EnumKey(root, index)) as key:
                            name = str(winreg.QueryValueEx(key, "DisplayName")[0])
                            if "RobotStudio 2025" not in name:
                                continue
                            location = str(winreg.QueryValueEx(key, "InstallLocation")[0]).strip()
                            try:
                                version = str(winreg.QueryValueEx(key, "DisplayVersion")[0])
                            except OSError:
                                version = None
                            if location:
                                results.append(
                                    Installation(Path(location).resolve(strict=False), name, version, "registry")
                                )
                    except OSError:
                        continue
        except OSError:
            continue
    unique: dict[str, Installation] = {str(item.path).lower(): item for item in results}
    return list(unique.values())


class EnvironmentProbe:
    def __init__(self, installation_override: Path | None = None) -> None:
        self.installation_override = installation_override

    def configure(self, path: Path | None) -> None:
        self.installation_override = path.resolve(strict=False) if path else None

    def installations(self) -> list[Installation]:
        discovered: list[Installation] = []
        if self.installation_override is not None:
            discovered.append(
                Installation(self.installation_override, "RobotStudio override", None, "process_override")
            )
        discovered.extend(_registry_installations())
        unique: dict[str, Installation] = {str(item.path).lower(): item for item in discovered}
        return list(unique.values())

    def active_installation(self) -> Installation | None:
        if self.installation_override is not None:
            executable = self.installation_override / "Bin" / "RobotStudio.exe"
            if executable.is_file():
                return Installation(
                    self.installation_override,
                    "RobotStudio override",
                    None,
                    "process_override",
                )
            return None
        for item in self.installations():
            if (item.path / "Bin" / "RobotStudio.exe").is_file():
                return item
        return None

    def inspect(self) -> dict[str, Any]:
        installation = self.active_installation()
        sdk: list[dict[str, Any]] = []
        robotstudio_exe_version = None
        if installation:
            bin_dir = installation.path / "Bin"
            robotstudio_exe_version = _file_version(bin_dir / "RobotStudio.exe") or installation.display_version
            for name in SDK_FILES:
                path = bin_dir / name
                sdk.append({"name": name, "present": path.is_file(), "version": _file_version(path)})
        return {
            "platform": platform.platform(),
            "python": {"version": platform.python_version(), "executable": sys.executable},
            "robotstudio": (
                {
                    **asdict(installation),
                    "path": str(installation.path),
                    "executable": str(installation.path / "Bin" / "RobotStudio.exe"),
                    "executable_version": robotstudio_exe_version,
                }
                if installation
                else None
            ),
            "sdk_assemblies": sdk,
        }

    def compatibility(self) -> dict[str, Any]:
        report = self.inspect()
        robotstudio = report["robotstudio"]
        host_version = robotstudio.get("executable_version") if robotstudio else None
        host_prefix = ".".join(str(host_version).split(".")[:2]) if host_version else None
        missing = [item["name"] for item in report["sdk_assemblies"] if not item["present"]]
        mismatched = [
            {"name": item["name"], "version": item["version"]}
            for item in report["sdk_assemblies"]
            if item["present"] and host_prefix and item["version"] and not item["version"].startswith(host_prefix + ".")
        ]
        return {
            "compatible": bool(robotstudio and not missing and not mismatched and host_prefix == "25.3"),
            "target": "RobotStudio 2025.3 / .NET Framework 4.8",
            "host_version": host_version,
            "missing_assemblies": missing,
            "mismatched_assemblies": mismatched,
            "note": "Compatibility is strict for the locally audited 25.3 SDK minor version.",
        }
