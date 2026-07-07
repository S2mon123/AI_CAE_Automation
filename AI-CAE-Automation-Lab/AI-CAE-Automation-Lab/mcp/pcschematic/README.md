# PCSCHEMATIC MCP Design Notes

This folder describes a future MCP bridge for PCSCHEMATIC Automation. It is a design skeleton, not a bundled PCSCHEMATIC plugin.

## Purpose

Expose electrical CAD automation as small auditable tools:

- inspect installation and COM/OLE registration,
- open or create a project,
- inspect component databases and symbol libraries,
- import PLC I/O or component tables,
- generate drawings through API or scripts,
- export component, terminal, cable, and PDF evidence,
- write a run report.

## Suggested Tools

| Tool | Purpose |
|---|---|
| `pcschematic_status` | Report executable, installation root, COM/OLE registration, manuals, scripts, databases, symbols |
| `pcschematic_search_docs` | Search local COM/OLE HTML docs and script examples |
| `pcschematic_select_component` | Find real database components matching electrical requirements |
| `pcschematic_select_symbol` | Find real symbol-library entries |
| `pcschematic_create_project` | Create a new project in a safe output directory |
| `pcschematic_run_script` | Run a generated Pascal/Basic script without modifying installation files |
| `pcschematic_export_lists` | Export component, terminal, and cable lists |
| `pcschematic_export_pdf` | Export intelligent PDF or ordinary PDF when supported |
| `pcschematic_report` | Write a Markdown/JSON evidence report |

## Safety Rules

- Never edit files inside the PCSCHEMATIC installation directory.
- Never overwrite old projects or exports.
- Never invent component models, manufacturers, pins, or symbol filenames.
- Treat UI automation as fallback only.
- Always record whether COM/OLE, built-in script, file import/export, or UI fallback was used.

## First Example

The first target workflow is a three-phase induction motor direct-start cabinet:

- main circuit,
- control circuit,
- terminal diagram,
- component list,
- terminal list,
- cable list when supported,
- PDF export.

