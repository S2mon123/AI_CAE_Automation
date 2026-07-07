# Electrical CAD Evidence Chain

Use this checklist for PCSCHEMATIC Automation or similar electrical CAD workflows.

## Environment

- PCSCHEMATIC executable path.
- Installation root.
- COM/OLE type library path.
- COM registration status.
- API/manual/script references used.
- Output directory and run ID.

## Inputs

- Project template or example project.
- Component database path.
- Symbol library path.
- PLC I/O table, motor list, terminal list, or design requirements.
- Voltage, power, control logic, and safety requirements.

## Generation

- Automation route: COM/OLE, built-in script, file import/export, or UI fallback.
- Generated project file.
- Created drawing pages.
- Component placement evidence.
- Terminal-strip definition.
- List generation commands.

## Outputs

- `.PRO` project.
- Component list.
- Terminal list.
- Cable list when available.
- Intelligent PDF or exported PDF.
- Run log.
- Final Markdown/JSON report.

## Review Gates

- No blank drawings.
- No invented component model or symbol.
- Every selected component traces to the database.
- Every symbol traces to the symbol library.
- Exported lists match project content.
- Unverified items are listed explicitly.

