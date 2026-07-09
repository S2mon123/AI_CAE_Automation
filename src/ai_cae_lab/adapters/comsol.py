from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

from ..config import configured_solver_paths, load_toolbox_config
from .common import run_process


def _comsol_roots(root: str | None) -> list[Path]:
    if not root:
        return []
    base = Path(root)
    if not base.exists():
        return []
    if base.name.lower() == "multiphysics":
        return [base.parent]
    if (base / "Multiphysics").exists():
        return [base]
    return sorted(base.glob("COMSOL*"))


def _first_existing(candidates: list[str | Path | None]) -> str | None:
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return str(path)
        found = shutil.which(str(candidate))
        if found:
            return found
    return None


def resolve_comsol_exe(comsol_exe: str | None = None, comsol_root: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        comsol_exe,
        os.environ.get("COMSOL_EXE"),
        configured.get("exe"),
        shutil.which("comsol"),
        *[item / "Multiphysics" / "bin" / "win64" / "comsol.exe" for item in roots],
        *[item / "Multiphysics" / "bin" / "comsol" for item in roots],
    ]
    return _first_existing(candidates)


def resolve_comsol_batch(comsol_batch: str | None = None, comsol_root: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        comsol_batch,
        os.environ.get("COMSOL_BATCH"),
        configured.get("batch"),
        shutil.which("comsolbatch"),
        *[item / "Multiphysics" / "bin" / "win64" / "comsolbatch.exe" for item in roots],
        *[item / "Multiphysics" / "bin" / "comsolbatch" for item in roots],
    ]
    return _first_existing(candidates) or resolve_comsol_exe(comsol_root=root)


def resolve_comsol_java(java_path: str | None = None, comsol_root: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        java_path,
        os.environ.get("COMSOL_JAVA"),
        configured.get("java"),
        *[item / "Multiphysics" / "java" / "win64" / "jre" / "bin" / "java.exe" for item in roots],
        shutil.which("java"),
    ]
    return _first_existing(candidates)


def resolve_comsol_compile(comsol_compile: str | None = None, comsol_root: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        comsol_compile,
        os.environ.get("COMSOL_COMPILE"),
        configured.get("compile"),
        shutil.which("comsolcompile"),
        *[item / "Multiphysics" / "bin" / "win64" / "comsolcompile.exe" for item in roots],
        *[item / "Multiphysics" / "bin" / "comsolcompile" for item in roots],
    ]
    return _first_existing(candidates)


def resolve_comsol_mphserver(mphserver: str | None = None, comsol_root: str | None = None) -> str | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    roots = _comsol_roots(root)
    candidates: list[str | Path | None] = [
        mphserver,
        os.environ.get("COMSOL_MPHSERVER"),
        configured.get("mphserver"),
        shutil.which("comsolmphserver"),
        *[item / "Multiphysics" / "bin" / "win64" / "comsolmphserver.exe" for item in roots],
        *[item / "Multiphysics" / "bin" / "comsolmphserver" for item in roots],
    ]
    return _first_existing(candidates)


def comsol_api_index_path(comsol_root: str | None = None) -> Path | None:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    if not root:
        return None
    base = Path(root)
    if base.name.lower() != "multiphysics":
        base = base / "Multiphysics"
    return base / "doc" / "help" / "wtpwebapps" / "ROOT" / "doc" / "com.comsol.help.comsol" / "api" / "index.html"


def comsol_check_install(
    comsol_root: str | None = None,
    comsol_batch: str | None = None,
    java_path: str | None = None,
) -> dict[str, Any]:
    configured = configured_solver_paths(load_toolbox_config(), "comsol")
    root = comsol_root or os.environ.get("COMSOL_ROOT") or configured.get("root")
    exe = resolve_comsol_exe(comsol_root=root)
    batch = resolve_comsol_batch(comsol_batch, root)
    compile_cmd = resolve_comsol_compile(comsol_root=root)
    mphserver = resolve_comsol_mphserver(comsol_root=root)
    java = resolve_comsol_java(java_path, root)
    docs_root = Path(root) / "Multiphysics" / "doc" if root and Path(root).name.lower() != "multiphysics" else (Path(root) / "doc" if root else None)
    api_index = comsol_api_index_path(root)
    checks = {
        "comsol_root": {"path": root, "exists": bool(root and Path(root).exists())},
        "comsol_exe": {"path": exe, "exists": bool(exe and Path(exe).exists())},
        "comsol_batch": {"path": batch, "exists": bool(batch and Path(batch).exists())},
        "comsol_compile": {"path": compile_cmd, "exists": bool(compile_cmd and Path(compile_cmd).exists())},
        "comsol_mphserver": {"path": mphserver, "exists": bool(mphserver and Path(mphserver).exists())},
        "comsol_java": {"path": java, "exists": bool(java and Path(java).exists())},
        "docs_root": {"path": str(docs_root) if docs_root else None, "exists": bool(docs_root and docs_root.exists())},
        "api_index": {"path": str(api_index) if api_index else None, "exists": bool(api_index and api_index.exists())},
    }
    runnable = checks["comsol_batch"]["exists"] or checks["comsol_exe"]["exists"]
    buildable = checks["comsol_compile"]["exists"]
    return {
        "status": "ok" if runnable and buildable else ("partial" if runnable or buildable else "missing"),
        "checks": checks,
        "message": "This check verifies paths only. License availability is proven by a real smoke run.",
    }


