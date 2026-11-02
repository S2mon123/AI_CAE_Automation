from __future__ import annotations

import asyncio
import importlib.metadata
import math
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.exceptions import ToolError


PROFILE = "hypermesh"
WORKSPACE_ROOTS_ENV = "AI_CAE_HYPERMESH_WORKSPACE_ROOTS"

SERVER_INSTRUCTIONS = """HyperMesh evidence-first MCP profile.

Use a run directory, preserve source CAD, and treat CAD import, nonzero entity
and element counts, mesh quality, and solver-deck export as independent gates.
Read the partition, feature-meshing, fillet/chamfer, shape-partition, quality-
remediation, and tetra-quality resources before writing cut or meshing Tcl. Prove measured
construction geometry, mapped/swept block topology, shared-face dependencies,
local transitions, and solver-specific quality gates. Client roots are
advisory; use workspace_root or AI_CAE_HYPERMESH_WORKSPACE_ROOTS for path
enforcement.
"""

ROOTS_NOTE = (
    "MCP roots are declared by the client and queried by the server; they are not "
    "a server primitive or an access-control boundary. Roots remain available for "
    "2025-11-25 compatibility but are deprecated in the 2026 protocol revision."
)


def _find_repo_root() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "ai_cae_lab").is_dir() and (parent / "codex-skills").is_dir():
            return parent
    return None


def _read_skill_file(relative_path: str, fallback: str) -> str:
    root = _find_repo_root()
    if root is None:
        return fallback
    path = root / "codex-skills" / "hypermesh-evidence-meshing" / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return fallback


def _split_workspace_roots(value: str | None) -> list[Path]:
    if not value:
        return []
    # The public examples target Windows, where os.pathsep is ';'. Accept newlines
    # too so environment configuration stays readable on every platform.
    normalized = value.replace("\r", "\n").replace("\n", os.pathsep)
    roots: list[Path] = []
    for item in normalized.split(os.pathsep):
        item = item.strip()
        if item:
            roots.append(Path(item).expanduser().resolve(strict=False))
    return roots


def configured_workspace_roots(workspace_root: str | None = None) -> list[Path]:
    if workspace_root:
        return [Path(workspace_root).expanduser().resolve(strict=False)]
    return _split_workspace_roots(os.environ.get(WORKSPACE_ROOTS_ENV))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_workspace_paths(
    script_path: str,
    run_dir: str,
    workspace_root: str | None = None,
) -> dict[str, Any]:
    roots = configured_workspace_roots(workspace_root)
    resolved = {
        "script_path": Path(script_path).expanduser().resolve(strict=False),
        "run_dir": Path(run_dir).expanduser().resolve(strict=False),
    }
    checks: dict[str, dict[str, Any]] = {}
    for name, path in resolved.items():
        matching_root = next((root for root in roots if _is_within(path, root)), None)
        checks[name] = {
            "path": str(path),
            "exists": path.exists(),
            "within_configured_root": bool(matching_root) if roots else None,
            "matching_root": str(matching_root) if matching_root else None,
        }

    allowed = not roots or all(item["within_configured_root"] for item in checks.values())
    return {
        "status": "ok" if allowed else "blocked",
        "allowed": allowed,
        "enforced": bool(roots),
        "configured_roots": [str(root) for root in roots],
        "checks": checks,
        "message": (
            "Both paths are inside an explicitly configured workspace root."
            if roots and allowed
            else "At least one path is outside the explicitly configured workspace root."
            if roots
            else f"No path boundary is configured. Set workspace_root or {WORKSPACE_ROOTS_ENV}."
        ),
    }


def _client_capability(ctx: Context, name: str) -> Any:
    client_params = getattr(ctx.session, "client_params", None)
    capabilities = getattr(client_params, "capabilities", None)
    return getattr(capabilities, name, None)


async def list_client_roots(ctx: Context) -> dict[str, Any]:
    if _client_capability(ctx, "roots") is None:
        return {"status": "unsupported", "roots": [], "message": ROOTS_NOTE}
    try:
        result = await ctx.session.list_roots()
    except Exception as exc:  # The client may advertise but reject the legacy request.
        return {
            "status": "unavailable",
            "roots": [],
            "message": f"Client roots request failed: {exc}. {ROOTS_NOTE}",
        }
    roots = [{"uri": str(root.uri), "name": root.name} for root in getattr(result, "roots", [])]
    return {"status": "ok", "roots": roots, "message": ROOTS_NOTE}


def _sdk_version() -> str:
    try:
        return importlib.metadata.version("mcp")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def manifest() -> dict[str, Any]:
    return {
        "name": "ai-cae-automation-lab-hypermesh",
        "profile": PROFILE,
        "sdk": {"package": "mcp", "version": _sdk_version(), "supported_major": 1},
        "transport": "stdio",
        "server_primitives": {
            "tools": [
                "hypermesh_check_installation",
                "hypermesh_run_tcl_file",
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
                "hypermesh_mcp_manifest",
            ],
            "resources": [
                "hypermesh://guidance/workflow",
                "hypermesh://guidance/quality-gates",
                "hypermesh://guidance/partition-strategy",
                "hypermesh://guidance/feature-meshing",
                "hypermesh://guidance/fillet-chamfer-meshing",
                "hypermesh://guidance/shape-partition-patterns",
                "hypermesh://guidance/quality-remediation",
                "hypermesh://guidance/tetra-quality-optimization",
                "hypermesh://server/manifest",
            ],
            "prompts": ["hypermesh_meshing_plan"],
        },
        "protocol_handling": {
            "base_protocol": "provided by the official Python SDK",
            "lifecycle_and_capability_negotiation": "provided by the official Python SDK",
            "structured_tool_output": True,
            "logging_and_progress": "used by hypermesh_run_tcl_file when supported by the client",
            "client_roots": "optional compatibility query; advisory and deprecated",
            "sampling": "not required; no server-to-client LLM calls",
            "elicitation": "not required; all execution inputs are explicit tool arguments",
            "authentication": "not required for local stdio; add OAuth before exposing an HTTP transport",
        },
        "path_policy": {
            "environment": WORKSPACE_ROOTS_ENV,
            "tool_argument": "workspace_root",
            "client_roots_enforced": False,
        },
    }


def plan_circular_feature_mesh(
    radius: float,
    target_circumferential_size: float,
    minimum_circumferential_divisions: int = 8,
    multiple_of: int = 4,
    symmetry_sectors: int = 1,
    axial_length: float | None = None,
    target_axial_size: float | None = None,
    washer_width: float | None = None,
    target_radial_size: float | None = None,
    maximum_angle_deg: float | None = None,
) -> dict[str, Any]:
    numeric_positive = {
        "radius": radius,
        "target_circumferential_size": target_circumferential_size,
    }
    for name, value in numeric_positive.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
    for name, value in {
        "minimum_circumferential_divisions": minimum_circumferential_divisions,
        "multiple_of": multiple_of,
        "symmetry_sectors": symmetry_sectors,
    }.items():
        if value < 1:
            raise ValueError(f"{name} must be at least one")

    circumference = 2.0 * math.pi * radius
    size_divisions = math.ceil(circumference / target_circumferential_size)
    angle_divisions = 0
    if maximum_angle_deg is not None:
        if maximum_angle_deg <= 0 or maximum_angle_deg > 360:
            raise ValueError("maximum_angle_deg must be greater than zero and no more than 360")
        angle_divisions = math.ceil(360.0 / maximum_angle_deg)
    raw_circumferential = max(
        minimum_circumferential_divisions,
        size_divisions,
        angle_divisions,
    )
    required_multiple = math.lcm(multiple_of, symmetry_sectors)
    circumferential_divisions = math.ceil(raw_circumferential / required_multiple) * required_multiple

    result: dict[str, Any] = {
        "status": "planned",
        "inputs": {
            "radius": radius,
            "target_circumferential_size": target_circumferential_size,
            "minimum_circumferential_divisions": minimum_circumferential_divisions,
            "multiple_of": multiple_of,
            "symmetry_sectors": symmetry_sectors,
            "axial_length": axial_length,
            "target_axial_size": target_axial_size,
            "washer_width": washer_width,
            "target_radial_size": target_radial_size,
            "maximum_angle_deg": maximum_angle_deg,
        },
        "circumferential": {
            "circumference": circumference,
            "size_divisions": size_divisions,
            "angle_divisions": angle_divisions or None,
            "raw_divisions": raw_circumferential,
            "required_multiple": required_multiple,
            "divisions": circumferential_divisions,
            "actual_size": circumference / circumferential_divisions,
        },
        "axial": None,
        "radial_washer": None,
        "acceptance_note": (
            "Planning baseline only. Increase density for curvature accuracy, higher-order elements, "
            "contact, bending/ovalization, stress gradients, or solver-specific requirements."
        ),
    }

    if axial_length is not None or target_axial_size is not None:
        if axial_length is None or target_axial_size is None or axial_length <= 0 or target_axial_size <= 0:
            raise ValueError("axial_length and target_axial_size must both be greater than zero")
        axial_divisions = math.ceil(axial_length / target_axial_size)
        result["axial"] = {
            "divisions": axial_divisions,
            "actual_size": axial_length / axial_divisions,
        }

    if washer_width is not None or target_radial_size is not None:
        if washer_width is None or target_radial_size is None or washer_width <= 0 or target_radial_size <= 0:
            raise ValueError("washer_width and target_radial_size must both be greater than zero")
        radial_layers = math.ceil(washer_width / target_radial_size)
        result["radial_washer"] = {
            "layers": radial_layers,
            "actual_size": washer_width / radial_layers,
        }

    return result


