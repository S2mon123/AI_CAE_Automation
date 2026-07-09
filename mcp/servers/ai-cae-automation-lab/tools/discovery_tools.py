from __future__ import annotations

from typing import Any

from ai_cae_lab.discovery import (
    discover_toolchains as _discover_toolchains,
    setup_local as _setup_local,
    write_activation_script,
    write_codex_mcp_config,
    write_local_config,
)


def discover_toolchains(deep: bool = False) -> dict[str, Any]:
    return _discover_toolchains(deep=deep)


def setup_local_toolchain(deep: bool = False) -> dict[str, Any]:
    return _setup_local(deep=deep)


def write_local_toolchain_config(path: str | None = None, deep: bool = False) -> dict[str, Any]:
    return write_local_config(path=path, deep=deep)


def write_toolchain_activation_script(config_path: str | None = None, output_path: str | None = None) -> dict[str, Any]:
    return write_activation_script(config_path=config_path, output_path=output_path)


def write_local_codex_mcp_config(output_path: str | None = None) -> dict[str, Any]:
    return write_codex_mcp_config(output_path=output_path)
