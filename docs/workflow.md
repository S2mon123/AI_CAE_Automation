# AI CAE Workflow

## 1. Prepare

- Define the physics target.
- List software, version, license requirement, and executable path.
- List input geometry, material data, loads, boundary conditions, and output metrics.

## 2. Check

- Verify files exist.
- Verify Python or MCP environment exists.
- Verify the solver can be started or connected.
- Record missing pieces before touching the model.

## 3. Build

- Create or load the model.
- Audit units, axes, geometry size, and boundary orientation.
- Set material, mesh, contacts, solver controls, and output requests.

## 4. Solve

- Run the smallest meaningful case first.
- Stop or downgrade when path, license, mesh, contact, or convergence problems appear.
- Keep logs instead of hiding failures.

## 5. Export

- Export project files, logs, images, CSV/JSON, and a short report.
- Separate preview images from real solver output.
- Mark credibility as one of:
  - dry-run,
  - functional validation,
  - visual validation,
  - engineering draft,
  - report-grade result.

## 6. Review

- Compare results with expected physics.
- Identify unstable assumptions.
- Write the next minimal improvement.