def plan_fillet_chamfer_mesh(
    feature_type: str,
    target_size: float,
    feature_radius: float | None = None,
    feature_width: float | None = None,
    feature_angle_deg: float = 90.0,
    minimum_rows: int = 2,
    maximum_turn_angle_deg: float = 20.0,
    maximum_chordal_deviation: float | None = None,
    minimum_element_size: float | None = None,
    maximum_growth_ratio: float = 1.5,
    analysis_role: str = "cosmetic",
    mesh_route: str = "shell",
) -> dict[str, Any]:
    """Plan measurable profile rows and decisions for a fillet or chamfer.

    The function never authorizes geometry removal. It identifies candidates,
    numeric conflicts, topology actions, and the evidence needed for a reviewed
    preserve/defeature decision.
    """
    normalized_type = feature_type.strip().lower().replace("-", "_").replace(" ", "_")
    type_aliases = {
        "round": "fillet",
        "rounded_edge": "fillet",
        "edge_blend": "fillet",
        "blend": "fillet",
        "bevel": "chamfer",
    }
    normalized_type = type_aliases.get(normalized_type, normalized_type)
    if normalized_type not in {"fillet", "chamfer"}:
        raise ValueError("feature_type must resolve to fillet or chamfer")

    normalized_route = mesh_route.strip().lower().replace("-", "_").replace(" ", "_")
    route_aliases = {
        "quad": "shell",
        "quad_shell": "shell",
        "midsurface": "shell",
        "hex": "mapped_hex",
        "hexa": "mapped_hex",
        "solid_map": "mapped_hex",
        "tet": "tetra",
    }
    normalized_route = route_aliases.get(normalized_route, normalized_route)
    if normalized_route not in {"shell", "mapped_hex", "tetra"}:
        raise ValueError("mesh_route must resolve to shell, mapped_hex, or tetra")

    if target_size <= 0:
        raise ValueError("target_size must be greater than zero")
    if minimum_rows < 1:
        raise ValueError("minimum_rows must be at least one")
    if not 0 < feature_angle_deg < 360:
        raise ValueError("feature_angle_deg must be greater than zero and less than 360")
    if not 0 < maximum_turn_angle_deg <= 180:
        raise ValueError("maximum_turn_angle_deg must be greater than zero and no more than 180")
    if maximum_chordal_deviation is not None and maximum_chordal_deviation <= 0:
        raise ValueError("maximum_chordal_deviation must be greater than zero")
    if minimum_element_size is not None and minimum_element_size <= 0:
        raise ValueError("minimum_element_size must be greater than zero")
    if maximum_growth_ratio <= 1:
        raise ValueError("maximum_growth_ratio must be greater than one")

    warnings: list[str] = []
    calculations: dict[str, Any]
    measured_width_difference: float | None = None

    if normalized_type == "fillet":
        if feature_radius is None or feature_radius <= 0:
            raise ValueError("feature_radius must be greater than zero for a fillet")
        if feature_width is not None and feature_width <= 0:
            raise ValueError("feature_width must be greater than zero when provided")

        theta = math.radians(feature_angle_deg)
        arc_width = feature_radius * theta
        size_rows = math.ceil(arc_width / target_size)
        angle_rows = math.ceil(feature_angle_deg / maximum_turn_angle_deg)
        deviation_rows = 0
        if maximum_chordal_deviation is not None:
            if maximum_chordal_deviation >= feature_radius:
                deviation_rows = 1
            else:
                deviation_rows = math.ceil(
                    theta / (2.0 * math.acos(1.0 - maximum_chordal_deviation / feature_radius))
                )
        rows = max(minimum_rows, size_rows, angle_rows, deviation_rows)
        actual_chord = 2.0 * feature_radius * math.sin(theta / (2.0 * rows))
        actual_deviation = feature_radius * (1.0 - math.cos(theta / (2.0 * rows)))
        actual_profile_size = arc_width / rows

        if feature_width is not None:
            measured_width_difference = feature_width - arc_width
            if abs(measured_width_difference) > max(1e-9, 0.1 * arc_width):
                warnings.append(
                    "Measured feature_width differs from the constant-radius arc width by more than 10%; "
                    "review variable radius, trimming, and feature continuity."
                )

        calculations = {
            "radius": feature_radius,
            "angle_deg": feature_angle_deg,
            "angle_rad": theta,
            "calculated_arc_width": arc_width,
            "measured_feature_width": feature_width,
            "measured_minus_calculated_width": measured_width_difference,
            "size_rows": size_rows,
            "angle_rows": angle_rows,
            "chordal_deviation_rows": deviation_rows or None,
            "rows": rows,
            "actual_arc_size": actual_profile_size,
            "actual_chord_length": actual_chord,
            "actual_chordal_deviation": actual_deviation,
        }
        profile_width = arc_width
        controlling_size = actual_chord
        realization = [
            "Use curvature-aware edge seeding on the retained profile and match longitudinal edge counts.",
            "Consider a longitudinal centerline split only when it improves row flow without short end edges.",
            "For reviewed removal, preview the selected chain and verify *removeedgefillets against installed help.",
            "For a retained split, derive *createfilletmidlines radius/width bounds from measured geometry.",
        ]
    else:
        if feature_width is None or feature_width <= 0:
            raise ValueError("feature_width must be greater than zero for a chamfer")
        if feature_radius is not None:
            warnings.append("feature_radius is ignored for a planar chamfer; use feature_width across the face.")

        size_rows = math.ceil(feature_width / target_size)
        rows = max(minimum_rows, size_rows)
        actual_profile_size = feature_width / rows
        calculations = {
            "measured_feature_width": feature_width,
            "included_angle_deg": feature_angle_deg,
            "size_rows": size_rows,
            "rows": rows,
            "actual_profile_size": actual_profile_size,
        }
        profile_width = feature_width
        controlling_size = actual_profile_size
        realization = [
            "Treat the chamfer as a narrow planar band and extend both endpoints into deliberate patch boundaries.",
            "Match the two long-edge counts and create the profile rows before meshing neighboring regions.",
            "For reviewed suppression, merge/suppress bounding topology only after adjacent faces reconstruct cleanly.",
            "Do not assume chamfers are exposed as a dedicated detected feature in every HyperMesh release.",
        ]
        if feature_angle_deg < 30 or feature_angle_deg > 150:
            warnings.append("The chamfer angle is acute/obtuse enough to risk a wedge or sliver residual block.")

    role = analysis_role.strip().lower().replace("-", "_").replace(" ", "_") or "unspecified"
    cosmetic_roles = {"cosmetic", "decorative", "non_structural", "negligible"}
    physics_critical = role not in cosmetic_roles
    minimum_size_conflict = bool(
        minimum_element_size is not None and controlling_size < minimum_element_size
    )

    if physics_critical:
        decision = "preserve_and_control"
        decision_reason = (
            "The declared analysis role is not cosmetic; retain the feature unless a sensitivity study "
            "and boundary/contact audit justify another representation."
        )
    elif minimum_size_conflict or profile_width < target_size:
        decision = "suppress_candidate_review_required"
        decision_reason = (
            "The cosmetic feature is smaller than the global target or its planned spacing conflicts with "
            "minimum size. Review defeaturing and compare retained/simplified results; do not auto-delete."
        )
    else:
        decision = "preserve_or_suppress_after_sensitivity_review"
        decision_reason = (
            "The feature is representable at the current baseline, but its cosmetic classification alone "
            "does not prove that removal is harmless."
        )

    if minimum_element_size is None:
        warnings.append("Provide the solver minimum element size before final acceptance.")
    elif minimum_size_conflict:
        warnings.append(
            "The planned profile spacing is below minimum_element_size; revise rows/criteria, use an "
            "appropriate idealization, or review suppression."
        )
    if minimum_rows < 2:
        warnings.append("A one-row retained profile needs explicit formulation and convergence evidence.")

    transition: dict[str, Any] | None = None
    if controlling_size < target_size and not math.isclose(controlling_size, target_size):
        overall_ratio = target_size / controlling_size
        transition_layers = math.ceil(math.log(overall_ratio) / math.log(maximum_growth_ratio))
        actual_growth = overall_ratio ** (1.0 / transition_layers)
        transition = {
            "fine_size": controlling_size,
            "coarse_size": target_size,
            "maximum_growth_ratio": maximum_growth_ratio,
            "layers": transition_layers,
            "actual_growth_ratio": actual_growth,
            "recommended_band_length": sum(
                controlling_size * actual_growth**index for index in range(1, transition_layers + 1)
            ),
        }

    route_rules = {
        "shell": [
            "Decide whether the physical edge treatment belongs in the midsurface idealization.",
            "Keep singularities and size transitions away from tangency endpoints and peak gradients.",
        ],
        "mapped_hex": [
            "Isolate the shoulder/fillet/chamfer transition as a staged source-target block.",
            "Match shared-face counts and verify source quality, scaled Jacobian, aspect, and warpage after each sweep.",
        ],
        "tetra": [
            "Prefer curvature/proximity-controlled boundary meshing over hex-style over-partitioning.",
            "Verify a closed surface, boundary triangle quality, and tet collapse around the retained feature.",
        ],
    }

    return {
        "status": "planned",
        "inputs": {
            "feature_type": normalized_type,
            "target_size": target_size,
            "feature_radius": feature_radius,
            "feature_width": feature_width,
            "feature_angle_deg": feature_angle_deg,
            "minimum_rows": minimum_rows,
            "maximum_turn_angle_deg": maximum_turn_angle_deg,
            "maximum_chordal_deviation": maximum_chordal_deviation,
            "minimum_element_size": minimum_element_size,
            "maximum_growth_ratio": maximum_growth_ratio,
            "analysis_role": role,
            "mesh_route": normalized_route,
        },
        "decision": decision,
        "decision_reason": decision_reason,
        "calculations": calculations,
        "minimum_size_conflict": minimum_size_conflict,
        "transition": transition,
        "realization": realization,
        "route_rules": route_rules[normalized_route],
        "warnings": warnings,
        "acceptance_evidence": [
            "Feature IDs, measured radius/width/angle, continuity, role, and protected entity sets.",
            "Derived rows, actual profile/chord size, chordal deviation, matching counts, and transition layers.",
            "Before/after topology counts, free/shared/non-manifold edges, shortest edge, and area/volume change.",
            "Localized minimum length, aspect, skew, warpage, angle, Jacobian, and solver-specific failures.",
            "Retained-versus-suppressed sensitivity evidence when stress, contact, stiffness, sealing, or fatigue may change.",
        ],
        "acceptance_note": (
            "This planner does not remove geometry. Resolve commands against installed HyperMesh help and "
            "accept only after protected-boundary, topology, quality, and sensitivity evidence is complete."
        ),
    }