def extract_java_public_class(java_file: str | Path) -> str:
    source = Path(java_file)
    text = source.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    if not match:
        match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    if not match:
        raise ValueError(f"No Java class declaration found in {source}")
    return match.group(1)


def compiled_class_path(java_file: str | Path, class_name: str | None = None) -> Path:
    source = Path(java_file)
    name = class_name or extract_java_public_class(source)
    return source.with_name(name + ".class")


def comsol_cube_java_source(class_name: str = "ComsolCube10mm", output_file: str = "../outputs/comsol_cube_10mm.mph") -> str:
    return f'''import com.comsol.model.*;
import com.comsol.model.util.*;

public class {class_name} {{
  public static Model run() {{
    Model model = ModelUtil.create("Model");
    model.modelNode().create("mod1");
    model.label("{class_name}.mph");
    model.param().set("L", "10[mm]", "Smoke-test cube side length");

    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").create("blk1", "Block");
    model.component("comp1").geom("geom1").feature("blk1").set("size", new String[]{{"L", "L", "L"}});
    model.component("comp1").geom("geom1").feature("blk1").set("base", "center");
    model.component("comp1").geom("geom1").run();

    model.component("comp1").material().create("mat1", "Common");
    model.component("comp1").material("mat1").label("Generic steel smoke material");
    model.component("comp1").material("mat1").propertyGroup("def").set("density", "7850[kg/m^3]");
    model.component("comp1").material("mat1").propertyGroup("def").set("thermalconductivity", "45[W/(m*K)]");
    model.component("comp1").material("mat1").propertyGroup("def").set("heatcapacity", "470[J/(kg*K)]");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(4);
    model.component("comp1").mesh("mesh1").run();
    return model;
  }}

  public static void main(String[] args) {{
    Model model = run();
    String out = args.length > 0 ? args[0] : "{output_file}";
    model.save(out);
  }}
}}
'''


