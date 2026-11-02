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
from ai_cae_lab.adapters.mechanical import mechanical_validate_result_summary
from ai_cae_lab.adapters.ovito import ovito_check_install
from ai_cae_lab.adapters.aedt import aedt_check_install
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
        self.assertEqual(
            normalize_active_solvers("ansys"),
            {"ansys", "aedt", "fluent", "workbench", "mechanical"},
        )
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

    def test_new_mcp_profiles_expose_only_their_solver_tools(self) -> None:
        class FakeFastMCP:
            def __init__(self, name: str) -> None:
                self.name = name
                self.tools: list[str] = []

            def tool(self):
                def decorator(func):
                    self.tools.append(func.__name__)
                    return func

                return decorator

        cases = {
            "aedt": ("aedt_check_installation", "lammps_run_input_file"),
            "mechanical": ("mechanical_validate_result_summary_file", "aedt_run_pyaedt_script_file"),
            "hypermesh": ("hypermesh_run_tcl_file", "ovito_run_script_file"),
            "lammps": ("lammps_run_input_file", "hypermesh_run_tcl_file"),
            "ovito": ("ovito_run_script_file", "mechanical_run_python_controller_file"),
        }
        for profile, (included, excluded) in cases.items():
            with patch("ai_cae_lab.mcp_server._load_fastmcp", return_value=FakeFastMCP):
                server = build_server(profile)
            self.assertIn(included, server.tools)
            self.assertIn("create_run_record", server.tools)
            self.assertNotIn(excluded, server.tools)

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

    def test_log_parser_does_not_treat_mesh_quality_findings_as_execution_failure(self) -> None:
        parsed = analyze_log_text(
            "classification=boundary-driven cluster: most failed tets have 2-4 geometry-associated nodes\n"
            "failure_count=91\n"
            "completed=true\n"
            "RETURN_CODE: 0\n"
        )
        self.assertEqual(parsed["status"], "success")
        self.assertFalse(any(signal["category"] == "failure" for signal in parsed["signals"]))

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

    def test_new_solver_bridge_plans_and_contexts_are_complete(self) -> None:
        expected_tools = {
            "aedt": "aedt_check_installation",
            "ansys-mechanical": "mechanical_validate_result_summary_file",
            "hypermesh": "hypermesh_run_tcl_file",
            "lammps": "lammps_run_input_file",
            "ovito": "ovito_run_script_file",
        }
        for solver, tool in expected_tools.items():
            plan = bridge_plan(solver, "coverage")
            self.assertIn(tool, plan["recommended_mcp_tools"])
            self.assertFalse(solver_context_scope(solver)["missing"])

    def test_new_solver_smoke_templates_are_written(self) -> None:
        for solver, expected in {
            "aedt": "aedt_connection_probe.py",
            "ansys-mechanical": "mechanical_probe.py",
            "hypermesh": "hypermesh_smoke.tcl",
            "lammps": "in.lammps_smoke",
            "ovito": "ovito_connection_probe.py",
        }.items():
            with tempfile.TemporaryDirectory() as tmp:
                run = create_run(tmp, solver, "smoke", "template coverage")
                payload = write_solver_smoke_template(solver, run["run_dir"], "smoke")
                self.assertEqual(payload["status"], "ok")
                self.assertTrue((Path(run["run_dir"]) / "scripts" / expected).exists())

    def test_mechanical_result_summary_requires_all_evidence_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "logs").mkdir()
            (root / "outputs").mkdir()
            (root / "exports").mkdir()
            (root / "logs" / "solve.out").write_text("MAPDL normal termination\n", encoding="utf-8")
            (root / "outputs" / "file.rst").write_bytes(b"rst")
            (root / "exports" / "results.csv").write_text("value\n1\n", encoding="utf-8")
            (root / "exports" / "deformation.png").write_bytes(b"png")
            summary = root / "results-summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "analysis_object_state": "Solved",
                        "normal_mapdl_termination": True,
                        "reaction_balance_error_percent": 0.5,
                        "mesh_quality": {"element_count": 10, "failed_element_count": 0},
                        "result_file": "outputs/file.rst",
                        "solve_log_file": "logs/solve.out",
                        "numeric_exports": ["exports/results.csv"],
                        "image_exports": ["exports/deformation.png"],
                    }
                ),
                encoding="utf-8",
            )
            payload = mechanical_validate_result_summary(str(summary))
            self.assertEqual(payload["status"], "ok")

    def test_aedt_and_ovito_checks_do_not_claim_solver_from_gui_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gui = Path(tmp) / "gui.exe"
            gui.write_bytes(b"")
            with patch("ai_cae_lab.adapters.aedt.resolve_aedt_exe", return_value=str(gui)), patch(
                "ai_cae_lab.adapters.aedt.resolve_pyaedt_python", return_value=None
            ):
                self.assertEqual(aedt_check_install()["status"], "partial")
            with patch("ai_cae_lab.adapters.ovito.resolve_ovito_gui", return_value=str(gui)), patch(
                "ai_cae_lab.adapters.ovito.resolve_ovito_script_command", return_value=None
            ):
                payload = ovito_check_install()
            self.assertEqual(payload["status"], "partial")
            self.assertTrue(payload["capabilities"]["interactive_gui"])
            self.assertFalse(payload["capabilities"]["batch_python"])

    def test_mechanical_install_check_accepts_one_real_control_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workbench = Path(tmp) / "RunWB2.exe"
            workbench.write_bytes(b"")
            with patch("ai_cae_lab.adapters.mechanical.resolve_workbench_command", return_value=str(workbench)), patch(
                "ai_cae_lab.adapters.mechanical.resolve_mechanical_python", return_value=None
            ):
                from ai_cae_lab.adapters.mechanical import mechanical_check_install

                payload = mechanical_check_install()
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["available_routes"], ["Workbench RunWB2 journal / Mechanical ExtAPI"])


if __name__ == "__main__":
    unittest.main()
