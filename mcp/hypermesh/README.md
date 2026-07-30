# HyperMesh MCP Profile

This profile discovers `hmbatch.exe` and runs explicit, user-supplied Tcl files
through `hmbatch -tcl`. It does not assume an undocumented Python API.

```powershell
python mcp\hypermesh\server.py
```

CAD import status, nonzero entity/element counts, mesh-quality reports, and a
nonempty solver-deck export are separate evidence gates.
