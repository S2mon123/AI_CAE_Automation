# Third-Party Notices

AI CAE Automation Lab provides bridge wrappers and workflow templates. It does
not bundle third-party solver source code, binaries, manuals, examples, licensed
databases, or generated customer projects.

## Commercial Tools

The following product names may appear in documentation because the adapters can
connect to user-owned local installations:

- Abaqus / SIMULIA
- Ansys Fluent and Ansys Workbench
- COMSOL Multiphysics
- MATLAB / Simulink
- PCSCHEMATIC Automation
- ParaView
- OpenFOAM

All trademarks belong to their respective owners.

## Public Adapter Policy

- Keep local executable paths in environment variables or ignored private config.
- Do not commit commercial solver binaries or manuals.
- Do not commit private `.mph`, `.odb`, `.cas`, `.dat`, `.wbpj`, `.PRO`, `.slx`,
  or customer geometry files.
- Do not copy third-party MCP implementations into this repository unless their
  license and attribution are reviewed and documented.
## Design References

This project may compare its public architecture against open-source CAE/MCP
projects such as `Cai-aa/CAE-Agent-Hub`, which is published under the MIT
License. The adapter code in this repository is written for this project and is
not a disguised copy of that implementation. If source code from an MIT project
is copied in the future, keep the original copyright notice, license text, and a
clear attribution note in this file.

## MIT Reference Compliance

`Cai-aa/CAE-Agent-Hub` is used as a public comparison/reference point for CAE
agent and MCP repository organization. This repository does not vendor that
source code. If MIT-licensed source is imported later, the original copyright
notice and license text must be retained in the copied files or accompanying
notices; attribution alone is not a substitute for the MIT license notice.

The solver-specific package layout under `mcp/` follows the broad public
architecture style of CAE MCP packages, but its server wrappers and bridge code
call this repository's own `src/ai_cae_lab` implementation. The current
repository therefore treats `Cai-aa/CAE-Agent-Hub` as an acknowledged
architecture reference, not as vendored source.