def plan_sphere_mesh(
    radius: float,
    target_surface_size: float,
    maximum_angle_deg: float = 15.0,
    symmetry_sectors: int = 8,
    minimum_great_circle_divisions: int = 24,
    solid: bool = True,
    core_radius_ratio: float = 0.3,
    target_radial_size: float | None = None,
    shell_thickness: float | None = None,
    target_through_thickness_size: float | None = None,
) -> dict[str, Any]:
    if radius <= 0 or target_surface_size <= 0:
        raise ValueError("radius and target_surface_size must be greater than zero")
    if maximum_angle_deg <= 0 or maximum_angle_deg > 90:
        raise ValueError("maximum_angle_deg must be greater than zero and no more than 90")
    if symmetry_sectors < 1 or minimum_great_circle_divisions < 4:
        raise ValueError("symmetry_sectors must be at least one and minimum divisions at least four")
    if solid and not 0.1 <= core_radius_ratio <= 0.6:
        raise ValueError("core_radius_ratio must be between 0.1 and 0.6 for a solid sphere")
    if target_radial_size is not None and target_radial_size <= 0:
        raise ValueError("target_radial_size must be greater than zero")
    if shell_thickness is not None or target_through_thickness_size is not None:
        if (
            shell_thickness is None
            or target_through_thickness_size is None
            or shell_thickness <= 0
            or target_through_thickness_size <= 0
        ):
            raise ValueError("shell_thickness and target_through_thickness_size must both be greater than zero")
        if shell_thickness >= radius:
            raise ValueError("shell_thickness must be smaller than radius")

    circumference = 2.0 * math.pi * radius
    size_divisions = math.ceil(circumference / target_surface_size)
    angle_divisions = math.ceil(360.0 / maximum_angle_deg)
    required_multiple = math.lcm(4, symmetry_sectors)
    raw_divisions = max(minimum_great_circle_divisions, size_divisions, angle_divisions)
    great_circle_divisions = math.ceil(raw_divisions / required_multiple) * required_multiple

    radial: dict[str, Any] | None = None
    if solid:
        core_radius = radius * core_radius_ratio
        outer_span = radius - core_radius
        radial_size = target_radial_size or target_surface_size
        radial_layers = max(1, math.ceil(outer_span / radial_size))
        radial = {
            "core_radius": core_radius,
            "core_radius_ratio": core_radius_ratio,
            "outer_block_span": outer_span,
            "outer_radial_layers": radial_layers,
            "actual_outer_radial_size": outer_span / radial_layers,
            "topology": "finite cube-like core plus six surrounding curved blocks",
        }

    through_thickness: dict[str, Any] | None = None
    if shell_thickness is not None and target_through_thickness_size is not None:
        layers = max(1, math.ceil(shell_thickness / target_through_thickness_size))
        through_thickness = {
            "layers": layers,
            "actual_size": shell_thickness / layers,
        }

    return {
        "status": "planned",
        "inputs": {
            "radius": radius,
            "target_surface_size": target_surface_size,
            "maximum_angle_deg": maximum_angle_deg,
            "symmetry_sectors": symmetry_sectors,
            "minimum_great_circle_divisions": minimum_great_circle_divisions,
            "solid": solid,
            "core_radius_ratio": core_radius_ratio,
            "target_radial_size": target_radial_size,
            "shell_thickness": shell_thickness,
            "target_through_thickness_size": target_through_thickness_size,
        },
        "measurement_contract": [
            "center and three orthogonal local axes",
            "outer/inner radii, thickness, openings, and cut-plane locations",
            "symmetry planes, contact/load/support patches, and smallest retained feature",
        ],
        "surface_counts": {
            "circumference": circumference,
            "size_divisions": size_divisions,
            "angle_divisions": angle_divisions,
            "required_multiple": required_multiple,
            "great_circle_divisions": great_circle_divisions,
            "quarter_arc_divisions": great_circle_divisions // 4,
            "semicircle_divisions": great_circle_divisions // 2,
            "actual_great_circle_size": circumference / great_circle_divisions,
        },
        "construction_sequence": [
            "Create three orthogonal center planes and validate the smallest analysis-valid sector.",
            "Create measured great-circle/meridian boundaries without generating a pole-collapsing latitude-longitude grid.",
            (
                "Create a finite cube-like core, connect its six faces to the spherical boundary, and retain shared faces."
                if solid
                else "Use six cube-projected four-sided surface patches, or explicitly design octant singularities."
            ),
            "Add local rings only for openings, contacts, loads, or refinement and terminate them through transition patches.",
            "Mesh and quality-check one patch/block/sector before any symmetry replication.",
        ],
        "radial_core": radial,
        "through_thickness": through_thickness,
        "risks": [
            "Never collapse all radial lines to the sphere center or all meridians to one pole node.",
            "Keep extraordinary nodes, core interfaces, and seams away from peak gradients when possible.",
            "Symmetry replication is valid only when geometry, materials, contacts, loads, and constraints match.",
        ],
        "acceptance_note": (
            "Planning baseline only. Verify shared-edge counts, topology/mappability, core transition, "
            "Jacobian, warpage, aspect, skew, and solver-specific convergence on the real geometry."
        ),
    }


def plan_flange_mesh(
    outer_radius: float,
    bore_radius: float,
    bolt_circle_radius: float,
    bolt_hole_radius: float,
    bolt_hole_count: int,
    target_size: float,
    maximum_angle_deg: float = 15.0,
    hub_radius: float | None = None,
    washer_width: float | None = None,
    flange_thickness: float | None = None,
    target_axial_size: float | None = None,
) -> dict[str, Any]:
    for name, value in {
        "outer_radius": outer_radius,
        "bolt_circle_radius": bolt_circle_radius,
        "bolt_hole_radius": bolt_hole_radius,
        "target_size": target_size,
    }.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
    if bore_radius < 0:
        raise ValueError("bore_radius must be zero or greater")
    if bolt_hole_count < 3:
        raise ValueError("bolt_hole_count must be at least three")
    if maximum_angle_deg <= 0 or maximum_angle_deg > 90:
        raise ValueError("maximum_angle_deg must be greater than zero and no more than 90")
    if bore_radius >= bolt_circle_radius - bolt_hole_radius:
        raise ValueError("bore overlaps or reaches the bolt-hole band")
    if outer_radius <= bolt_circle_radius + bolt_hole_radius:
        raise ValueError("outer rim overlaps or reaches the bolt-hole band")
    if hub_radius is not None and not bore_radius < hub_radius < outer_radius:
        raise ValueError("hub_radius must lie between bore_radius and outer_radius")
    if washer_width is not None and washer_width <= 0:
        raise ValueError("washer_width must be greater than zero")
    if flange_thickness is not None or target_axial_size is not None:
        if flange_thickness is None or target_axial_size is None or flange_thickness <= 0 or target_axial_size <= 0:
            raise ValueError("flange_thickness and target_axial_size must both be greater than zero")

    pitch_angle = 360.0 / bolt_hole_count
    pitch_arc = 2.0 * math.pi * bolt_circle_radius / bolt_hole_count
    center_chord = 2.0 * bolt_circle_radius * math.sin(math.pi / bolt_hole_count)
    tangent_ligament = center_chord - 2.0 * bolt_hole_radius
    inner_clearance = bolt_circle_radius - bolt_hole_radius - bore_radius
    outer_clearance = outer_radius - bolt_circle_radius - bolt_hole_radius
    if tangent_ligament <= 0:
        raise ValueError("adjacent bolt holes overlap or touch")

    hole_size_divisions = math.ceil(2.0 * math.pi * bolt_hole_radius / target_size)
    hole_angle_divisions = math.ceil(360.0 / maximum_angle_deg)
    raw_hole_divisions = max(8, hole_size_divisions, hole_angle_divisions)
    hole_divisions = math.ceil(raw_hole_divisions / 4) * 4

    pitch_circle_size_divisions = math.ceil(2.0 * math.pi * bolt_circle_radius / target_size)
    pitch_circle_multiple = 2 * bolt_hole_count
    pitch_circle_divisions = math.ceil(pitch_circle_size_divisions / pitch_circle_multiple) * pitch_circle_multiple

    ring_radii = [bore_radius]
    if hub_radius is not None:
        ring_radii.append(hub_radius)
    if washer_width is not None:
        washer_inner = bolt_circle_radius - bolt_hole_radius - washer_width
        washer_outer = bolt_circle_radius + bolt_hole_radius + washer_width
        if washer_inner <= max(ring_radii) or washer_outer >= outer_radius:
            raise ValueError("washer band overlaps the bore/hub or outer rim")
        ring_radii.extend([washer_inner, washer_outer])
    ring_radii.append(outer_radius)

    axial: dict[str, Any] | None = None
    if flange_thickness is not None and target_axial_size is not None:
        layers = max(1, math.ceil(flange_thickness / target_axial_size))
        axial = {"layers": layers, "actual_size": flange_thickness / layers}

    warnings: list[str] = []
    for name, clearance in {
        "adjacent-hole tangent ligament": tangent_ligament,
        "bore-to-hole inner clearance": inner_clearance,
        "hole-to-rim outer clearance": outer_clearance,
    }.items():
        if clearance < 2.0 * target_size:
            warnings.append(f"{name} has fewer than two target-size rows; refine or redesign the transition")
    if hub_radius is not None and hub_radius >= bolt_circle_radius - bolt_hole_radius:
        warnings.append("hub reaches the bolt-hole band; a shared hub/washer transition is required")

    return {
        "status": "planned_with_warnings" if warnings else "planned",
        "inputs": {
            "outer_radius": outer_radius,
            "bore_radius": bore_radius,
            "bolt_circle_radius": bolt_circle_radius,
            "bolt_hole_radius": bolt_hole_radius,
            "bolt_hole_count": bolt_hole_count,
            "target_size": target_size,
            "maximum_angle_deg": maximum_angle_deg,
            "hub_radius": hub_radius,
            "washer_width": washer_width,
            "flange_thickness": flange_thickness,
            "target_axial_size": target_axial_size,
        },
        "measurement_contract": [
            "center/axis, outer and bore radii, hub/neck/step radii",
            "PCD, hole diameter/count/angular phase, and hole type",
            "flange/hub/gasket thickness, contact bands, fillets, loads, and constraints",
        ],
        "bolt_pattern": {
            "pitch_angle_deg": pitch_angle,
            "pitch_arc": pitch_arc,
            "adjacent_center_chord": center_chord,
            "adjacent_tangent_ligament": tangent_ligament,
            "inner_clearance": inner_clearance,
            "outer_clearance": outer_clearance,
            "hole_divisions": hole_divisions,
            "hole_actual_size": 2.0 * math.pi * bolt_hole_radius / hole_divisions,
            "pitch_circle_divisions": pitch_circle_divisions,
            "pitch_circle_required_multiple": pitch_circle_multiple,
        },
        "radial_zones": {
            "construction_ring_radii": ring_radii,
            "rows_at_target_size": {
                "adjacent_hole_ligament": math.floor(tangent_ligament / target_size),
                "inner_clearance": math.floor(inner_clearance / target_size),
                "outer_clearance": math.floor(outer_clearance / target_size),
            },
        },
        "construction_sequence": [
            "Create a verified center/axis system and concentric bore, hub/step, washer/contact, transition, and rim circles.",
            "Create radial lines through every hole center and every mid-pitch plane.",
            "Connect each retained hole at quadrant/tangent points to its washer or transition ring with compatible counts.",
            "Split hub/neck steps and fillets into staged source-target blocks before an axial solid-map sweep.",
            "Mesh one hole/washer sector first, then radial transitions and regular bore/rim zones; replicate only after quality checks.",
        ],
        "axial": axial,
        "warnings": warnings,
        "risks": [
            "A one-pitch cyclic analysis sector is valid only for periodic geometry, materials, contacts, pretension, loads, and constraints.",
            "Do not let washer rings overlap physical gasket/contact boundaries without a shared transition plan.",
            "A mappable flange block still requires local Jacobian, warpage, aspect, skew, and contact-zone checks.",
        ],
        "acceptance_note": (
            "Planning baseline only. Verify measured geometry, shared sector counts, seam equivalence, "
            "ligament rows, axial layers, contact representation, and solver convergence."
        ),
    }


def plan_size_transition(
    fine_size: float,
    coarse_size: float,
    maximum_growth_ratio: float = 1.5,
    minimum_layers: int = 1,
) -> dict[str, Any]:
    if fine_size <= 0 or coarse_size <= 0:
        raise ValueError("fine_size and coarse_size must be greater than zero")
    if maximum_growth_ratio <= 1:
        raise ValueError("maximum_growth_ratio must be greater than one")
    if minimum_layers < 0:
        raise ValueError("minimum_layers must be zero or greater")

    lower = min(fine_size, coarse_size)
    upper = max(fine_size, coarse_size)
    ratio = upper / lower
    if math.isclose(ratio, 1.0):
        layers = 0
        actual_growth = 1.0
    else:
        layers = max(minimum_layers, math.ceil(math.log(ratio) / math.log(maximum_growth_ratio)))
        actual_growth = ratio ** (1.0 / layers)

    return {
        "status": "planned",
        "direction": "coarsening" if coarse_size > fine_size else "refining" if coarse_size < fine_size else "uniform",
        "fine_size": fine_size,
        "coarse_size": coarse_size,
        "overall_ratio": ratio,
        "maximum_growth_ratio": maximum_growth_ratio,
        "transition_layers": layers,
        "actual_growth_ratio": actual_growth,
        "recommended_band_length": sum(lower * actual_growth**index for index in range(1, layers + 1)),
        "acceptance_note": (
            "Create an explicit transition patch/block and place unavoidable singularities away from "
            "holes, contacts, load paths, and mapped source faces."
        ),
    }


