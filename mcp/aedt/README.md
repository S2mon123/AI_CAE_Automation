# AEDT MCP Profile

This profile exposes the shared run, discovery, evidence, and AEDT/PyAEDT tools.
It supports user-supplied PyAEDT scripts and does not bundle AEDT, PyAEDT, or
commercial project files.

```powershell
python mcp\aedt\server.py
```

Configure `AEDT_EXE`, `AEDT_INSTALL_DIR`, and `PYAEDT_PYTHON` through the ignored
private toolchain config or environment variables. The adapter does not assume
that an HFSS-focused workflow can complete Maxwell work.
