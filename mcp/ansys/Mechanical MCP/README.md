# Ansys Mechanical MCP Profile

This standalone profile covers three supported control routes:

- Workbench `RunWB2` journals
- Mechanical Scripting/ACT through `ExtAPI`
- PyMechanical gRPC controller scripts

```powershell
python "mcp\ansys\Mechanical MCP\server.py"
```

Success requires Mechanical `Solved` state, MAPDL normal termination, reaction
balance, acceptable mesh evidence, an `.rst`, numeric exports, images, and logs.
