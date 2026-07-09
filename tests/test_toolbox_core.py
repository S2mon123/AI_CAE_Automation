from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai_cae_lab.adapters.comsol import (
    comsol_cube_java_source,
    comsol_mph_validator_java_source,
    comsol_run_java_model_to_mph,
    comsol_validate_mph_loadable,
    compiled_class_path,
    extract_java_public_class,
    write_comsol_cube_java,
)
from ai_cae_lab.config import bridge_plan, load_toolbox_config, toolchain_paths
from ai_cae_lab.context_scope import solver_context_scope
from ai_cae_lab.discovery import (
    discover_ansys_family,
    discover_comsol,
    local_config_from_discovery,
    write_activation_script,
)
from ai_cae_lab.evidence import classify_file, scan_evidence
from ai_cae_lab.logs import analyze_log_text
from ai_cae_lab.mcp_server import build_server, normalize_active_solvers
from ai_cae_lab.runs import create_run, load_run, update_run_status
from ai_cae_lab.templates import write_solver_smoke_template


class ToolboxCoreTests(unittest.TestCase):
    def test_default_config_does_not_load_public_examples(self) -> None:
        config = load_toolbox_config()
        self.assertIsNone(config["_config_path"])
        self.assertEqual(config["solver_paths"], {})

    def test_toolchain_paths_filters_placeholder_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "toolbox.local.json"
            config.write_text(
                '{"solver_paths":{"comsol":{"batch":"<path-to-comsolbatch.exe>","root":"/opt/comsol"}}}',
                encoding="utf-8",
            )
            payload = toolchain_paths("comsol", config)
            self.assertEqual(payload["configured_paths"], {"root": "/opt/comsol"})
            self.assertFalse(payload["config_is_example"])

    def test_top_level_local_config_normalizes_to_solver_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "ai-cae.local.json"
            config.write_text(
                json.dumps({"comsol": {"root": "C:/COMSOL63", "batch": "C:/COMSOL63/comsolbatch.exe"}}),
                encoding="utf-8",
            )
            payload = load_toolbox_config(config)
            self.assertEqual(payload["solver_paths"]["comsol"]["root"], "C:/COMSOL63")
            paths = toolchain_paths("comsol", config)
            self.assertEqual(paths["configured_paths"]["batch"], "C:/COMSOL63/comsolbatch.exe")

    def test_discover_comsol_from_fake_env_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "COMSOL63"
            mp = root / "Multiphysics"
            bin_dir = mp / "bin" / "win64"
            java = mp / "java" / "win64" / "jre" / "bin" / "java.exe"
            api = mp / "doc" / "help" / "wtpwebapps" / "ROOT" / "doc" / "com.comsol.help.comsol" / "api" / "index.html"
            for item in [bin_dir / "comsolbatch.exe", bin_dir / "comsol.exe", bin_dir / "comsolcompile.exe", java, api]:
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_text("", encoding="utf-8")
            env = {
                "COMSOL_ROOT": str(root),
                "COMSOL_BATCH": str(bin_dir / "comsolbatch.exe"),
                "COMSOL_EXE": str(bin_dir / "comsol.exe"),
                "COMSOL_JAVA": str(java),
                "COMSOL_COMPILE": str(bin_dir / "comsolcompile.exe"),
            }
            with patch.dict(os.environ, env, clear=False), patch("ai_cae_lab.discovery._which", return_value=None), patch("ai_cae_lab.discovery._windows_glob", return_value=[]):
                record = discover_comsol()
            self.assertEqual(record.status, "ok")
            self.assertEqual(record.paths["batch"], str((bin_dir / "comsolbatch.exe").resolve()))
            self.assertIn("api_index", record.paths)

    def test_discover_ansys_root_without_executable_is_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ANSYS Inc"
            root.mkdir()
            env = {
                "ANSYS_ROOT": str(root),
                "FLUENT_ROOT": "",
                "FLUENT_EXE": "",
                "WORKBENCH_EXE": "",
                "ANSYS_WORKBENCH_EXE": "",
            }
            with patch.dict(os.environ, env, clear=False), patch("ai_cae_lab.discovery._which", return_value=None), patch("ai_cae_lab.discovery._windows_glob", return_value=[]):
                records = discover_ansys_family()
            self.assertEqual(records["ansys"].status, "partial")
            self.assertEqual(records["fluent"].status, "partial")
            self.assertIn("missing required paths", records["fluent"].messages[0])

    def test_local_config_from_discovery_and_activation_script(self) -> None:
        discovery = {
            "solvers": {
                "comsol": {"paths": {"root": "C:/COMSOL63", "batch": "C:/COMSOL63/bin/comsolbatch.exe"}},
                "abaqus": {"paths": {"command": "C:/SIMULIA/Commands/abaqus.bat"}},
            }
        }
        payload = local_config_from_discovery(discovery)
        self.assertEqual(payload["solver_paths"]["comsol"]["root"], "C:/COMSOL63")
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "ai-cae.local.json"
            script = Path(tmp) / "activate-ai-cae.ps1"
            config.write_text(json.dumps(payload), encoding="utf-8")
            result = write_activation_script(config, script)
            text = Path(result["path"]).read_text(encoding="utf-8")
        self.assertIn("$env:AI_CAE_TOOLBOX_CONFIG", text)
        self.assertIn("$env:COMSOL_BATCH", text)
        self.assertIn("$env:ABAQUS_COMMAND", text)

    def test_solver_context_scope_limits_comsol_files(self) -> None:
        payload = solver_context_scope("comsol")
        scope_paths = {item["path"] for item in payload["scope"]}
        self.assertIn("mcp/comsol", scope_paths)
        self.assertIn("src/ai_cae_lab/adapters/comsol.py", scope_paths)
        self.assertIn("examples/comsol-cube-10mm", scope_paths)
        self.assertNotIn("examples/fluent-sinusoidal-weld-pool", scope_paths)

    def test_mcp_solver_profile_normalization(self) -> None:
        self.assertEqual(normalize_active_solvers("comsol"), {"comsol"})
        self.assertEqual(normalize_active_solvers("ansys"), {"ansys", "fluent", "workbench"})
        self.assertEqual(normalize_active_solvers("pc-schematic"), {"pcschematic"})
        self.assertIsNone(normalize_active_solvers("all"))

    def test_mcp_solver_profile_filters_registered_tools(self) -> None:
        class FakeFastMCP:
            def __init__(self, name: str) -> None:
                self.name = name
                self.tools: list[str] = []

            def tool(self):
                def decorator(func):
                    self.tools.append(func.__name__)
                    return func

                return decorator

        with patch("ai_cae_lab.mcp_server._load_fastmcp", return_value=FakeFastMCP):
            server = build_server("comsol")

        self.assertIn("comsol_check_installation", server.tools)
        self.assertIn("create_run_record", server.tools)
        self.assertNotIn("abaqus_run_no_gui_script", server.tools)
        self.assertNotIn("fluent_run_journal_file", server.tools)

    def test_bridge_plan_contains_comsol_java_tools(self) -> None:
        plan = bridge_plan("comsol", "unit test")
        self.assertIn("comsol_write_cube_smoke_java", plan["recommended_mcp_tools"])
        self.assertIn("comsol_compile_java_file", plan["recommended_mcp_tools"])
        self.assertIn("comsol_run_compiled_java_class", plan["recommended_mcp_tools"])
        self.assertIn("comsol_run_java_model_to_mph_file", plan["recommended_mcp_tools"])

    def test_smoke_template_writes_comsol_cube_java_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = create_run(tmp, "comsol", "comsol smoke", "unit test")
            payload = write_solver_smoke_template("comsol", run["run_dir"], "comsol smoke")
            self.assertEqual(payload["status"], "ok")
            java_files = list((Path(run["run_dir"]) / "scripts").glob("*.java"))
            self.assertEqual(len(java_files), 1)
            text = java_files[0].read_text(encoding="utf-8")
            self.assertIn('geom().create("geom1", 3)', text)
            self.assertIn('create("blk1", "Block")', text)

    def test_evidence_classifies_java_and_detects_failed_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = create_run(tmp, "comsol", "classification", "unit test")
            script = Path(run["run_dir"]) / "scripts" / "Model.java"
            script.write_text("class Model {}", encoding="utf-8")
            log = Path(run["run_dir"]) / "logs" / "comsol_batch.log"
            log.write_text("License error: could not obtain a license\n", encoding="utf-8")
            evidence = scan_evidence(run["run_dir"], write=False)
            self.assertEqual(classify_file(script), "script")
            self.assertIn("script", evidence["counts"])
            self.assertEqual(classify_file(Path(run["run_dir"]) / "run.log"), "run_metadata")
            self.assertEqual(evidence["execution_status"], "license_error")
            self.assertEqual(evidence["credibility_grade"], "failed-run")

    def test_log_parser_success_and_failure_precedence(self) -> None:
        success = analyze_log_text("COMSOL Batch: Done\nRETURN_CODE: 0\n")
        self.assertEqual(success["status"], "success")
        failed = analyze_log_text("RETURN_CODE: 0\nERROR: solver failed to converge\n")
        self.assertEqual(failed["status"], "failed")

    def test_run_status_lifecycle_updates_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = create_run(tmp, "comsol", "status", "unit test")
            update_run_status(run["run_dir"], "running", "pid=123", {"pid": 123})
            update_run_status(run["run_dir"], "completed", "returncode=0")
            payload = load_run(run["run_dir"])
            self.assertEqual(payload["status"], "completed")
            self.assertEqual(payload["metadata"]["pid"], 123)
            self.assertGreaterEqual(len(payload["status_history"]), 2)

    def test_comsol_cube_writer_and_class_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ComsolCube10mm.java"
            payload = write_comsol_cube_java(target)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(extract_java_public_class(target), "ComsolCube10mm")
            self.assertEqual(compiled_class_path(target).name, "ComsolCube10mm.class")
            self.assertIn("Block", comsol_cube_java_source())


    def test_comsol_mph_validator_source_and_missing_file(self) -> None:
        source = comsol_mph_validator_java_source()
        self.assertIn("ModelUtil.load", source)
        self.assertIn("AI_CAE_MPH_LOADABLE", source)
        with tempfile.TemporaryDirectory() as tmp:
            payload = comsol_validate_mph_loadable(str(Path(tmp) / "missing.mph"), tmp)
        self.assertEqual(payload["status"], "missing")
        self.assertEqual(payload["stage"], "prepare")

    def test_log_parser_solver_specific_signals(self) -> None:
        self.assertEqual(analyze_log_text("Abaqus JOB beam COMPLETED\n")["status"], "success")
        self.assertEqual(analyze_log_text("Abaqus JOB beam ABORTED\n")["status"], "failed")
        self.assertEqual(analyze_log_text("Error: Divergence detected in AMG solver\n")["status"], "failed")
        self.assertEqual(analyze_log_text("AI_CAE_MPH_LOADABLE: cube.mph\n")["status"], "success")

    def test_comsol_java_to_mph_stops_when_compile_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            java_file = Path(tmp) / "ComsolCube10mm.java"
            write_comsol_cube_java(java_file)
            with patch("ai_cae_lab.adapters.comsol.resolve_comsol_compile", return_value=None):
                payload = comsol_run_java_model_to_mph(str(java_file), tmp)
            self.assertEqual(payload["stage"], "compile")
            self.assertEqual(payload["status"], "missing")


if __name__ == "__main__":
    unittest.main()
