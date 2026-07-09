# COMSOL EHD Soybean Drying

This example folder documents a staged workflow for ion-wind-assisted soybean
drying in COMSOL. It is designed for public release without bundling commercial
models, solver logs, local manuals, or large result files.

## What This Example Demonstrates

- How to start with an equivalent EHD body-force model instead of overclaiming a
  full corona discharge simulation.
- How to create a run record before modeling.
- How to generate a COMSOL Java API smoke template.
- How to compile and run COMSOL Java models through MCP tools or the CLI.
- How to scan artifacts and write a credibility report.

## Suggested CLI Flow

```powershell
python -m pip install -e ".[mcp]"
ai-cae-toolbox bridge-plan --solver comsol --objective "EHD ion wind soybean drying"
ai-cae-toolbox create-run --solver comsol --case ehd-soybean-drying --objective "Staged EHD drying validation"
ai-cae-toolbox write-smoke-template --solver comsol --run-dir runs\<run-id> --case ehd-soybean-drying
ai-cae-toolbox scan-evidence runs\<run-id>
ai-cae-toolbox generate-report runs\<run-id>
```

With the MCP server installed, an agent can call the same workflow through
structured tools.

## Public Safety

Do not commit:

- `.mph` files from licensed COMSOL runs
- `.class` files produced by COMSOL compile
- local solver logs containing machine paths
- copied COMSOL manuals or API HTML
- large generated plots or videos unless they are deliberately tiny samples

Keep real run artifacts in `runs/` or a private research folder.

## Prompt

Use [`../../prompts/comsol-ehd-soybean-drying.md`](../../prompts/comsol-ehd-soybean-drying.md)
as the task prompt.
