from __future__ import annotations

import argparse
import json
from pathlib import Path

import gmsh


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Stage A short weld plate mesh.")
    parser.add_argument("--outdir", default="inputs", help="Output directory.")
    parser.add_argument("--nx", type=int, default=60)
    parser.add_argument("--ny", type=int, default=40)
    parser.add_argument("--nz", type=int, default=12)
    parser.add_argument("--lx", type=float, default=0.030, help="Plate length in m.")
    parser.add_argument("--ly", type=float, default=0.020, help="Plate width in m.")
    parser.add_argument("--lz", type=float, default=0.006, help="Plate thickness in m.")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    msh_out = outdir / "stageA_plate_ansys.msh"
    inp_out = outdir / "stageA_plate_abaqus.inp"
    unv_out = outdir / "stageA_plate_unv.unv"
    meta_out = outdir / "stageA_mesh_meta.json"

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("stageA_short_weld_plate")

    box = gmsh.model.occ.addBox(0.0, -args.ly / 2.0, -args.lz, args.lx, args.ly, args.lz)
    gmsh.model.occ.synchronize()
    surfaces = gmsh.model.getBoundary([(3, box)], oriented=False, recursive=False)

    groups = {"top_heat_flux": [], "bottom": [], "x_min_side": [], "x_max_side": [], "y_min_side": [], "y_max_side": []}
    tol = 1.0e-9
    for dim, tag in surfaces:
        com = gmsh.model.occ.getCenterOfMass(dim, tag)
        if abs(com[2]) < tol:
            groups["top_heat_flux"].append(tag)
        elif abs(com[2] + args.lz) < tol:
            groups["bottom"].append(tag)
        elif abs(com[0]) < tol:
            groups["x_min_side"].append(tag)
        elif abs(com[0] - args.lx) < tol:
            groups["x_max_side"].append(tag)
        elif abs(com[1] + args.ly / 2.0) < tol:
            groups["y_min_side"].append(tag)
        elif abs(com[1] - args.ly / 2.0) < tol:
            groups["y_max_side"].append(tag)

    for dim, tag in gmsh.model.getEntities(1):
        endpoints = gmsh.model.getBoundary([(dim, tag)], oriented=False, recursive=False)
        coords = [gmsh.model.getValue(0, point_tag, []) for _, point_tag in endpoints]
        dx = abs(coords[1][0] - coords[0][0])
        dy = abs(coords[1][1] - coords[0][1])
        dz = abs(coords[1][2] - coords[0][2])
        length = max(dx, dy, dz)
        if abs(length - args.lx) < tol:
            n = args.nx + 1
        elif abs(length - args.ly) < tol:
            n = args.ny + 1
        elif abs(length - args.lz) < tol:
            n = args.nz + 1
        else:
            raise RuntimeError(f"Unexpected curve length {length} for curve {tag}")
        gmsh.model.mesh.setTransfiniteCurve(tag, n)

    for dim, tag in surfaces:
        gmsh.model.mesh.setTransfiniteSurface(tag)
        gmsh.model.mesh.setRecombine(dim, tag)
    gmsh.model.mesh.setTransfiniteVolume(box)
    gmsh.model.mesh.setRecombine(3, box)

    steel_group = gmsh.model.addPhysicalGroup(3, [box])
    gmsh.model.setPhysicalName(3, steel_group, "steel_plate")
    for name, tags in groups.items():
        pg = gmsh.model.addPhysicalGroup(2, tags)
        gmsh.model.setPhysicalName(2, pg, name)

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(msh_out))
    gmsh.write(str(inp_out))
    gmsh.write(str(unv_out))

    meta = {
        "domain_m": {"x": args.lx, "y": args.ly, "z": args.lz},
        "coordinate_definition": {
            "x": "welding travel direction",
            "y": "sinusoidal weaving direction",
            "z": "thickness direction, top surface at z=0",
        },
        "divisions": {"nx": args.nx, "ny": args.ny, "nz": args.nz},
        "expected_hex_cells": args.nx * args.ny * args.nz,
        "nominal_cell_m": {"dx": args.lx / args.nx, "dy": args.ly / args.ny, "dz": args.lz / args.nz},
        "physical_groups": groups,
        "outputs": {"msh": str(msh_out), "inp": str(inp_out), "unv": str(unv_out)},
    }
    meta_out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    gmsh.finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
