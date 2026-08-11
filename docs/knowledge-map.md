# Knowledge Map

## Core Concepts

- AI-driven CAE automation
- MCP-driven desktop engineering software
- Prompt engineering for solver execution
- Evidence chain for simulation credibility
- Smoke tests before long runs
- Credibility grading for CAE results

## Topic Clusters

### Structural and explicit dynamics

- Abaqus/Explicit drilling
- element deletion and damage variables
- force, torque, energy, and status outputs
- Ansys Mechanical static, modal, contact, and thermal-structural workflows
- Solved state, MAPDL termination, reaction balance, mesh, and RST evidence

### CFD and aerodynamics

- Fluent external flow
- axis audit for geometry
- residuals, Cl/Cd, Cp, Mach, and streamline outputs
- Fluent welding: thermal, liquid fraction, melt flow, VOF, spatter, and FSI claim gates

### Multiphysics and heat transfer

- COMSOL Java automation
- conjugate heat transfer
- temperature, velocity, pressure, and maximum temperature reporting

### Electrical and electromagnetic simulation

- AEDT design and solution type selection
- Maxwell winding polarity, inductance matrix, and reciprocity
- HFSS ports, adaptive convergence, passivity, and S-parameters
- S-parameter export
- field and surface current plots

### Preprocessing and meshing

- HyperMesh CAD translator evidence
- topology cleanup and free-edge audit
- element counts, solver profiles, named quality criteria, and deck export

### Molecular dynamics and atomistic visualization

- LAMMPS minimization, equilibration, loading, thermo, and trajectories
- potential provenance, units, seeds, strain rate, and stress conventions
- OVITO modifiers, reference configurations, camera, scalar ranges, and exports
- separate upstream solve evidence from visualization evidence

### Electrical CAD documentation

- PCSCHEMATIC Automation project generation
- COM/OLE and built-in script bridge patterns
- component database and symbol-library evidence
- terminal, cable, and component list export
- intelligent PDF and engineering documentation review

### Open-source solvers and visualization

- OpenFOAM case generation
- ParaView post-processing
- LAMMPS molecular dynamics
- OVITO atomistic post-processing
- Python-based FEM agents

## Long-Term Knowledge Base Shape

```text
docs/          durable explanation
prompts/       reusable task instructions
checklists/    execution and review gates
examples/      public skeleton projects
mcp/           bridge patterns and configuration notes
scripts/       small verification tools
```
