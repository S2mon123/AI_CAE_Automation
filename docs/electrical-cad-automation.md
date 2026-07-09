# Electrical CAD Automation

This track extends the repository beyond solver-oriented CAE into electrical engineering documentation automation.

The first target is PCSCHEMATIC Automation because electrical CAD work naturally produces auditable artifacts:

- project files,
- component and symbol references,
- terminal lists,
- component lists,
- cable lists when available,
- intelligent PDFs,
- run logs and reports.

## Automation Layers

### 1. File and database inspection

Inspect project folders, component databases, symbol libraries, manuals, script folders, and example projects before trying to generate drawings.

### 2. COM/OLE or open API bridge

When PCSCHEMATIC COM/OLE automation is available, expose small MCP tools for opening projects, creating pages, placing symbols, filling fields, and exporting lists.

### 3. Built-in scripting bridge

If Pascal/Basic scripts are the stable local route, generate scripts into a working directory and run them through PCSCHEMATIC without modifying the installation folder.

### 4. UI fallback

UI automation should be a last resort. It must produce screenshots, logs, and a clear explanation of which manual GUI steps were automated.

## Evidence Contract

An electrical CAD automation task is not complete until it records:

- software executable path,
- COM/OLE registration status,
- manuals or API references used,
- component database and symbol-library sources,
- created project path,
- exported PDF and lists,
- missing or unverified fields,
- failure point when generation cannot be completed.

## First Public Example

The starter example is a three-phase induction motor direct-start cabinet:

- main circuit,
- control circuit,
- terminal diagram,
- component list,
- terminal list,
- cable list when supported.