def write_comsol_cube_java(
    target_path: str | Path,
    class_name: str = "ComsolCube10mm",
    output_file: str = "../outputs/comsol_cube_10mm.mph",
    overwrite: bool = False,
) -> dict[str, Any]:
    target = Path(target_path)
    if target.exists() and not overwrite:
        return {"status": "skipped", "path": str(target), "message": "target exists"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(comsol_cube_java_source(class_name=class_name, output_file=output_file), encoding="utf-8")
    return {"status": "ok", "path": str(target), "class_name": class_name, "output_file": output_file}


def comsol_mph_validator_java_source(class_name: str = "ValidateMphLoadable") -> str:
    return f'''import com.comsol.model.*;
import com.comsol.model.util.*;

public class {class_name} {{
  public static void main(String[] args) {{
    if (args.length < 1) {{
      throw new IllegalArgumentException("Usage: {class_name} <input.mph> [validated-copy.mph]");
    }}
    Model model = ModelUtil.load("ValidatedModel", args[0]);
    System.out.println("AI_CAE_MPH_LOADABLE: " + args[0]);
    if (args.length > 1 && args[1] != null && args[1].length() > 0) {{
      model.save(args[1]);
      System.out.println("AI_CAE_MPH_VALIDATED_COPY: " + args[1]);
    }}
  }}
}}
'''


def write_comsol_mph_validator_java(
    target_path: str | Path,
    class_name: str = "ValidateMphLoadable",
    overwrite: bool = False,
) -> dict[str, Any]:
    target = Path(target_path)
    if target.exists() and not overwrite:
        return {"status": "skipped", "path": str(target), "message": "target exists"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(comsol_mph_validator_java_source(class_name=class_name), encoding="utf-8")
    return {"status": "ok", "path": str(target), "class_name": class_name}


def comsol_run_batch(
    run_dir: str,
    input_file: str | None = None,
    output_file: str | None = None,
    comsol_batch: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_comsol_batch(comsol_batch)
    if command is None:
        return {"status": "missing", "message": "COMSOL batch command not found. Set COMSOL_BATCH or COMSOL_ROOT."}
    args: list[str] = []
    if input_file:
        path = Path(input_file)
        if not path.exists():
            return {"status": "missing", "message": f"COMSOL input file not found: {path}"}
        args.extend(["-inputfile", str(path)])
    if output_file:
        args.extend(["-outputfile", output_file])
    if extra_args:
        args.extend(extra_args)
    return run_process(
        command=command,
        args=args,
        run_dir=run_dir,
        log_name="comsol_batch.log",
        timeout_sec=timeout_sec,
    )


def comsol_compile_java(
    java_file: str,
    run_dir: str,
    comsol_compile: str | None = None,
    timeout_sec: int = 1800,
) -> dict[str, Any]:
    command = resolve_comsol_compile(comsol_compile)
    source = Path(java_file)
    if command is None:
        return {"status": "missing", "message": "COMSOL compile command not found. Set COMSOL_COMPILE or COMSOL_ROOT."}
    if not source.exists():
        return {"status": "missing", "message": f"COMSOL Java file not found: {source}"}
    return run_process(
        command=command,
        args=[str(source)],
        run_dir=run_dir,
        log_name="comsol_compile.log",
        timeout_sec=timeout_sec,
        cwd=source.parent,
    )


def comsol_run_compiled_class(
    class_file: str,
    run_dir: str,
    output_file: str | None = None,
    comsol_batch: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    command = resolve_comsol_batch(comsol_batch)
    compiled = Path(class_file)
    if command is None:
        return {"status": "missing", "message": "COMSOL batch command not found. Set COMSOL_BATCH or COMSOL_ROOT."}
    if not compiled.exists():
        return {"status": "missing", "message": f"COMSOL compiled class not found: {compiled}"}
    args: list[str] = ["-inputfile", str(compiled)]
    if output_file:
        args.extend(["-outputfile", output_file])
    if extra_args:
        args.extend(extra_args)
    return run_process(
        command=command,
        args=args,
        run_dir=run_dir,
        log_name="comsol_class_batch.log",
        timeout_sec=timeout_sec,
        cwd=compiled.parent,
    )


def comsol_run_java_model_to_mph(
    java_file: str,
    run_dir: str,
    output_file: str | None = None,
    comsol_compile: str | None = None,
    comsol_batch: str | None = None,
    timeout_sec: int = 7200,
) -> dict[str, Any]:
    source = Path(java_file)
    if not source.exists():
        return {"status": "missing", "stage": "prepare", "message": f"COMSOL Java file not found: {source}"}
    try:
        class_name = extract_java_public_class(source)
    except ValueError as exc:
        return {"status": "failed", "stage": "prepare", "message": str(exc)}

    compile_result = comsol_compile_java(str(source), run_dir, comsol_compile=comsol_compile, timeout_sec=min(timeout_sec, 1800))
    if compile_result.get("status") != "completed":
        return {
            "status": compile_result.get("status", "failed"),
            "stage": "compile",
            "class_name": class_name,
            "compile": compile_result,
        }

    class_path = compiled_class_path(source, class_name)
    run_result = comsol_run_compiled_class(
        str(class_path),
        run_dir,
        output_file=output_file,
        comsol_batch=comsol_batch,
        timeout_sec=timeout_sec,
    )
    return {
        "status": run_result.get("status", "failed"),
        "stage": "run",
        "class_name": class_name,
        "java_file": str(source),
        "class_file": str(class_path),
        "output_file": output_file,
        "compile": compile_result,
        "run": run_result,
    }



def comsol_validate_mph_loadable(
    mph_file: str,
    run_dir: str,
    validated_copy: str | None = None,
    comsol_compile: str | None = None,
    comsol_batch: str | None = None,
    timeout_sec: int = 3600,
) -> dict[str, Any]:
    source_mph = Path(mph_file)
    if not source_mph.exists():
        return {"status": "missing", "stage": "prepare", "message": f"COMSOL MPH file not found: {source_mph}"}

    scripts_dir = Path(run_dir) / "scripts"
    validator_java = scripts_dir / "ValidateMphLoadable.java"
    write_comsol_mph_validator_java(validator_java, overwrite=True)

    compile_result = comsol_compile_java(
        str(validator_java),
        run_dir,
        comsol_compile=comsol_compile,
        timeout_sec=min(timeout_sec, 1800),
    )
    if compile_result.get("status") != "completed":
        return {
            "status": compile_result.get("status", "failed"),
            "stage": "compile",
            "mph_file": str(source_mph),
            "validator_java": str(validator_java),
            "compile": compile_result,
        }

    class_path = compiled_class_path(validator_java, "ValidateMphLoadable")
    extra_args = [str(source_mph)]
    if validated_copy:
        extra_args.append(str(validated_copy))
    validate_result = comsol_run_compiled_class(
        str(class_path),
        run_dir,
        comsol_batch=comsol_batch,
        extra_args=extra_args,
        timeout_sec=timeout_sec,
    )
    return {
        "status": validate_result.get("status", "failed"),
        "stage": "validate",
        "mph_file": str(source_mph),
        "validated_copy": validated_copy,
        "validator_java": str(validator_java),
        "class_file": str(class_path),
        "compile": compile_result,
        "validate": validate_result,
    }
