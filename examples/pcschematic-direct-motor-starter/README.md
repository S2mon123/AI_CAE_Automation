# PCSCHEMATIC Direct Motor Starter Example Skeleton

This folder is a public project layout for a PCSCHEMATIC Automation workflow.

It intentionally does not include proprietary component databases, symbol libraries, manuals, `.PRO` project files, or exported commercial drawings.

## Target

Generate a three-phase induction motor direct-start cabinet project with:

- main circuit,
- control circuit,
- terminal diagram,
- component list,
- terminal list,
- cable list when supported,
- PDF export.

## Suggested Layout

```text
input/
  motor_requirements.json
  component_selection_rules.md
scripts/
  generate_project.bas
  generate_project.pas
runs/
  <timestamp>/
    run.log
    project/
    exports/
    evidence.json
    report.md
```

## First Validation Target

- verify PCSCHEMATIC executable and COM/OLE registration,
- inspect database and symbol-library paths,
- create a tiny test project,
- generate or export at least one list,
- record which parts were automated and which require manual review.
