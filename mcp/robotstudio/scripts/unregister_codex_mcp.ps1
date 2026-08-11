$ErrorActionPreference = "Stop"
& codex mcp remove robotstudio
if ($LASTEXITCODE -ne 0) { throw "Failed to unregister robotstudio MCP." }
Write-Output "Unregistered Codex MCP server 'robotstudio'."
