# Software Matrix

| Software | Automation path | Best first smoke test | Evidence to export |
|---|---|---|---|
| Ansys Electronics Desktop | PyAEDT, AEDT scripting, solver-scoped MCP | import `ansys.aedt.core` and start a disposable desktop | `.aedt`, design/solution type, adaptive log, matrix/S-parameter CSV, native fields |
| Abaqus | noGUI script, CAE plugin, socket bridge, file queue | start CAE or run `abaqus.bat cae noGUI=<script>` | `.sta`, `.msg`, `.odb`, viewport PNG, CSV |
| Ansys Fluent | PyFluent, journal, Fluent Meshing workflow, MCP wrapper | launch Fluent and run a tiny case or dry-run mesh check | transcript, case/data, residual CSV, force reports, contours |
| Ansys Mechanical | RunWB2 journal, ACT/ExtAPI, PyMechanical gRPC | start one control route and read application/analysis state | Solved state, `solve.out`, reactions, mesh, `.rst`, CSV/JSON, native PNG |
| Ansys Workbench | RunWB2 journal and project orchestration | open a minimal project and inspect systems | journal log, `.wbpj`, project archive, downstream solver evidence |
| Altair HyperMesh | Tcl, `hmbatch -tcl`, BatchMesher | print a marker through hmbatch, then import tiny public CAD | import return code, entity/element counts, quality CSV, `.hm`, solver deck |
| LAMMPS | input scripts, command line, MPI build | run the zero-potential parser smoke | `log.lammps`, thermo CSV, data/restart, trajectory, derived curves |
| OVITO | GUI, `ovitos`, external Python package | import `ovito` and print its version | pipeline script, modifier parameters, tables, PNG/MP4, state/provenance note |
| COMSOL | Java Model Builder, LiveLink, MCP wrapper | compile or run a tiny model script | `.mph`, plot PNG, table export, solver log |
| MATLAB/Simulink | official MCP server, MATLAB engine, toolbox commands | attach to MATLAB and evaluate a simple expression | model file, simulation output, figures, diagnostics |
| OpenFOAM | case file generation, shell commands, MCP wrapper | run `blockMesh` and `checkMesh` on a small case | logs, case folder, residuals, ParaView files |
| ParaView | Python script, pvpython, MCP wrapper | load a sample file and export screenshot | screenshot, state file, CSV, animation |
| PCSCHEMATIC Automation | COM/OLE automation, built-in Pascal/Basic scripts, database/symbol inspection, UI fallback | open or create a tiny `.PRO` project and export a list or PDF | `.PRO`, run log, component list, terminal list, cable list, intelligent PDF |

## Notes

- Commercial software paths are machine-specific. Do not hard-code a path in public docs unless it is a placeholder.
- Public examples should not include licensed solver assets or proprietary geometry.
- Every solver integration should have a tiny smoke test before large automation.
- OVITO rendering is postprocessing evidence, not proof that an upstream LAMMPS
  solve completed or is physically valid.
- Interatomic-potential files require separate redistribution-rights review.
- Electrical CAD integrations should verify component databases, symbol libraries, terminal lists, and exported documents instead of claiming schematic generation from screenshots alone.
