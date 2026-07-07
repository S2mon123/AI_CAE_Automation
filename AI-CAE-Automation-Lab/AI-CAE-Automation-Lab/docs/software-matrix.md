# Software Matrix

| Software | Automation path | Best first smoke test | Evidence to export |
|---|---|---|---|
| Abaqus | noGUI script, CAE plugin, socket bridge, file queue | start CAE or run `abaqus.bat cae noGUI=<script>` | `.sta`, `.msg`, `.odb`, viewport PNG, CSV |
| Ansys Fluent | PyFluent, journal, Fluent Meshing workflow, MCP wrapper | launch Fluent and run a tiny case or dry-run mesh check | transcript, case/data, residual CSV, force reports, contours |
| Ansys Mechanical/Workbench | RunWB2 journal, ACT extension, socket bridge | open a minimal project and read analysis count | solve output, result PNG, exported table, project archive |
| COMSOL | Java Model Builder, LiveLink, MCP wrapper | compile or run a tiny model script | `.mph`, plot PNG, table export, solver log |
| MATLAB/Simulink | official MCP server, MATLAB engine, toolbox commands | attach to MATLAB and evaluate a simple expression | model file, simulation output, figures, diagnostics |
| OpenFOAM | case file generation, shell commands, MCP wrapper | run `blockMesh` and `checkMesh` on a small case | logs, case folder, residuals, ParaView files |
| ParaView | Python script, pvpython, MCP wrapper | load a sample file and export screenshot | screenshot, state file, CSV, animation |
| PCSCHEMATIC Automation | COM/OLE automation, built-in Pascal/Basic scripts, database/symbol inspection, UI fallback | open or create a tiny `.PRO` project and export a list or PDF | `.PRO`, run log, component list, terminal list, cable list, intelligent PDF |

## Notes

- Commercial software paths are machine-specific. Do not hard-code a path in public docs unless it is a placeholder.
- Public examples should not include licensed solver assets or proprietary geometry.
- Every solver integration should have a tiny smoke test before large automation.
- Electrical CAD integrations should verify component databases, symbol libraries, terminal lists, and exported documents instead of claiming schematic generation from screenshots alone.
