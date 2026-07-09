from __future__ import annotations

from typing import Any

from ai_cae_lab.adapters.comsol import (
    comsol_check_install,
    comsol_compile_java,
    comsol_run_batch,
    comsol_run_compiled_class,
    comsol_run_java_model_to_mph,
    comsol_validate_mph_loadable,
    write_comsol_cube_java,
    write_comsol_mph_validator_java,
)


def check_comsol_installation(comsol_root: str | None = None, comsol_batch: str | None = None, java_path: str | None = None) -> dict[str, Any]:
    return comsol_check_install(comsol_root, comsol_batch, java_path)


def write_cube_smoke_java(target_path: str, class_name: str = "ComsolCube10mm", output_file: str = "../outputs/comsol_cube_10mm.mph", overwrite: bool = False) -> dict[str, Any]:
    return write_comsol_cube_java(target_path, class_name, output_file, overwrite)


def compile_java_file(java_file: str, run_dir: str, comsol_compile: str | None = None, timeout_sec: int = 1800) -> dict[str, Any]:
    return comsol_compile_java(java_file, run_dir, comsol_compile, timeout_sec)


def run_compiled_java_class(class_file: str, run_dir: str, output_file: str | None = None, comsol_batch: str | None = None, timeout_sec: int = 7200) -> dict[str, Any]:
    return comsol_run_compiled_class(class_file, run_dir, output_file, comsol_batch, None, timeout_sec)


def run_java_model_to_mph(java_file: str, run_dir: str, output_file: str | None = None, comsol_compile: str | None = None, comsol_batch: str | None = None, timeout_sec: int = 7200) -> dict[str, Any]:
    return comsol_run_java_model_to_mph(java_file, run_dir, output_file, comsol_compile, comsol_batch, timeout_sec)


def run_batch_file(run_dir: str, input_file: str | None = None, output_file: str | None = None, comsol_batch: str | None = None, timeout_sec: int = 7200) -> dict[str, Any]:
    return comsol_run_batch(run_dir, input_file, output_file, comsol_batch, None, timeout_sec)



def write_mph_validator_java(target_path: str, class_name: str = "ValidateMphLoadable", overwrite: bool = False) -> dict[str, Any]:
    return write_comsol_mph_validator_java(target_path, class_name, overwrite)


def validate_mph_loadable(mph_file: str, run_dir: str, validated_copy: str | None = None, comsol_compile: str | None = None, comsol_batch: str | None = None, timeout_sec: int = 3600) -> dict[str, Any]:
    return comsol_validate_mph_loadable(mph_file, run_dir, validated_copy, comsol_compile, comsol_batch, timeout_sec)
