# HyperMesh Quality Gates

- CAD import returns success and creates nonzero expected entities.
- No unresolved duplicate surfaces, intersections, or unintended free edges remain.
- Surface and volume element counts are nonzero.
- Element type and solver profile match the downstream analysis.
- Quality metrics use named criteria: aspect ratio, skew, Jacobian, warpage,
  minimum/maximum angle, tet collapse, or solver-specific checks.
- Failed element counts and percentages are exported, not hidden.
- Any quality exception is localized and justified.
- Solver-deck export completes and the deck is nonempty.

Block downstream solve claims when logs contain translator failure, nonzero
`*geomimport` error code, BatchMesher nonzero return value, zero elements, or
unresolved severe quality failures.