def plan_partition_strategy(
    geometry_summary: str,
    mesh_route: str,
    has_symmetry: bool = False,
    has_holes_or_slots: bool = False,
    has_branches_or_intersections: bool = False,
    has_curved_sectors: bool = False,
    requires_conformal_interfaces: bool = True,
    sweep_direction_hint: str = "",
) -> dict[str, Any]:
    route = mesh_route.strip().lower().replace("-", "_")
    aliases = {
        "shell": "quad_shell",
        "quad": "quad_shell",
        "quad_dominant": "quad_shell",
        "hex": "mapped_hex",
        "hexa": "mapped_hex",
        "solid_map": "mapped_hex",
        "tet": "tetra",
        "tet_dominant": "tetra",
    }
    route = aliases.get(route, route)
    if route not in {"quad_shell", "mapped_hex", "tetra"}:
        raise ValueError("mesh_route must resolve to quad_shell, mapped_hex, or tetra")

    sequence = [
        "Define solver profile, element order, target/min/max size, and active 2D/3D quality criteria.",
        "Audit free/shared/non-manifold topology, duplicates, overlaps, normals, and physics-driving boundaries.",
        "Classify features as preserve, seed, washer/local-control, or remove with an engineering reason.",
    ]
    partition_principles: list[str] = []
    risks: list[str] = []

    if route == "quad_shell":
        sequence.extend(
            [
                "Partition difficult features into controlled patches, transition bands, and regular far-field patches.",
                "Record ordered boundary loops and make opposing/shared edge counts compatible before automesh.",
                "Mesh feature patches first, transitions second, and regular patches last; localize any permitted trias.",
            ]
        )
        partition_principles.extend(
            [
                "Prefer four-sided/map-friendly patches without sliver faces or acute corners.",
                "Use hard points and split lines only for required node/flow locations; suppress meaningless trim lines.",
            ]
        )
        risks.append("A quad-dominant result can still have poor flow if extraordinary nodes sit in critical regions.")
    elif route == "mapped_hex":
        sequence.extend(
            [
                "Describe every block by source, target, path/along faces, sweep direction, and shared-face dependencies.",
                "Backtrack from terminal blocks toward the core, then mesh difficult sources and dependencies in reverse order.",
                "Verify one- or three-direction mappability after each cut and quality-check source meshes before volume mapping.",
            ]
        )
        partition_principles.extend(
            [
                "Use compact three-direction mappable blocks where sweep directions change.",
                "Do not assume individually mappable blocks can always be meshed in one multi-solid operation.",
            ]
        )
        risks.extend(
            [
                "Conflicting constraints on a shared face can invalidate a multi-solid mapping sequence.",
                "Mappability proves topology eligibility, not acceptable Jacobian, warpage, or aspect ratio.",
            ]
        )
    else:
        sequence.extend(
            [
                "Avoid decomposition that does not serve materials, contacts, boundary conditions, or local refinement.",
                "Create a closed, intersection-free, curvature/proximity-controlled surface mesh.",
                "Generate the volume mesh and repair boundary triangles or narrow-volume causes when tet collapse fails.",
            ]
        )
        partition_principles.append("Prefer local surface controls over hex-style over-partitioning.")
        risks.append("Excess geometric partitions can constrain boundary triangles and worsen tetra quality.")

    if has_symmetry:
        partition_principles.append(
            "Partition and validate the smallest analysis-valid symmetry/periodic sector first."
        )
    if has_holes_or_slots:
        partition_principles.append(
            "Plan fixed hole/slot counts and washer or local transition topology before surrounding patches."
        )
    if has_branches_or_intersections:
        partition_principles.append(
            "Isolate branches, then resolve a central junction/core block before sweeping into it."
        )
        risks.append("Independent branch sweeps can leave an unmappable or poor-quality residual core.")
    if has_curved_sectors:
        partition_principles.append(
            "Split curved sectors when their forced sweep role distorts elements; verify rather than assume the split."
        )
    if requires_conformal_interfaces:
        partition_principles.append("Retain shared partition faces and enforce matching boundary topology/counts.")
    else:
        risks.append("Name and verify the nonconformal coupling/contact method at every mismatched interface.")

    return {
        "status": "planned",
        "inputs": {
            "geometry_summary": geometry_summary,
            "mesh_route": route,
            "has_symmetry": has_symmetry,
            "has_holes_or_slots": has_holes_or_slots,
            "has_branches_or_intersections": has_branches_or_intersections,
            "has_curved_sectors": has_curved_sectors,
            "requires_conformal_interfaces": requires_conformal_interfaces,
            "sweep_direction_hint": sweep_direction_hint,
        },
        "sequence": sequence,
        "partition_principles": partition_principles,
        "block_contract": (
            ["patch_id", "boundary_loop", "ordered_edge_counts", "flow_direction", "neighbors"]
            if route == "quad_shell"
            else ["block_id", "source", "target", "path_faces", "sweep_direction", "shared_faces", "dependencies"]
            if route == "mapped_hex"
            else ["volume_id", "boundary_surface_set", "local_controls", "closed_surface_check"]
        ),
        "risks": risks,
        "acceptance": [
            "No new unresolved sliver face, short edge, acute wedge, topology defect, or residual unmappable block.",
            "All planned selections and created entities have nonzero counts and stable IDs/descriptors.",
            "All active solver-specific quality metrics are rechecked after meshing and remediation.",
        ],
    }


def plan_tetra_quality_remediation(
    total_elements: int,
    target_size: float,
    minimum_surface_size: float,
    minimum_geometric_feature: float | None = None,
    tet_collapse_fail_count: int = 0,
    tet_collapse_worst: float | None = None,
    tet_collapse_threshold: float = 0.10,
    jacobian_fail_count: int = 0,
    jacobian_worst: float | None = None,
    jacobian_threshold: float = 0.60,
    aspect_ratio_fail_count: int = 0,
    aspect_ratio_worst: float | None = None,
    aspect_ratio_threshold: float = 8.0,
    volumetric_skew_fail_count: int = 0,
    volumetric_skew_worst: float | None = None,
    volumetric_skew_threshold: float = 0.95,
    minimum_height_fail_count: int = 0,
    minimum_height_worst: float | None = None,
    minimum_height_threshold: float = 0.20,
    minimum_height_overlap_tet_collapse: int = 0,
    minimum_height_overlap_aspect_ratio: int = 0,
    minimum_height_overlap_volumetric_skew: int = 0,
    previous_minimum_height_fail_count: int | None = None,
    optimized_minimum_height_fail_count: int | None = None,
    protected_small_features: bool = True,
) -> dict[str, Any]:
    if total_elements < 1:
        raise ValueError("total_elements must be greater than zero")
    for name, value in {
        "target_size": target_size,
        "minimum_surface_size": minimum_surface_size,
        "tet_collapse_threshold": tet_collapse_threshold,
        "jacobian_threshold": jacobian_threshold,
        "aspect_ratio_threshold": aspect_ratio_threshold,
        "volumetric_skew_threshold": volumetric_skew_threshold,
        "minimum_height_threshold": minimum_height_threshold,
    }.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
    if minimum_geometric_feature is not None and minimum_geometric_feature <= 0:
        raise ValueError("minimum_geometric_feature must be greater than zero")

    counts = {
        "tet_collapse": tet_collapse_fail_count,
        "jacobian": jacobian_fail_count,
        "aspect_ratio": aspect_ratio_fail_count,
        "volumetric_skew": volumetric_skew_fail_count,
        "minimum_height": minimum_height_fail_count,
    }
    for name, value in counts.items():
        if value < 0 or value > total_elements:
            raise ValueError(f"{name}_fail_count must be between zero and total_elements")

    metrics = {
        "tet_collapse": {
            "direction": "minimum",
            "threshold": tet_collapse_threshold,
            "worst": tet_collapse_worst,
        },
        "jacobian": {
            "direction": "minimum",
            "threshold": jacobian_threshold,
            "worst": jacobian_worst,
        },
        "aspect_ratio": {
            "direction": "maximum",
            "threshold": aspect_ratio_threshold,
            "worst": aspect_ratio_worst,
        },
        "volumetric_skew": {
            "direction": "maximum",
            "threshold": volumetric_skew_threshold,
            "worst": volumetric_skew_worst,
        },
        "minimum_height": {
            "direction": "minimum",
            "threshold": minimum_height_threshold,
            "worst": minimum_height_worst,
        },
    }
    missing_worst_values: list[str] = []
    for name, metric in metrics.items():
        fail_count = counts[name]
        worst = metric["worst"]
        if fail_count > 0 and worst is None:
            missing_worst_values.append(name)
        metric["fail_count"] = fail_count
        metric["fail_rate_percent"] = 100.0 * fail_count / total_elements
        metric["status"] = "pass" if fail_count == 0 else "fail"
        if worst is not None:
            if metric["direction"] == "minimum":
                metric["worst_to_threshold_ratio"] = worst / metric["threshold"]
            else:
                metric["worst_to_threshold_ratio"] = worst / metric["threshold"]

    dominant_metric = max(metrics, key=lambda name: metrics[name]["fail_rate_percent"])
    global_minimum_baseline = 0.33 * target_size
    global_maximum_baseline = 1.75 * target_size
    fine_to_coarse = plan_size_transition(
        minimum_surface_size,
        target_size,
        maximum_growth_ratio=1.25,
        minimum_layers=1,
    )

    cause_signals: list[str] = []
    if minimum_height_fail_count > 0 and minimum_height_worst is not None:
        if minimum_height_worst < 0.5 * minimum_height_threshold:
            cause_signals.append(
                "Minimum height is severely below its gate; treat the patch as a flattened/sliver-tet problem, not a marginal threshold miss."
            )
    if minimum_geometric_feature is not None and minimum_geometric_feature <= 1.1 * minimum_height_threshold:
        cause_signals.append(
            "The smallest retained geometric feature is at or below the minimum-height gate with little meshing margin. Review it for protected physics or defeaturing."
        )
    if minimum_surface_size < global_minimum_baseline:
        cause_signals.append(
            "The global curvature/proximity minimum is below the 33%-of-target BatchMesher planning baseline; keep such fine size local to protected features instead of applying it model-wide."
        )

    overlap_checks = {
        "tet_collapse": (minimum_height_overlap_tet_collapse, tet_collapse_fail_count),
        "aspect_ratio": (minimum_height_overlap_aspect_ratio, aspect_ratio_fail_count),
        "volumetric_skew": (minimum_height_overlap_volumetric_skew, volumetric_skew_fail_count),
    }
    fully_nested = [name for name, (overlap, failures) in overlap_checks.items() if failures > 0 and overlap == failures]
    if fully_nested:
        cause_signals.append(
            "All failures for " + ", ".join(fully_nested) +
            " are contained in the minimum-height set; repair the shared boundary/geometry patches before metric-specific node edits."
        )

    optimizer_improvement = None
    if previous_minimum_height_fail_count is not None and optimized_minimum_height_fail_count is not None:
        if previous_minimum_height_fail_count < 0 or optimized_minimum_height_fail_count < 0:
            raise ValueError("optimizer failure counts must be zero or greater")
        if previous_minimum_height_fail_count == 0:
            optimizer_improvement = 0.0
        else:
            optimizer_improvement = (
                previous_minimum_height_fail_count - optimized_minimum_height_fail_count
            ) / previous_minimum_height_fail_count
        if optimizer_improvement < 0.01:
            cause_signals.append(
                "The prior optimizer improved minimum-height failures by less than 1%; stop repeating node-only optimization and change geometry/surface-remesh constraints."
            )

    geometry_decision = (
        "protect_and_apply_local_control"
        if protected_small_features
        else "review_short_edges_sliver_faces_and_cosmetic_blends_for_suppression"
    )
    if minimum_geometric_feature is not None and minimum_geometric_feature <= 1.1 * minimum_height_threshold:
        geometry_decision = (
            "manual_physics_review_then_local_control_or_sensitivity_study"
            if protected_small_features
            else "defeature_or_reconstruct_before_remeshing"
        )

    return {
        "status": "blocked" if any(counts.values()) else "pass",
        "evidence_status": "incomplete" if missing_worst_values else "complete",
        "missing_worst_values": missing_worst_values,
        "metrics": metrics,
        "dominant_metric": dominant_metric,
        "size_feasibility": {
            "target_size": target_size,
            "current_minimum_surface_size": minimum_surface_size,
            "current_minimum_to_target_ratio": minimum_surface_size / target_size,
            "batchmesher_global_minimum_planning_baseline": global_minimum_baseline,
            "batchmesher_global_maximum_planning_baseline": global_maximum_baseline,
            "minimum_geometric_feature": minimum_geometric_feature,
            "minimum_height_gate": minimum_height_threshold,
            "geometry_decision": geometry_decision,
            "local_to_global_transition": fine_to_coarse,
        },
        "overlap": {
            "minimum_height_with_tet_collapse": minimum_height_overlap_tet_collapse,
            "minimum_height_with_aspect_ratio": minimum_height_overlap_aspect_ratio,
            "minimum_height_with_volumetric_skew": minimum_height_overlap_volumetric_skew,
        },
        "optimizer_improvement_fraction": optimizer_improvement,
        "cause_signals": cause_signals,
        "remediation_sequence": [
            "Export each metric's exact worst value, element ID, centroid, failed count, and failure rate with hm_getelemcheckvalues; cluster failed elements and add at least one neighboring layer.",
            "Map every cluster to boundary triangles, CAD surfaces, short edges, narrow faces, fillets, holes, contacts, loads, constraints, and interfaces before editing.",
            "Repair free/T-edges, intersections, sliver faces, and unprotected cosmetic short features; block automatic defeaturing when physics roles are unknown.",
            "Generate and quality-check a closed surface-tria mesh first. Use a regular global minimum near the criteria baseline and apply finer curvature/proximity controls only to protected features.",
            "Regenerate affected tetra volumes with minimum-height restriction and quality-optimized settings verified for the installed HyperMesh release.",
            "If required, use Solid Mesh Optimization with boundary triangles set to Remesh, feature lines and interfaces protected, anchor nodes fixed, and one neighboring/refinement-box layer included.",
            "Reject an iteration that only renumbers failures, improves the dominant count by less than 1%, moves failures into critical regions, or worsens any other active metric.",
        ],
        "acceptance": [
            "All active solver-specific failure counts are zero, or every residual exception is localized and justified by downstream solver evidence.",
            "Worst values and IDs are exported even when failure counts are zero; a count-only report is incomplete.",
            "Protected feature, contact, load, constraint, material, and interface entities remain valid after cleanup/remesh.",
            "Geometry volume/bounding-box change and surface free/non-manifold topology remain within documented tolerances.",
            "A feature-retained versus simplified sensitivity or mesh-convergence study is required before suppressing a stress/contact/fatigue-driving small feature.",
        ],
    }


