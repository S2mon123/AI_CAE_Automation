# Evidence Chain Checklist

## Environment

- Software name and version.
- Executable path.
- Python or MCP path.
- License status or failure message.
- Operating system and working directory.

## Inputs

- Geometry/model path.
- Material source.
- Boundary conditions.
- Mesh settings.
- Solver settings.

## Execution

- Command or API entry point.
- Start time and end time.
- Logs.
- Warnings and errors.
- Job status.

## Outputs

- Project or model file.
- Solver result file.
- Images.
- CSV/JSON tables.
- Summary report.

## Credibility Grade

| Grade | Meaning |
|---|---|
| dry-run | scripts or setup generated, solver not run |
| functional validation | workflow executes, physics not yet trusted |
| visual validation | output is visible and plausible, still not calibrated |
| engineering draft | inputs and solver settings are reviewed, limitations remain |
| report-grade | validated material data, mesh study, convergence, and independent checks |

