# COMSOL MCP Tests

The repository-level tests cover the shared COMSOL bridge without requiring a
commercial COMSOL license:

```powershell
python -m unittest discover -s tests
```

Real COMSOL smoke testing requires a local licensed installation and should use
`examples/comsol-cube-10mm`.