def plan_tetra_hotspot_remediation(
    total_elements: int,
    failed_element_count: int,
    hotspot_count: int,
    boundary_associated_failure_count: int,
    two_or_more_boundary_nodes_count: int,
    three_or_more_boundary_nodes_count: int,
    target_size: float,
    minimum_surface_size: float,
    minimum_height_fail_count: int = 0,
    minimum_height_worst: float | None = None,
    minimum_height_threshold: float = 0.20,
    tet_collapse_fail_count: int = 0,
    aspect_ratio_fail_count: int = 0,
    volumetric_skew_fail_count: int = 0,
    dominant_hotspot_element_count: int = 0,
    minimum_failed_tet_edge: float | None = None,
    minimum_associated_geometry_edge: float | None = None,
    requested_local_size: float | None = None,
    maximum_growth_ratio: float = 1.25,
    strict_pareto: bool = True,
) -> dict[str, Any]:
    """Classify tetra failure hotspots and choose a transactional remedy.

    This planner deliberately separates geometric-boundary failures from
    interior node-position failures.  An absolute minimum-height failure is not
    automatically a refinement request: smaller tets can make the same gate
    harder to satisfy when the boundary topology is already over-constrained.
    """

    if total_elements < 1:
        raise ValueError("total_elements must be greater than zero")
    if failed_element_count < 1 or failed_element_count > total_elements:
        raise ValueError("failed_element_count must be between one and total_elements")
    if hotspot_count < 1 or hotspot_count > failed_element_count:
        raise ValueError("hotspot_count must be between one and failed_element_count")
    for name, value in {
        "boundary_associated_failure_count": boundary_associated_failure_count,
        "two_or_more_boundary_nodes_count": two_or_more_boundary_nodes_count,
        "three_or_more_boundary_nodes_count": three_or_more_boundary_nodes_count,
        "dominant_hotspot_element_count": dominant_hotspot_element_count,
        "minimum_height_fail_count": minimum_height_fail_count,
        "tet_collapse_fail_count": tet_collapse_fail_count,
        "aspect_ratio_fail_count": aspect_ratio_fail_count,
        "volumetric_skew_fail_count": volumetric_skew_fail_count,
    }.items():
        if value < 0 or value > failed_element_count:
            raise ValueError(f"{name} must be between zero and failed_element_count")
    if two_or_more_boundary_nodes_count > boundary_associated_failure_count:
        raise ValueError("two_or_more_boundary_nodes_count cannot exceed boundary_associated_failure_count")
    if three_or_more_boundary_nodes_count > two_or_more_boundary_nodes_count:
        raise ValueError("three_or_more_boundary_nodes_count cannot exceed two_or_more_boundary_nodes_count")
    for name, value in {
        "target_size": target_size,
        "minimum_surface_size": minimum_surface_size,
        "minimum_height_threshold": minimum_height_threshold,
        "maximum_growth_ratio": maximum_growth_ratio,
    }.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero")
    if maximum_growth_ratio <= 1.0:
        raise ValueError("maximum_growth_ratio must be greater than one")
    for name, value in {
        "minimum_height_worst": minimum_height_worst,
        "minimum_failed_tet_edge": minimum_failed_tet_edge,
        "minimum_associated_geometry_edge": minimum_associated_geometry_edge,
        "requested_local_size": requested_local_size,
    }.items():
        if value is not None and value <= 0:
            raise ValueError(f"{name} must be greater than zero when provided")

    boundary_ratio = boundary_associated_failure_count / failed_element_count
    boundary_two_ratio = two_or_more_boundary_nodes_count / failed_element_count
    boundary_three_ratio = three_or_more_boundary_nodes_count / failed_element_count
    interior_count = failed_element_count - boundary_associated_failure_count
    dominant_share = dominant_hotspot_element_count / failed_element_count

    if boundary_two_ratio >= 0.60:
        classification = "boundary_topology_driven"
    elif boundary_ratio <= 0.30:
        classification = "interior_node_or_connectivity_driven"
    else:
        classification = "mixed_boundary_and_interior"

    height_dominant = minimum_height_fail_count == max(
        minimum_height_fail_count,
        tet_collapse_fail_count,
        aspect_ratio_fail_count,
        volumetric_skew_fail_count,
    ) and minimum_height_fail_count > 0
    severe_height = (
        minimum_height_worst is not None
        and minimum_height_worst < 0.5 * minimum_height_threshold
    )
    local_size = requested_local_size or minimum_surface_size
    local_size_to_height_gate = local_size / minimum_height_threshold
    blind_refinement_blocked = bool(
        height_dominant
        and (
            boundary_two_ratio >= 0.60
            or severe_height
            or local_size_to_height_gate <= 2.0
        )
    )

    if blind_refinement_blocked:
        first_action = "regularize_or_coarsen_boundary_sampling_before_any_refinement"
        refinement_decision = "blocked_as_default"
        refinement_reason = (
            "Minimum height is dominant and the failures are boundary constrained or severe. "
            "Further local refinement can reduce absolute tetra height; first redistribute edge/surface "
            "sampling, repair the boundary trias, or review non-physical topology."
        )
    elif classification == "interior_node_or_connectivity_driven":
        first_action = "fixed_boundary_local_tetra_optimization"
        refinement_decision = "conditional"
        refinement_reason = "The evidence is mainly interior; optimize connectivity/node placement before changing CAD density."
    else:
        first_action = "surface_first_cluster_remesh_with_feature_constraints"
        refinement_decision = "conditional"
        refinement_reason = "Refine only when curvature or physics is under-resolved; otherwise regularize the boundary mesh."

    baseline_ratios = (0.25, 0.275, 0.30, 0.33)
    minimum_gate_margin = 2.5 * minimum_height_threshold
    parameter_search = []
    for ratio in baseline_ratios:
        candidate = max(minimum_gate_margin, ratio * target_size)
        if not any(math.isclose(candidate, row["minimum_size"], rel_tol=0.0, abs_tol=1e-12) for row in parameter_search):
            parameter_search.append(
                {
                    "minimum_size": candidate,
                    "minimum_to_target_ratio": candidate / target_size,
                    "maximum_growth_ratio": maximum_growth_ratio,
                    "purpose": "model-level baseline only; protected features may use a reviewed smaller local size",
                }
            )

    geometry_edge_signal = None
    if minimum_associated_geometry_edge is not None and minimum_failed_tet_edge is not None:
        geometry_edge_signal = (
            "mesh_sampling_or_boundary_tria_conflict"
            if minimum_associated_geometry_edge > 2.0 * minimum_failed_tet_edge
            else "small_retained_geometry_may_be_driving_the_failure"
        )

    return {
        "status": "planned",
        "classification": classification,
        "statistics": {
            "total_elements": total_elements,
            "failed_element_count": failed_element_count,
            "failure_rate_percent": 100.0 * failed_element_count / total_elements,
            "hotspot_count": hotspot_count,
            "boundary_associated_failure_count": boundary_associated_failure_count,
            "boundary_associated_ratio": boundary_ratio,
            "two_or_more_boundary_nodes_ratio": boundary_two_ratio,
            "three_or_more_boundary_nodes_ratio": boundary_three_ratio,
            "interior_failure_count": interior_count,
            "dominant_hotspot_element_count": dominant_hotspot_element_count,
            "dominant_hotspot_share": dominant_share,
        },
        "diagnosis": {
            "height_dominant": height_dominant,
            "severe_minimum_height": severe_height,
            "minimum_height_threshold": minimum_height_threshold,
            "minimum_height_worst": minimum_height_worst,
            "requested_or_current_local_size": local_size,
            "local_size_to_height_gate": local_size_to_height_gate,
            "minimum_failed_tet_edge": minimum_failed_tet_edge,
            "minimum_associated_geometry_edge": minimum_associated_geometry_edge,
            "geometry_edge_signal": geometry_edge_signal,
        },
        "refinement_gate": {
            "decision": refinement_decision,
            "blind_refinement_blocked": blind_refinement_blocked,
            "reason": refinement_reason,
            "allowed_only_for": [
                "under-resolved protected curvature",
                "contact/load/fatigue or result-gradient region",
                "a refinement zone with an explicit transition and successful all-metric recheck",
            ],
        },
        "first_action": first_action,
        "parameter_search": parameter_search,
        "cluster_routes": {
            "geometry_edge_or_three_boundary_nodes": [
                "inspect associated line IDs, total line length, local node spacing, tangency, and protected role",
                "redistribute or coarsen irregular edge seeding; do not automatically split an already short height",
                "remesh the attached surface patch while maintaining geometry edges, feature lines, and anchors",
            ],
            "surface_boundary": [
                "quality-check boundary trias, then test edge-swap and remesh candidates independently",
                "include one neighboring layer first; add a second layer only when transition distance is inadequate",
            ],
            "interior": [
                "use fixed-boundary local tetra optimization or connectivity repair before changing surface density",
            ],
        },
        "transaction_sequence": [
            "Export exact failed IDs/values/centroids and node-to-geometry associations; cluster by shared topology or a radius tied to target size.",
            "Rank hotspots by severity, multi-metric overlap, boundary-node ratio, protected physics role, and hotspot size.",
            "Checkpoint the current accepted mesh before each hotspot; process one hotspot instead of the full union.",
            "Run route-specific fixed-topology, edge-swap, or boundary-remesh candidates with protected geometry edges, feature lines, interfaces, and anchor nodes.",
            "Recheck every active metric globally, not only the seed metric; compare counts, exact worst values, locations, element count, geometry entities, and time.",
            "Commit the hotspot candidate only when it satisfies the acceptance contract; otherwise reload the checkpoint and record the rejection.",
            "After an accepted topology-changing transaction, regenerate hotspot IDs because element numbers and adjacency can change.",
        ],
        "acceptance_contract": {
            "mode": "strict_pareto" if strict_pareto else "reviewed_tradeoff",
            "rollback_on_any_active_metric_regression": strict_pareto,
            "requires_global_recheck": True,
            "requires_exact_worst_values": True,
            "requires_geometry_and_feature_preservation": True,
            "requires_candidate_checkpoint": True,
        },
    }


