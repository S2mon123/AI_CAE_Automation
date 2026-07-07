# Codex Skills

These skill folders can be copied into a Codex skills directory, such as:

```text
~/.codex/skills
```

Install from the repository root:

```powershell
python scripts\install_codex_assets.py --install-skills
```

The skills are intentionally named with the `ai-cae` and `evidence` theme to
distinguish this project from solver-specific skill-pack hubs. They work best
with the local MCP toolbox installed:

```powershell
python -m pip install -e ".[mcp]"
```

Current public skill packages:

| Skill | Purpose |
|---|---|
| `ai-cae-run-manager` | Run folders, evidence scans, credibility grading, reports |
| `abaqus-evidence-simulation` | Abaqus modeling, job execution, status, ODB evidence |
| `fluent-evidence-cfd` | Fluent journal/PyFluent workflow, logs, case/data evidence |
| `pcschematic-evidence-cad` | PCSCHEMATIC COM/OLE and electrical CAD evidence |
