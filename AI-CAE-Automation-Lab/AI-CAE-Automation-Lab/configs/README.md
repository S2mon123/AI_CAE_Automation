# Configuration Examples

This folder contains public-safe configuration examples. Copy them outside the
repository before adding local machine paths, license settings, or private
project locations.

The first milestone uses environment variables instead of committed local paths:

| Solver | Suggested environment variables |
|---|---|
| Abaqus | `ABAQUS_COMMAND` |
| Ansys Workbench | `ANSYS_ROOT`, `WORKBENCH_EXE`, `ANSYS_WORKBENCH_EXE` |
| Ansys Fluent | `FLUENT_EXE`, `FLUENT_ROOT` |
| COMSOL | `COMSOL_EXE`, `COMSOL_ROOT`, `COMSOL_BATCH`, `COMSOL_JAVA` |
| MATLAB | `MATLAB_EXE`, `MATLABROOT` |
| PCSCHEMATIC | `PCSCHEMATIC_EXE`, `PCSCHEMATIC_ROOT`, `PCSCHEMATIC_TLB` |

Do not commit real customer models, licensed manuals, raw solver outputs, or
private installation paths.