def plan_tetra_zero_failure_search(
    total_elements: int,
    unique_failed_element_count: int,
    hotspot_count: int,
    boundary_associated_failure_count: int,
    two_or_more_boundary_nodes_count: int,
    tet_collapse_fail_count: int = 0,
    aspect_ratio_fail_count: int = 0,
    volumetric_skew_fail_count: int = 0,
    minimum_height_fail_count: int = 0,
    tet_collapse_worst: float | None = None,
    aspect_ratio_worst: float | None = None,
    volumetric_skew_worst: float | None = None,
    minimum_height_worst: float | None = None,
    jacobian_fail_count: int = 0,
    non_tetra_element_count: int = 0,
    plateau_detected: bool = False,
    zero_failure_required: bool = True,
    observed_maximum_boundary_displacement: float | None = None,
    maximum_allowed_boundary_displacement: float | None = None,
    current_geometry_association_change_count: int = 0,
    initial_geometry_association_change_count: int = 0,
) -> dict[str, Any]:
    """Plan the final zero-failure search and keep geometry risk explicit.

    This is the escalation planner used after ordinary surface-first and local
    hotspot repair reaches a plateau.  It deliberately keeps the numerical
    quality gate separate from CAD-adherence acceptance: zero failed elements
    must never hide excessive boundary motion or lost feature associations.
    """

    if total_elements < 1:
        raise ValueError("total_elements must be greater than zero")
    counts = {
        "unique_failed_element_count": unique_failed_element_count,
        "hotspot_count": hotspot_count,
        "boundary_associated_failure_count": boundary_associated_failure_count,
        "two_or_more_boundary_nodes_count": two_or_more_boundary_nodes_count,
        "tet_collapse_fail_count": tet_collapse_fail_count,
        "aspect_ratio_fail_count": aspect_ratio_fail_count,
        "volumetric_skew_fail_count": volumetric_skew_fail_count,
        "minimum_height_fail_count": minimum_height_fail_count,
        "jacobian_fail_count": jacobian_fail_count,
        "non_tetra_element_count": non_tetra_element_count,
        "current_geometry_association_change_count": current_geometry_association_change_count,
        "initial_geometry_association_change_count": initial_geometry_association_change_count,
    }
    for name, value in counts.items():
        if value < 0:
            raise ValueError(f"{name} must be zero or greater")
    if unique_failed_element_count > total_elements:
        raise ValueError("unique_failed_element_count cannot exceed total_elements")
    if hotspot_count > unique_failed_element_count:
        raise ValueError("hotspot_count cannot exceed unique_failed_element_count")
    if boundary_associated_failure_count > unique_failed_element_count:
        raise ValueError("boundary_associated_failure_count cannot exceed unique_failed_element_count")
    if two_or_more_boundary_nodes_count > boundary_associated_failure_count:
        raise ValueError("two_or_more_boundary_nodes_count cannot exceed boundary_associated_failure_count")
    for name, value in {
        "tet_collapse_worst": tet_collapse_worst,
        "aspect_ratio_worst": aspect_ratio_worst,
        "volumetric_skew_worst": volumetric_skew_worst,
        "minimum_height_worst": minimum_height_worst,
        "observed_maximum_boundary_displacement": observed_maximum_boundary_displacement,
        "maximum_allowed_boundary_displacement": maximum_allowed_boundary_displacement,
    }.items():
        if value is not None and value < 0:
            raise ValueError(f"{name} must be zero or greater when provided")

    metric_failures = {
        "tet_collapse": tet_collapse_fail_count,
        "aspect_ratio": aspect_ratio_fail_count,
        "volumetric_skew": volumetric_skew_fail_count,
        "minimum_height": minimum_height_fail_count,
        "jacobian": jacobian_fail_count,
    }
    four_metric_zero = all(
        metric_failures[name] == 0
        for name in ("tet_collapse", "aspect_ratio", "volumetric_skew", "minimum_height")
    )
    pure_tetra = non_tetra_element_count == 0
    numerical_acceptance = four_metric_zero and jacobian_fail_count == 0 and pure_tetra
    boundary_ratio = (
        boundary_associated_failure_count / unique_failed_element_count
        if unique_failed_element_count
        else 0.0
    )
    constrained_boundary_ratio = (
        two_or_more_boundary_nodes_count / unique_failed_element_count
        if unique_failed_element_count
        else 0.0
    )

    if observed_maximum_boundary_displacement is None:
        geometry_status = "not_measured"
    elif maximum_allowed_boundary_displacement is None:
        geometry_status = "measured_tolerance_not_defined"
    elif observed_maximum_boundary_displacement <= maximum_allowed_boundary_displacement:
        geometry_status = "pass"
    else:
        geometry_status = "fail"
    association_status = (
        "pass"
        if current_geometry_association_change_count == 0
        and initial_geometry_association_change_count == 0
        else "review_required"
    )
    geometry_acceptance = geometry_status == "pass" and association_status == "pass"

    if numerical_acceptance:
        phase = "independent_reload_and_geometry_acceptance"
    elif plateau_detected and boundary_ratio >= 0.90:
        phase = "shape_preserving_boundary_escalation"
    elif boundary_ratio >= 0.60:
        phase = "boundary_hotspot_transaction"
    else:
        phase = "split_boundary_and_interior_residuals"

    residual_routes = {
        "boundary_plateau": [
            "Checkpoint the best globally accepted mesh before each candidate.",
            "Test *morphsmoothmorphbased on one and two neighboring layers with quality 2/3, feature-aware fixing, and protected interfaces/anchors.",
            "Rank candidates lexicographically by total failed counts, exact worst margins, protected-feature integrity, then boundary displacement; do not optimize a single metric in isolation.",
        ],
        "minimum_height_residual": [
            "Use a one-layer shape-preserving local free-morph candidate only after the boundary plateau route.",
            "Do not refine an absolute-height residual by default; measure the local boundary-tria and geometry-edge spacing first.",
        ],
        "interior_skew_or_connectivity_residual": [
            "Use fixed-boundary local *tetmesh mode 6 on the residual patch plus one neighboring layer.",
            "Use mode 7 only for swappable-boundary trials and mode 8 only for remeshable-boundary trials; keep min_height active and verify the installed release syntax.",
        ],
    }

    return {
        "status": "accepted" if numerical_acceptance else "planned",
        "phase": phase,
        "classification": {
            "boundary_associated_ratio": boundary_ratio,
            "two_or_more_boundary_nodes_ratio": constrained_boundary_ratio,
            "plateau_detected": plateau_detected,
        },
        "quality_evidence": {
            "metric_fail_counts": metric_failures,
            "exact_worst_values": {
                "tet_collapse": tet_collapse_worst,
                "aspect_ratio": aspect_ratio_worst,
                "volumetric_skew": volumetric_skew_worst,
                "minimum_height": minimum_height_worst,
            },
            "four_metric_zero": four_metric_zero,
            "pure_tetra": pure_tetra,
            "numerical_acceptance_pass": numerical_acceptance,
        },
        "geometry_evidence": {
            "status": geometry_status,
            "association_status": association_status,
            "observed_maximum_boundary_displacement": observed_maximum_boundary_displacement,
            "maximum_allowed_boundary_displacement": maximum_allowed_boundary_displacement,
            "current_geometry_association_change_count": current_geometry_association_change_count,
            "initial_geometry_association_change_count": initial_geometry_association_change_count,
            "geometry_acceptance_pass": geometry_acceptance,
            "warning": (
                "Numerical quality and CAD adherence are separate gates. Define an engineering displacement tolerance before simulation acceptance."
                if geometry_status != "pass"
                else None
            ),
        },
        "residual_routes": residual_routes,
        "transaction_sequence": [
            "Export exact values, IDs, centroids, metric intersections, boundary-node counts, and geometry associations; never reuse stale IDs after a topology change.",
            "Run one route-specific candidate from a checkpoint and recheck every metric globally.",
            "Rollback any candidate that worsens an active count, exact worst margin, protected feature, element type, or documented geometry tolerance.",
            "When four metrics reach zero, export the solver deck and independently reload it for a second full-model check.",
            "Audit node displacement and both current and initial CAD associations. Do not force-project stale initial IDs unless the referenced current geometry entity exists and a checkpointed trial passes all gates.",
        ],
        "acceptance_contract": {
            "zero_failure_required": zero_failure_required,
            "quality_acceptance_pass": numerical_acceptance,
            "geometry_acceptance_pass": geometry_acceptance,
            "simulation_acceptance_pass": numerical_acceptance and geometry_acceptance,
            "requires_independent_reload": True,
            "requires_exact_worst_values": True,
            "requires_pure_tetra_audit": True,
            "requires_boundary_displacement_tolerance": True,
            "requires_geometry_association_audit": True,
        },
    }


