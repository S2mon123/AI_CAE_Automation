# Fluent Claim Gates

## External Flow

- Geometry-axis audit precedes rotation or force-vector definition.
- Far-field direction, drag direction, lift direction, reference area, and length are recorded.
- Mesh count, skewness, orthogonal quality, boundary layers, and y+ intent are reported.
- Residuals decrease and force coefficients stabilize; an iteration count alone is not convergence.
- Pressure, Cp, Mach, and streamlines are native Fluent exports from the solved case/data.

## Welding and Melt Pools

- Temperature only: call it thermal welding simulation.
- Liquid fraction without gas/VOF: call it solidification/melting, not a deformed free surface.
- Melt velocity with solidification: call it melt-flow modeling.
- VOF gas-metal interface: may support a free-surface claim after volume and Courant checks.
- Marangoni, recoil pressure, and evaporation require explicit model/UDF evidence.
- Spatter requires persistent detached droplets after mesh/time-step sensitivity.
- One-way temperature mapping to a structural solver is thermal-structural coupling, not strict two-way FSI.
