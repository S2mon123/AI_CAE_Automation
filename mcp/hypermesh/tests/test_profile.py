from __future__ import annotations

import asyncio
import math
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PROFILE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROFILE_DIR.parents[1]
SRC_DIR = REPO_ROOT / "src"
for path in (str(PROFILE_DIR), str(SRC_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import server as hypermesh_server  # noqa: E402
from hypermesh_profile import (  # noqa: E402
    WORKSPACE_ROOTS_ENV,
    list_client_roots,
    manifest,
    plan_circular_feature_mesh,
    plan_fillet_chamfer_mesh,
    plan_flange_mesh,
    plan_partition_strategy,
    plan_size_transition,
    plan_sphere_mesh,
    plan_tetra_hotspot_remediation,
    plan_tetra_quality_remediation,
    plan_tetra_zero_failure_search,
    validate_workspace_paths,
)


class HyperMeshProfileTests(unittest.TestCase):
    def test_server_exposes_tools_resources_and_prompt(self) -> None:
        async def inspect_server() -> tuple[set[str], set[str], set[str], bool]:
            mcp = hypermesh_server.build_server()
            tools = {tool.name for tool in await mcp.list_tools()}
            resources = {str(resource.uri) for resource in await mcp.list_resources()}
            prompts = {prompt.name for prompt in await mcp.list_prompts()}
            return tools, resources, prompts, bool(mcp.instructions)

        tools, resources, prompts, has_instructions = asyncio.run(inspect_server())
        self.assertTrue(has_instructions)
        self.assertTrue(
            {
                "hypermesh_check_installation",
                "hypermesh_run_tcl_file",
                "hypermesh_mcp_manifest",
                "hypermesh_validate_workspace_paths",
                "hypermesh_plan_partition_strategy",
                "hypermesh_plan_size_transition",
                "hypermesh_plan_circular_feature_mesh",
                "hypermesh_plan_fillet_chamfer_mesh",
                "hypermesh_plan_tetra_quality_remediation",
                "hypermesh_plan_tetra_hotspot_remediation",
                "hypermesh_plan_tetra_zero_failure_search",
                "hypermesh_plan_sphere_mesh",
                "hypermesh_plan_flange_mesh",
                "hypermesh_list_client_roots",
            }.issubset(tools)
        )
        self.assertEqual(
            resources,
            {
                "hypermesh://guidance/workflow",
                "hypermesh://guidance/quality-gates",
                "hypermesh://guidance/partition-strategy",
                "hypermesh://guidance/feature-meshing",
                "hypermesh://guidance/fillet-chamfer-meshing",
                "hypermesh://guidance/shape-partition-patterns",
                "hypermesh://guidance/quality-remediation",
                "hypermesh://guidance/tetra-quality-optimization",
                "hypermesh://server/manifest",
            },
        )
        self.assertIn("hypermesh_meshing_plan", prompts)

    def test_feature_resource_is_loaded_from_skill(self) -> None:
        async def read_feature_resource() -> str:
            mcp = hypermesh_server.build_server()
            return str(await mcp.read_resource("hypermesh://guidance/feature-meshing"))

        content = asyncio.run(read_feature_resource())
        self.assertIn("Circular Edges and Cylindrical Surfaces", content)
        self.assertIn("Holes, Washers, and Slots", content)
        self.assertIn("Size Transitions and Biased Edges", content)

    def test_partition_and_remediation_resources_are_loaded_from_skill(self) -> None:
        async def read_resources() -> tuple[str, str]:
            mcp = hypermesh_server.build_server()
            partition = str(await mcp.read_resource("hypermesh://guidance/partition-strategy"))
            remediation = str(await mcp.read_resource("hypermesh://guidance/quality-remediation"))
            return partition, remediation

        partition, remediation = asyncio.run(read_resources())
        self.assertIn("Plan Mapped/Swept Solid Blocks", partition)
        self.assertIn("Terminal-block backtracking", partition)
        self.assertIn("Metric-Specific Remedies", remediation)
        self.assertIn("Repair the highest-level cause first", remediation)

    def test_fillet_chamfer_resource_is_loaded_from_skill(self) -> None:
        async def read_resource() -> str:
            mcp = hypermesh_server.build_server()
            return str(await mcp.read_resource("hypermesh://guidance/fillet-chamfer-meshing"))

        content = asyncio.run(read_resource())
        self.assertIn("Fillet Calculations and Topology", content)
        self.assertIn("Chamfer Calculations and Topology", content)
        self.assertIn("*createfilletmidlines", content)

    def test_tetra_quality_resource_is_loaded_from_skill(self) -> None:
        async def read_resource() -> str:
            mcp = hypermesh_server.build_server()
            return str(await mcp.read_resource("hypermesh://guidance/tetra-quality-optimization"))

        content = asyncio.run(read_resource())
        self.assertIn("hm_getelemcheckvalues", content)
        self.assertIn("Surface-First Remediation Sequence", content)

    def test_shape_partition_resource_is_loaded_from_skill(self) -> None:
        async def read_shape_resource() -> str:
            mcp = hypermesh_server.build_server()
            return str(await mcp.read_resource("hypermesh://guidance/shape-partition-patterns"))

        content = asyncio.run(read_shape_resource())
        self.assertIn("Sphere and Spherical-Shell Pattern", content)
        self.assertIn("Flange and Bolt-Circle Pattern", content)
        self.assertIn("Construction-Line Rules", content)

    def test_circular_feature_plan_rounds_to_symmetry_multiple(self) -> None:
        plan = plan_circular_feature_mesh(
            radius=10.0,
            target_circumferential_size=5.0,
            symmetry_sectors=6,
            multiple_of=4,
            axial_length=21.0,
            target_axial_size=5.0,
            washer_width=6.0,
            target_radial_size=2.5,
            maximum_angle_deg=20.0,
        )
        circumference = 2.0 * math.pi * 10.0
        self.assertEqual(plan["circumferential"]["required_multiple"], 12)
        self.assertEqual(plan["circumferential"]["angle_divisions"], 18)
        self.assertEqual(plan["circumferential"]["divisions"], 24)
        self.assertAlmostEqual(plan["circumferential"]["actual_size"], circumference / 24)
        self.assertEqual(plan["axial"]["divisions"], 5)
        self.assertEqual(plan["radial_washer"]["layers"], 3)

    def test_size_transition_calculates_growth_layers(self) -> None:
        plan = plan_size_transition(
            fine_size=2.0,
            coarse_size=8.0,
            maximum_growth_ratio=1.5,
        )
        self.assertEqual(plan["direction"], "coarsening")
        self.assertEqual(plan["transition_layers"], 4)
        self.assertLessEqual(plan["actual_growth_ratio"], 1.5)
        self.assertGreater(plan["recommended_band_length"], 8.0)

    def test_fillet_plan_combines_size_angle_and_deviation_controls(self) -> None:
        plan = plan_fillet_chamfer_mesh(
            feature_type="round",
            target_size=2.0,
            feature_radius=5.0,
            feature_angle_deg=90.0,
            minimum_rows=3,
            maximum_turn_angle_deg=20.0,
            maximum_chordal_deviation=0.1,
            minimum_element_size=1.0,
            analysis_role="fatigue",
            mesh_route="hex",
        )
        self.assertEqual(plan["inputs"]["feature_type"], "fillet")
        self.assertEqual(plan["calculations"]["size_rows"], 4)
        self.assertEqual(plan["calculations"]["angle_rows"], 5)
        self.assertEqual(plan["calculations"]["chordal_deviation_rows"], 4)
        self.assertEqual(plan["calculations"]["rows"], 5)
        self.assertEqual(plan["decision"], "preserve_and_control")
        self.assertFalse(plan["minimum_size_conflict"])
        self.assertTrue(any("staged source-target" in rule for rule in plan["route_rules"]))

    def test_cosmetic_chamfer_reports_minimum_size_conflict(self) -> None:
        plan = plan_fillet_chamfer_mesh(
            feature_type="bevel",
            target_size=5.0,
            feature_width=3.0,
            feature_angle_deg=45.0,
            minimum_rows=2,
            minimum_element_size=2.0,
            analysis_role="cosmetic",
        )
        self.assertEqual(plan["inputs"]["feature_type"], "chamfer")
        self.assertEqual(plan["calculations"]["rows"], 2)
        self.assertEqual(plan["calculations"]["actual_profile_size"], 1.5)
        self.assertTrue(plan["minimum_size_conflict"])
        self.assertEqual(plan["decision"], "suppress_candidate_review_required")

    def test_fillet_plan_requires_radius(self) -> None:
        with self.assertRaisesRegex(ValueError, "feature_radius"):
            plan_fillet_chamfer_mesh(feature_type="fillet", target_size=2.0)

    def test_sphere_plan_avoids_collapsed_core_and_matches_counts(self) -> None:
        plan = plan_sphere_mesh(
            radius=10.0,
            target_surface_size=2.0,
            maximum_angle_deg=15.0,
            symmetry_sectors=8,
            solid=True,
            core_radius_ratio=0.3,
            target_radial_size=2.0,
            shell_thickness=1.2,
            target_through_thickness_size=0.4,
        )
        self.assertEqual(plan["surface_counts"]["great_circle_divisions"], 32)
        self.assertEqual(plan["surface_counts"]["quarter_arc_divisions"], 8)
        self.assertAlmostEqual(plan["radial_core"]["core_radius"], 3.0)
        self.assertEqual(plan["radial_core"]["outer_radial_layers"], 4)
        self.assertEqual(plan["through_thickness"]["layers"], 3)
        self.assertTrue(any("center" in risk for risk in plan["risks"]))

    def test_flange_plan_measures_bolt_pattern_and_ligaments(self) -> None:
        plan = plan_flange_mesh(
            outer_radius=50.0,
            bore_radius=10.0,
            hub_radius=18.0,
            bolt_circle_radius=35.0,
            bolt_hole_radius=3.0,
            bolt_hole_count=8,
            target_size=4.0,
            maximum_angle_deg=20.0,
            washer_width=2.0,
            flange_thickness=10.0,
            target_axial_size=3.0,
        )
        self.assertEqual(plan["status"], "planned")
        self.assertEqual(plan["bolt_pattern"]["pitch_angle_deg"], 45.0)
        self.assertEqual(plan["bolt_pattern"]["hole_divisions"], 20)
        self.assertEqual(plan["bolt_pattern"]["pitch_circle_divisions"], 64)
        self.assertEqual(plan["axial"]["layers"], 4)
        self.assertEqual(plan["radial_zones"]["construction_ring_radii"], [10.0, 18.0, 30.0, 40.0, 50.0])

    def test_flange_plan_rejects_overlapping_bolt_band(self) -> None:
        with self.assertRaisesRegex(ValueError, "outer rim"):
            plan_flange_mesh(
                outer_radius=36.0,
                bore_radius=10.0,
                bolt_circle_radius=35.0,
                bolt_hole_radius=3.0,
                bolt_hole_count=8,
                target_size=2.0,
            )

    def test_flange_plan_rejects_overlapping_adjacent_holes(self) -> None:
        with self.assertRaisesRegex(ValueError, "adjacent bolt holes"):
            plan_flange_mesh(
                outer_radius=50.0,
                bore_radius=0.0,
                bolt_circle_radius=10.0,
                bolt_hole_radius=8.0,
                bolt_hole_count=8,
                target_size=1.0,
            )

    def test_partition_strategy_builds_mapped_hex_dependencies(self) -> None:
        plan = plan_partition_strategy(
            geometry_summary="symmetric branched cylinder with bolt holes",
            mesh_route="hex",
            has_symmetry=True,
            has_holes_or_slots=True,
            has_branches_or_intersections=True,
            has_curved_sectors=True,
        )
        self.assertEqual(plan["inputs"]["mesh_route"], "mapped_hex")
        self.assertIn("source", plan["block_contract"])
        self.assertTrue(any("terminal" in step.lower() for step in plan["sequence"]))
        self.assertTrue(any("central junction" in rule.lower() for rule in plan["partition_principles"]))
        self.assertTrue(any("mappability" in risk.lower() for risk in plan["risks"]))

    def test_partition_strategy_rejects_unknown_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "mesh_route"):
            plan_partition_strategy("part", "magic_mesh")

    def test_tetra_quality_plan_detects_shared_sliver_cause_and_optimizer_plateau(self) -> None:
        plan = plan_tetra_quality_remediation(
            total_elements=417935,
            target_size=2.0,
            minimum_surface_size=0.4,
            minimum_geometric_feature=0.200195887,
            tet_collapse_fail_count=8,
            tet_collapse_worst=0.062004273,
            aspect_ratio_fail_count=9,
            aspect_ratio_worst=10.7132167,
            volumetric_skew_fail_count=25,
            volumetric_skew_worst=0.999543695,
            minimum_height_fail_count=534,
            minimum_height_worst=0.0316921933,
            minimum_height_overlap_tet_collapse=8,
            minimum_height_overlap_aspect_ratio=9,
            minimum_height_overlap_volumetric_skew=25,
            previous_minimum_height_fail_count=534,
            optimized_minimum_height_fail_count=532,
        )
        self.assertEqual(plan["status"], "blocked")
        self.assertEqual(plan["evidence_status"], "complete")
        self.assertEqual(plan["dominant_metric"], "minimum_height")
        self.assertAlmostEqual(
            plan["size_feasibility"]["batchmesher_global_minimum_planning_baseline"], 0.66
        )
        self.assertLess(plan["optimizer_improvement_fraction"], 0.01)
        self.assertTrue(any("contained" in signal for signal in plan["cause_signals"]))
        self.assertTrue(any("less than 1%" in signal for signal in plan["cause_signals"]))

    def test_tetra_quality_plan_requires_worst_values_for_failed_metrics(self) -> None:
        plan = plan_tetra_quality_remediation(
            total_elements=100,
            target_size=2.0,
            minimum_surface_size=0.8,
            minimum_height_fail_count=2,
        )
        self.assertEqual(plan["evidence_status"], "incomplete")
        self.assertEqual(plan["missing_worst_values"], ["minimum_height"])

    def test_tetra_hotspot_plan_blocks_blind_refinement_for_boundary_height_failures(self) -> None:
        plan = plan_tetra_hotspot_remediation(
            total_elements=355651,
            failed_element_count=114,
            hotspot_count=20,
            boundary_associated_failure_count=113,
            two_or_more_boundary_nodes_count=109,
            three_or_more_boundary_nodes_count=74,
            target_size=2.0,
            minimum_surface_size=0.66,
            minimum_height_fail_count=102,
            minimum_height_worst=0.0485968427,
            tet_collapse_fail_count=3,
            aspect_ratio_fail_count=19,
            volumetric_skew_fail_count=18,
            dominant_hotspot_element_count=37,
            minimum_failed_tet_edge=0.100578736,
            minimum_associated_geometry_edge=2.05803465,
        )
        self.assertEqual(plan["classification"], "boundary_topology_driven")
        self.assertTrue(plan["refinement_gate"]["blind_refinement_blocked"])
        self.assertEqual(
            plan["first_action"],
            "regularize_or_coarsen_boundary_sampling_before_any_refinement",
        )
        self.assertEqual(
            plan["diagnosis"]["geometry_edge_signal"],
            "mesh_sampling_or_boundary_tria_conflict",
        )
        self.assertEqual(
            [row["minimum_size"] for row in plan["parameter_search"]],
            [0.5, 0.55, 0.6, 0.66],
        )
        self.assertTrue(plan["acceptance_contract"]["rollback_on_any_active_metric_regression"])

    def test_tetra_hotspot_plan_routes_interior_failures_to_fixed_boundary_optimization(self) -> None:
        plan = plan_tetra_hotspot_remediation(
            total_elements=1000,
            failed_element_count=10,
            hotspot_count=3,
            boundary_associated_failure_count=2,
            two_or_more_boundary_nodes_count=1,
            three_or_more_boundary_nodes_count=0,
            target_size=2.0,
            minimum_surface_size=0.8,
            aspect_ratio_fail_count=10,
            dominant_hotspot_element_count=5,
        )
        self.assertEqual(plan["classification"], "interior_node_or_connectivity_driven")
        self.assertEqual(plan["first_action"], "fixed_boundary_local_tetra_optimization")
        self.assertFalse(plan["refinement_gate"]["blind_refinement_blocked"])

    def test_zero_failure_search_escalates_boundary_plateau_to_shape_preserving_morph(self) -> None:
        plan = plan_tetra_zero_failure_search(
            total_elements=355383,
            unique_failed_element_count=100,
            hotspot_count=21,
            boundary_associated_failure_count=100,
            two_or_more_boundary_nodes_count=99,
            tet_collapse_fail_count=2,
            aspect_ratio_fail_count=16,
            volumetric_skew_fail_count=5,
            minimum_height_fail_count=91,
            minimum_height_worst=0.0580368119,
            plateau_detected=True,
        )
        self.assertEqual(plan["phase"], "shape_preserving_boundary_escalation")
        self.assertFalse(plan["acceptance_contract"]["quality_acceptance_pass"])
        boundary_route = " ".join(plan["residual_routes"]["boundary_plateau"])
        interior_route = " ".join(
            plan["residual_routes"]["interior_skew_or_connectivity_residual"]
        )
        self.assertIn("*morphsmoothmorphbased", boundary_route)
        self.assertIn("mode 6", interior_route)
        self.assertIn("min_height active", interior_route)

    def test_zero_failure_quality_pass_does_not_hide_geometry_tolerance_failure(self) -> None:
        plan = plan_tetra_zero_failure_search(
            total_elements=355383,
            unique_failed_element_count=0,
            hotspot_count=0,
            boundary_associated_failure_count=0,
            two_or_more_boundary_nodes_count=0,
            tet_collapse_worst=0.101912525,
            aspect_ratio_worst=5.168739577,
            volumetric_skew_worst=0.934614759,
            minimum_height_worst=0.200055174,
            observed_maximum_boundary_displacement=1.432328839,
            maximum_allowed_boundary_displacement=0.5,
        )
        self.assertTrue(plan["acceptance_contract"]["quality_acceptance_pass"])
        self.assertEqual(plan["geometry_evidence"]["status"], "fail")
        self.assertFalse(plan["acceptance_contract"]["simulation_acceptance_pass"])

    def test_zero_failure_requires_explicit_geometry_tolerance_for_simulation_acceptance(self) -> None:
        plan = plan_tetra_zero_failure_search(
            total_elements=100,
            unique_failed_element_count=0,
            hotspot_count=0,
            boundary_associated_failure_count=0,
            two_or_more_boundary_nodes_count=0,
            tet_collapse_worst=0.12,
            aspect_ratio_worst=4.0,
            volumetric_skew_worst=0.90,
            minimum_height_worst=0.22,
            observed_maximum_boundary_displacement=0.04,
        )
        self.assertEqual(plan["status"], "accepted")
        self.assertEqual(
            plan["geometry_evidence"]["status"],
            "measured_tolerance_not_defined",
        )
        self.assertFalse(plan["acceptance_contract"]["simulation_acceptance_pass"])

    def test_circular_feature_plan_rejects_partial_axial_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "axial_length"):
            plan_circular_feature_mesh(
                radius=10.0,
                target_circumferential_size=2.0,
                axial_length=20.0,
            )

    def test_workspace_policy_blocks_path_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as outside_dir:
            root = Path(temp_dir)
            script = root / "scripts" / "mesh.tcl"
            script.parent.mkdir()
            script.write_text("# smoke", encoding="utf-8")
            outside_run = Path(outside_dir) / "run"
            policy = validate_workspace_paths(str(script), str(outside_run), str(root))

        self.assertEqual(policy["status"], "blocked")
        self.assertFalse(policy["allowed"])
        self.assertTrue(policy["checks"]["script_path"]["within_configured_root"])
        self.assertFalse(policy["checks"]["run_dir"]["within_configured_root"])

    def test_workspace_policy_uses_environment_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script = root / "mesh.tcl"
            script.write_text("# smoke", encoding="utf-8")
            with patch.dict("os.environ", {WORKSPACE_ROOTS_ENV: str(root)}, clear=False):
                policy = validate_workspace_paths(str(script), str(root / "run"))
        self.assertTrue(policy["allowed"])
        self.assertTrue(policy["enforced"])

    def test_roots_are_optional_client_capability(self) -> None:
        fake_context = SimpleNamespace(
            session=SimpleNamespace(client_params=SimpleNamespace(capabilities=SimpleNamespace(roots=None)))
        )
        result = asyncio.run(list_client_roots(fake_context))
        self.assertEqual(result["status"], "unsupported")
        self.assertIn("client", result["message"])
        self.assertIn("deprecated", result["message"])

    def test_manifest_distinguishes_server_and_client_features(self) -> None:
        payload = manifest()
        self.assertEqual(payload["transport"], "stdio")
        self.assertIn("resources", payload["server_primitives"])
        self.assertEqual(
            payload["protocol_handling"]["client_roots"], "optional compatibility query; advisory and deprecated"
        )
        self.assertFalse(payload["path_policy"]["client_roots_enforced"])


if __name__ == "__main__":
    unittest.main()
