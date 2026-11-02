# Read-only deployment

## 1. Host and local artifacts

Create a dedicated Python environment and install this directory. Set
`PHYSICAL_AI_WORKSPACE` outside public source. TSM inputs and validation reports
must be placed explicitly inside that workspace. The tools reject path escapes
and existing output-file overwrite. Keep raw source, private configuration, keys,
controller exports and field reports out of public Git.

The host uses `mcp.server.fastmcp` from the official `mcp==1.29.0` package. The
sibling RobotStudio server continues to use its existing `fastmcp` 2.x package;
they are different processes and protocol implementations, not interchangeable imports.

Copy `examples/host.config.example.json` to a private `host.local.json`. With null
adapters the server is fully usable for offline work and reports NOT_CONFIGURED
for physical reads. See the TOML example for Codex registration. Install the
repository's `codex-skills/abb-physical-ai` folder into the normal Codex skill
directory if needed; back up any existing folder first. Refresh the updated
`robotstudio-core` copy separately. No script silently replaces global settings.

## 2. Win7 discovery and build

Transfer this package via an already approved channel. RDP availability does not
establish file-transfer availability, Bridge port access, ADS routing or PLC state.
Do not change a working PLC adapter to host-only or enable sharing/firewall exceptions
just to make the bridge reachable.

In Win7 PowerShell, from the transferred package directory, run one discovery command:

```powershell
powershell.exe -NoProfile -File .\scripts\probe_win7.ps1 -OutputPath "$env:TEMP\physical-ai-win7-discovery.json"
```

Return both `.json` and `.json.clixml`. Optional `-ProjectRoots` names only known
project directories; the probe checks one level and never selects the newest file.
No ADS connection or COM object is created by discovery. This script targets PS2
syntax; its actual Win7 execution is still a field check.

Build the bridge on Win7 or a compatible Windows .NET Framework host:

```powershell
powershell.exe -NoProfile -File .\scripts\build_windows.ps1 -OutputDirectory .\bin -BridgeOnly
```

It compiles x86 with the installed .NET 4 compiler. A successful host build is not
proof that the VM has the required Framework or ADS runtime. Use only its legally
installed x86 `TcAdsDll.dll`; do not copy vendor DLLs from this repository.

Fill the Win7 configuration with confirmed bridge ID, management IPv4, allowed
host IP, AMS Net ID, TC2 Runtime port, exact start/done BOOL symbol spelling and
absolute DLL/key paths. The example refuses to start until `target_confirmed` is
true. It does not establish confirmation itself. A leading dot in the actual ADS
symbol is significant and must be preserved.

Generate a private random key of at least 32 bytes, store it base64 encoded in
separate local key files on host and VM, and restrict access with the site's account
and ACL policy. Never include the actual key in source, prompts or logs. Matching
keys authenticate messages but do not encrypt HTTP. Use only the reviewed private
management network; stronger transport requirements need a separately verified
Win7-compatible tunnel/TLS solution.

```powershell
.\bin\PhysicalAI.ReadOnlyBridge.exe <private-bridge-config.json>
```

HttpListener may require a pre-authorized URL reservation for the exact bind/port.
This package does not create one, open firewall ports or run an administrator shell.
If the listener cannot start, resolve that deployment policy explicitly; do not
claim a successful installation. Stop this foreground process with Ctrl+C.
No auto-start service is installed and this read-only process is not a motion supervisor.

Host `bridge` object:

```json
{
  "url": "http://192.168.1.100:8766/rpc",
  "bridge_id": "confirmed-site-bridge-id",
  "ams_net_id": "1.2.3.4.5.6",
  "ads_port": 801,
  "key_file": "C:/path/to/private/bridge.key"
}
```

All values above are placeholders. The client forbids DNS/public IPv4 endpoints,
redirects, inherited proxies and hidden retries. Both response nonce/request ID and
target bridge/AMS/port must match. Start with capabilities and Runtime state, then
read aliases. BOOL metadata mismatch fails closed; there is no absolute-address
fallback. ADS errors remain errors, not zero values.

## 3. ABB independent PC SDK proxy

Build against the installed RobotStudio 2025.3 PC SDK:

```powershell
.\scripts\build_windows.ps1 -OutputDirectory .\bin -RobotStudioBin '<installed-RobotStudio-Bin>'
```

This creates an x64 .NET Framework 4.8-hosted proxy. Vendor communication runtime
must already be installed. No RobotStudio Station SDK reference is used. Current
RobotStudio 2026/.NET 10 examples must not be treated as the 2025.3 build baseline.

Fill `abb.config.example.json` with exact controller GUID, IP, expected virtual/real
type, SDK Bin and allowed signals. The GUID must already be known to the installed
PC SDK communication runtime; this proxy does not scan networks or add controllers.
Provide credentials through the named process environment variables, never command
arguments or public config. It performs a single explicit login and no default-user
fallback. Prefer a site-managed read-only account. It compares GUID/IP/type before
performing the requested read and always logs off/disposes after the operation.

Host `abb` object:

```json
{
  "proxy_executable": "C:/path/to/bin/PhysicalAI.AbbReadOnly.exe",
  "proxy_config": "C:/path/to/private/abb.local.json",
  "controller_identity": "confirmed-controller-guid"
}
```

Available operations: `status`, `inventory`, `io` with an allowlisted signal name.
No Mastership, source export, upload, load, Motor On, Start or Stop is requested.
Reported controller options and RAPID source hashes remain UNKNOWN.

## 4. RobotStudio and validation

Keep the original `robotstudio` server and Add-In configuration. Restart its MCP
process to expose `inspect_cube_task_context`. The C# Add-In protocol did not change
and does not need rebuilding for that Python-only addition. Live Station reads
require the existing Add-In to be loaded. A missing license, controller or Station
must remain a reported blocker.

Neither server currently implements automatic path compilation/collision simulation.
An engineer may put an explicit RobotStudio review JSON under workspace inputs,
but structural validation never creates deployment or motion authorization. Follow
the supplied evidence schema and preserve missing/expired checks as INCOMPLETE.

## 5. Tests

```powershell
$env:PHYSICAL_AI_BRIDGE_TEST_EXE = '<compiled-readonly-bridge.exe>'
.\.venv\Scripts\python.exe -m pytest -q
```

The optional executable enables a real Python/C# signed-wire test in fixture mode;
it never loads ADS or listens on a network. C# policy tests compile both
`win7/ReadOnlyBridge.cs` and `tests/BridgePolicyTests.cs` with
`/main:BridgePolicyTests /platform:x86 /r:System.Web.Extensions.dll`, then run the
result. The actual ADS/ABB/Win7/Premium/VC tests remain separate field acceptance.