def register_hypermesh_profile(server: Any) -> Any:
    # FastMCP v1 exposes instructions as a read-only facade over the low-level
    # server. The profile pins v1 and sets the low-level field deliberately.
    server._mcp_server.instructions = SERVER_INSTRUCTIONS

    @server.resource(
        "hypermesh://guidance/workflow",
        name="hypermesh_workflow",
        title="HyperMesh Evidence Workflow",
        description="Evidence-first CAD import, cleanup, meshing, quality, and export workflow.",
        mime_type="text/markdown",
    )
    def hypermesh_workflow_resource() -> str:
        return _read_skill_file(
            "SKILL.md",
            "Use explicit Tcl through hmbatch, preserve source CAD, and require import, entity, quality, and export evidence.",
        )

    @server.resource(
        "hypermesh://guidance/quality-gates",
        name="hypermesh_quality_gates",
        title="HyperMesh Quality Gates",
        description="Blocking acceptance criteria for imported geometry, mesh quality, and exported decks.",
        mime_type="text/markdown",
    )
    def hypermesh_quality_gates_resource() -> str:
        return _read_skill_file(
            "references/quality-gates.md",
            "Require nonzero imported entities and elements, named quality criteria, and a nonempty solver deck.",
        )

    @server.resource(
        "hypermesh://guidance/partition-strategy",
        name="hypermesh_partition_strategy",
        title="HyperMesh Partition and Block Strategy",
        description="Decision logic for 2D quad patches, mapped/swept solid blocks, cut sequencing, and tetra fallback.",
        mime_type="text/markdown",
    )
    def hypermesh_partition_strategy_resource() -> str:
        return _read_skill_file(
            "references/partition-strategy.md",
            "Partition only to create valid patch flow or mapped source-target-path block topology.",
        )

    @server.resource(
        "hypermesh://guidance/feature-meshing",
        name="hypermesh_feature_meshing",
        title="HyperMesh Feature-Aware Meshing",
        description="Local controls for cylinders, holes, circular/feature edges, boundaries, and sweepable solids.",
        mime_type="text/markdown",
    )
    def hypermesh_feature_meshing_resource() -> str:
        return _read_skill_file(
            "references/feature-meshing.md",
            "Derive explicit circumferential, axial, and radial divisions and preserve physics-driving boundaries.",
        )

    @server.resource(
        "hypermesh://guidance/fillet-chamfer-meshing",
        name="hypermesh_fillet_chamfer_meshing",
        title="HyperMesh Fillet and Chamfer Meshing",
        description="Measured preserve/defeature decisions, profile rows, curvature controls, block topology, and acceptance evidence.",
        mime_type="text/markdown",
    )
    def hypermesh_fillet_chamfer_meshing_resource() -> str:
        return _read_skill_file(
            "references/fillet-chamfer-meshing.md",
            "Classify fillets and chamfers by physics, derive representable profile rows, and verify topology after any defeaturing.",
        )

    @server.resource(
        "hypermesh://guidance/shape-partition-patterns",
        name="hypermesh_shape_partition_patterns",
        title="HyperMesh Sphere and Flange Partition Patterns",
        description="Measured construction-line and block patterns for spheres, spherical shells, flanges, hubs, and bolt circles.",
        mime_type="text/markdown",
    )
    def hypermesh_shape_partition_patterns_resource() -> str:
        return _read_skill_file(
            "references/shape-partition-patterns.md",
            "Measure the center, axes, radii, PCD, holes, clearances, and thicknesses before creating sphere or flange partitions.",
        )

    @server.resource(
        "hypermesh://guidance/quality-remediation",
        name="hypermesh_quality_remediation",
        title="HyperMesh Quality Diagnosis and Remediation",
        description="Cause-driven repair order for geometry, partition, connectivity, and node-position failures.",
        mime_type="text/markdown",
    )
    def hypermesh_quality_remediation_resource() -> str:
        return _read_skill_file(
            "references/quality-remediation.md",
            "Diagnose geometry and topology before local remesh, connectivity edits, or smoothing.",
        )

    @server.resource(
        "hypermesh://guidance/tetra-quality-optimization",
        name="hypermesh_tetra_quality_optimization",
        title="HyperMesh Tetra Quality Optimization",
        description="Surface-first tetra quality audit, feature-feasibility checks, failed-patch localization, and gated remediation.",
        mime_type="text/markdown",
    )
    def hypermesh_tetra_quality_optimization_resource() -> str:
        return _read_skill_file(
            "references/tetra-quality-optimization.md",
            "Export exact tetra quality values and repair geometry or boundary triangles before node-only optimization.",
        )

    @server.resource(
        "hypermesh://server/manifest",
        name="hypermesh_server_manifest",
        title="HyperMesh MCP Manifest",
        description="Implemented primitives, protocol responsibilities, and path policy.",
        mime_type="application/json",
    )
    def hypermesh_manifest_resource() -> dict[str, Any]:
        return manifest()

    @server.prompt(
        name="hypermesh_meshing_plan",
        title="Plan a Feature-Aware HyperMesh Workflow",
        description="Create an evidence-gated HyperMesh meshing plan from explicit geometry and solver requirements.",
    )
    def hypermesh_meshing_plan(
        objective: str,
        geometry_features: str,
        solver_profile: str,
        target_size: str,
        element_type: str = "unspecified",
        quality_criteria: str = "solver-profile defaults must be made explicit",
    ) -> str:
        return f"""Plan an evidence-first HyperMesh workflow.

Objective: {objective}
Geometry/features: {geometry_features}
Downstream solver profile: {solver_profile}
Element type/order: {element_type}
Global target size and units: {target_size}
Quality criteria: {quality_criteria}

Before proposing Tcl, read hypermesh://guidance/workflow,
hypermesh://guidance/partition-strategy,
hypermesh://guidance/feature-meshing,
hypermesh://guidance/fillet-chamfer-meshing,
hypermesh://guidance/shape-partition-patterns,
hypermesh://guidance/quality-remediation,
hypermesh://guidance/tetra-quality-optimization, and
hypermesh://guidance/quality-gates. Choose a shell/quad, mapped/swept hex, or
tet route. Measure centers, axes, radii, PCD, clearances, thicknesses, and every
retained fillet/chamfer profile before creating construction lines. Write a
patch/block dependency plan before cutting, classify preserved/suppressed
features, and derive local circumferential, axial, radial, fillet/chamfer row,
washer, edge-density, bias, transition, and sweep controls. Require
machine-readable evidence for selections, post-cut topology/mappability,
entity/element counts, named quality failures, remediation, and nonempty
exports. Do not claim success from return code or file presence alone."""

    @server.tool(
        name="hypermesh_mcp_manifest",
        title="Inspect HyperMesh MCP Components",
        description="Return implemented MCP primitives, SDK responsibilities, optional client features, and path policy.",
        structured_output=True,
    )
    def hypermesh_mcp_manifest() -> dict[str, Any]:
        return manifest()

    @server.tool(
        name="hypermesh_validate_workspace_paths",
        title="Validate HyperMesh Workspace Paths",
        description="Check Tcl and run-directory paths against an explicit workspace root or environment policy.",
        structured_output=True,
    )
    def hypermesh_validate_workspace_paths(
        script_path: str,
        run_dir: str,
        workspace_root: str | None = None,
    ) -> dict[str, Any]:
        return validate_workspace_paths(script_path, run_dir, workspace_root)

    @server.tool(
        name="hypermesh_plan_partition_strategy",
        title="Plan HyperMesh Partition Strategy",
        description="Create a route-specific, auditable surface-patch or solid-block partition and meshing sequence.",
        structured_output=True,
    )
    def hypermesh_plan_partition_strategy(
        geometry_summary: str,
        mesh_route: str,
        has_symmetry: bool = False,
        has_holes_or_slots: bool = False,
        has_branches_or_intersections: bool = False,
        has_curved_sectors: bool = False,
        requires_conformal_interfaces: bool = True,
        sweep_direction_hint: str = "",
    ) -> dict[str, Any]:
        return plan_partition_strategy(
            geometry_summary,
            mesh_route,
            has_symmetry,
            has_holes_or_slots,
            has_branches_or_intersections,
            has_curved_sectors,
            requires_conformal_interfaces,
            sweep_direction_hint,
        )

    @server.tool(
        name="hypermesh_plan_size_transition",
        title="Plan HyperMesh Size Transition",
        description="Calculate auditable transition layers and actual growth between fine and coarse mesh sizes.",
        structured_output=True,
    )
    def hypermesh_plan_size_transition(
        fine_size: float,
        coarse_size: float,
        maximum_growth_ratio: float = 1.5,
        minimum_layers: int = 1,
    ) -> dict[str, Any]:
        return plan_size_transition(fine_size, coarse_size, maximum_growth_ratio, minimum_layers)

    @server.tool(
        name="hypermesh_plan_circular_feature_mesh",
        title="Plan Circular Feature Divisions",
        description="Derive auditable circular, axial, and washer division counts from sizes and symmetry constraints.",
        structured_output=True,
    )
    def hypermesh_plan_circular_feature_mesh(
        radius: float,
        target_circumferential_size: float,
        minimum_circumferential_divisions: int = 8,
        multiple_of: int = 4,
        symmetry_sectors: int = 1,
        axial_length: float | None = None,
        target_axial_size: float | None = None,
        washer_width: float | None = None,
        target_radial_size: float | None = None,
        maximum_angle_deg: float | None = None,
    ) -> dict[str, Any]:
        return plan_circular_feature_mesh(
            radius,
            target_circumferential_size,
            minimum_circumferential_divisions,
            multiple_of,
            symmetry_sectors,
            axial_length,
            target_axial_size,
            washer_width,
            target_radial_size,
            maximum_angle_deg,
        )

    @server.tool(
        name="hypermesh_plan_fillet_chamfer_mesh",
        title="Plan Fillet or Chamfer Mesh",
        description="Classify a measured fillet/chamfer and calculate auditable rows, curvature, minimum-size conflicts, transitions, and route-specific topology.",
        structured_output=True,
    )
    def hypermesh_plan_fillet_chamfer_mesh(
        feature_type: str,
        target_size: float,
        feature_radius: float | None = None,
        feature_width: float | None = None,
        feature_angle_deg: float = 90.0,
        minimum_rows: int = 2,
        maximum_turn_angle_deg: float = 20.0,
        maximum_chordal_deviation: float | None = None,
        minimum_element_size: float | None = None,
        maximum_growth_ratio: float = 1.5,
        analysis_role: str = "cosmetic",
        mesh_route: str = "shell",
    ) -> dict[str, Any]:
        return plan_fillet_chamfer_mesh(
            feature_type,
            target_size,
            feature_radius,
            feature_width,
            feature_angle_deg,
            minimum_rows,
            maximum_turn_angle_deg,
            maximum_chordal_deviation,
            minimum_element_size,
            maximum_growth_ratio,
            analysis_role,
            mesh_route,
        )

    @server.tool(
        name="hypermesh_plan_tetra_quality_remediation",
        title="Plan Tetra Quality Remediation",
        description="Diagnose exact tetra-quality evidence, size/feature conflicts, overlapping failure modes, optimizer plateaus, and a surface-first remediation sequence.",
        structured_output=True,
    )
    def hypermesh_plan_tetra_quality_remediation(
        total_elements: int,
        target_size: float,
        minimum_surface_size: float,
        minimum_geometric_feature: float | None = None,
        tet_collapse_fail_count: int = 0,
        tet_collapse_worst: float | None = None,
        tet_collapse_threshold: float = 0.10,
        jacobian_fail_count: int = 0,
        jacobian_worst: float | None = None,
        jacobian_threshold: float = 0.60,
        aspect_ratio_fail_count: int = 0,
        aspect_ratio_worst: float | None = None,
        aspect_ratio_threshold: float = 8.0,
        volumetric_skew_fail_count: int = 0,
        volumetric_skew_worst: float | None = None,
        volumetric_skew_threshold: float = 0.95,
        minimum_height_fail_count: int = 0,
        minimum_height_worst: float | None = None,
        minimum_height_threshold: float = 0.20,
        minimum_height_overlap_tet_collapse: int = 0,
        minimum_height_overlap_aspect_ratio: int = 0,
        minimum_height_overlap_volumetric_skew: int = 0,
        previous_minimum_height_fail_count: int | None = None,
        optimized_minimum_height_fail_count: int | None = None,
        protected_small_features: bool = True,
    ) -> dict[str, Any]:
        return plan_tetra_quality_remediation(
            total_elements,
            target_size,
            minimum_surface_size,
            minimum_geometric_feature,
            tet_collapse_fail_count,
            tet_collapse_worst,
            tet_collapse_threshold,
            jacobian_fail_count,
            jacobian_worst,
            jacobian_threshold,
            aspect_ratio_fail_count,
            aspect_ratio_worst,
            aspect_ratio_threshold,
            volumetric_skew_fail_count,
            volumetric_skew_worst,
            volumetric_skew_threshold,
            minimum_height_fail_count,
            minimum_height_worst,
            minimum_height_threshold,
            minimum_height_overlap_tet_collapse,
            minimum_height_overlap_aspect_ratio,
            minimum_height_overlap_volumetric_skew,
            previous_minimum_height_fail_count,
            optimized_minimum_height_fail_count,
            protected_small_features,
        )

    @server.tool(
        name="hypermesh_plan_tetra_hotspot_remediation",
        title="Plan Tetra Hotspot Remediation",
        description="Classify geometry-boundary versus interior tetra hotspots, block harmful blind refinement, and create checkpointed per-cluster Pareto remediation routes.",
        structured_output=True,
    )
    def hypermesh_plan_tetra_hotspot_remediation(
        total_elements: int,
        failed_element_count: int,
        hotspot_count: int,
        boundary_associated_failure_count: int,
        two_or_more_boundary_nodes_count: int,
        three_or_more_boundary_nodes_count: int,
        target_size: float,
        minimum_surface_size: float,
        minimum_height_fail_count: int = 0,
        minimum_height_worst: float | None = None,
        minimum_height_threshold: float = 0.20,
        tet_collapse_fail_count: int = 0,
        aspect_ratio_fail_count: int = 0,
        volumetric_skew_fail_count: int = 0,
        dominant_hotspot_element_count: int = 0,
        minimum_failed_tet_edge: float | None = None,
        minimum_associated_geometry_edge: float | None = None,
        requested_local_size: float | None = None,
        maximum_growth_ratio: float = 1.25,
        strict_pareto: bool = True,
    ) -> dict[str, Any]:
        return plan_tetra_hotspot_remediation(
            total_elements,
            failed_element_count,
            hotspot_count,
            boundary_associated_failure_count,
            two_or_more_boundary_nodes_count,
            three_or_more_boundary_nodes_count,
            target_size,
            minimum_surface_size,
            minimum_height_fail_count,
            minimum_height_worst,
            minimum_height_threshold,
            tet_collapse_fail_count,
            aspect_ratio_fail_count,
            volumetric_skew_fail_count,
            dominant_hotspot_element_count,
            minimum_failed_tet_edge,
            minimum_associated_geometry_edge,
            requested_local_size,
            maximum_growth_ratio,
            strict_pareto,
        )

    @server.tool(
        name="hypermesh_plan_tetra_zero_failure_search",
        title="Plan Tetra Zero-Failure Search",
        description="Escalate a plateaued tetra mesh through shape-preserving boundary morphing and metric-specific residual repair, then separate numerical and CAD-adherence acceptance.",
        structured_output=True,
    )
    def hypermesh_plan_tetra_zero_failure_search(
        total_elements: int,
        unique_failed_element_count: int,
        hotspot_count: int,
        boundary_associated_failure_count: int,
        two_or_more_boundary_nodes_count: int,
        tet_collapse_fail_count: int = 0,
        aspect_ratio_fail_count: int = 0,
        volumetric_skew_fail_count: int = 0,
        minimum_height_fail_count: int = 0,
        tet_collapse_worst: float | None = None,
        aspect_ratio_worst: float | None = None,
        volumetric_skew_worst: float | None = None,
        minimum_height_worst: float | None = None,
        jacobian_fail_count: int = 0,
        non_tetra_element_count: int = 0,
        plateau_detected: bool = False,
        zero_failure_required: bool = True,
        observed_maximum_boundary_displacement: float | None = None,
        maximum_allowed_boundary_displacement: float | None = None,
        current_geometry_association_change_count: int = 0,
        initial_geometry_association_change_count: int = 0,
    ) -> dict[str, Any]:
        return plan_tetra_zero_failure_search(
            total_elements=total_elements,
            unique_failed_element_count=unique_failed_element_count,
            hotspot_count=hotspot_count,
            boundary_associated_failure_count=boundary_associated_failure_count,
            two_or_more_boundary_nodes_count=two_or_more_boundary_nodes_count,
            tet_collapse_fail_count=tet_collapse_fail_count,
            aspect_ratio_fail_count=aspect_ratio_fail_count,
            volumetric_skew_fail_count=volumetric_skew_fail_count,
            minimum_height_fail_count=minimum_height_fail_count,
            tet_collapse_worst=tet_collapse_worst,
            aspect_ratio_worst=aspect_ratio_worst,
            volumetric_skew_worst=volumetric_skew_worst,
            minimum_height_worst=minimum_height_worst,
            jacobian_fail_count=jacobian_fail_count,
            non_tetra_element_count=non_tetra_element_count,
            plateau_detected=plateau_detected,
            zero_failure_required=zero_failure_required,
            observed_maximum_boundary_displacement=observed_maximum_boundary_displacement,
            maximum_allowed_boundary_displacement=maximum_allowed_boundary_displacement,
            current_geometry_association_change_count=current_geometry_association_change_count,
            initial_geometry_association_change_count=initial_geometry_association_change_count,
        )

    @server.tool(
        name="hypermesh_plan_sphere_mesh",
        title="Plan Sphere or Spherical-Shell Mesh",
        description="Derive measured sphere construction topology, great-circle counts, core/radial blocks, and shell layers.",
        structured_output=True,
    )
    def hypermesh_plan_sphere_mesh(
        radius: float,
        target_surface_size: float,
        maximum_angle_deg: float = 15.0,
        symmetry_sectors: int = 8,
        minimum_great_circle_divisions: int = 24,
        solid: bool = True,
        core_radius_ratio: float = 0.3,
        target_radial_size: float | None = None,
        shell_thickness: float | None = None,
        target_through_thickness_size: float | None = None,
    ) -> dict[str, Any]:
        return plan_sphere_mesh(
            radius,
            target_surface_size,
            maximum_angle_deg,
            symmetry_sectors,
            minimum_great_circle_divisions,
            solid,
            core_radius_ratio,
            target_radial_size,
            shell_thickness,
            target_through_thickness_size,
        )

    @server.tool(
        name="hypermesh_plan_flange_mesh",
        title="Plan Flange and Bolt-Circle Mesh",
        description="Derive flange measurements, bolt/PCD counts, ligament checks, auxiliary rings, radial lines, and axial layers.",
        structured_output=True,
    )
    def hypermesh_plan_flange_mesh(
        outer_radius: float,
        bore_radius: float,
        bolt_circle_radius: float,
        bolt_hole_radius: float,
        bolt_hole_count: int,
        target_size: float,
        maximum_angle_deg: float = 15.0,
        hub_radius: float | None = None,
        washer_width: float | None = None,
        flange_thickness: float | None = None,
        target_axial_size: float | None = None,
    ) -> dict[str, Any]:
        return plan_flange_mesh(
            outer_radius,
            bore_radius,
            bolt_circle_radius,
            bolt_hole_radius,
            bolt_hole_count,
            target_size,
            maximum_angle_deg,
            hub_radius,
            washer_width,
            flange_thickness,
            target_axial_size,
        )

    @server.tool(
        name="hypermesh_list_client_roots",
        title="List Client Roots (Compatibility)",
        description="Query roots from a supporting legacy client; roots are advisory, client-owned, and deprecated.",
        structured_output=True,
    )
    async def hypermesh_list_client_roots(ctx: Context) -> dict[str, Any]:
        return await list_client_roots(ctx)

    # Core 0.3.x exposes a thin installation check while core 0.2.x does not.
    # Replace it when present and register the same profile-owned interface in
    # either case so this package remains independently installable.
    try:
        server.remove_tool("hypermesh_check_installation")
    except ToolError:
        pass

    @server.tool(
        name="hypermesh_check_installation",
        title="Check HyperMesh Installation",
        description="Check hmbatch availability without launching a meshing workflow.",
        structured_output=True,
    )
    def hypermesh_check_installation(batch_exe: str | None = None) -> dict[str, Any]:
        from ai_cae_lab.adapters.hypermesh import hypermesh_check_install

        return hypermesh_check_install(batch_exe)

    # Replace the thin shared tool with a profile-aware version that preserves
    # its existing arguments and adds an optional explicit workspace boundary.
    try:
        server.remove_tool("hypermesh_run_tcl_file")
    except ToolError:
        # Core 0.2.x does not expose the thin adapter tool. The profile still
        # registers the workspace-aware implementation below.
        pass

    @server.tool(
        name="hypermesh_run_tcl_file",
        title="Run HyperMesh Tcl with Evidence",
        description="Run explicit Tcl through hmbatch, enforce an optional workspace root, and report logs/progress.",
        structured_output=True,
    )
    async def hypermesh_run_tcl_file(
        script_path: str,
        run_dir: str,
        ctx: Context,
        batch_exe: str | None = None,
        timeout_sec: int = 3600,
        workspace_root: str | None = None,
    ) -> dict[str, Any]:
        policy = validate_workspace_paths(script_path, run_dir, workspace_root)
        if not policy["allowed"]:
            await ctx.warning(policy["message"])
            return {"status": "blocked", "workspace_policy": policy}

        from ai_cae_lab.adapters.hypermesh import hypermesh_run_tcl

        await ctx.info(f"Starting HyperMesh Tcl: {Path(script_path).name}")
        await ctx.report_progress(0.0, total=1.0, message="Validating hmbatch and Tcl inputs")
        result = await asyncio.to_thread(
            hypermesh_run_tcl,
            script_path,
            run_dir,
            batch_exe,
            timeout_sec,
        )
        result["workspace_policy"] = policy
        await ctx.report_progress(1.0, total=1.0, message=f"HyperMesh Tcl status: {result.get('status')}")
        if result.get("status") == "completed":
            await ctx.info("HyperMesh Tcl process completed; mesh acceptance still requires evidence gates.")
        else:
            await ctx.warning(f"HyperMesh Tcl process ended with status: {result.get('status')}")
        return result

    return server
