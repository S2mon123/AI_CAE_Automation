# Compatible with Windows PowerShell 2.0. Local read-only discovery, no COM activation or ADS connection.
param([Parameter(Mandatory=$true)][string]$OutputPath, [string[]]$ProjectRoots = @())
$ErrorActionPreference = 'Stop'
$report = New-Object PSObject -Property @{
    source = 'WIN7_LOCAL_PROBE'
    observed_at = [DateTime]::UtcNow.ToString('o')
    os = (Get-WmiObject Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture)
    process_bits = ([IntPtr]::Size * 8)
    dotnet = @(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' -ErrorAction SilentlyContinue | Select-Object Version,Release,Install)
    network = @(Get-WmiObject Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=True' | Select-Object Description,IPAddress,IPSubnet)
    twincat_registry = @(Get-ItemProperty 'HKLM:\SOFTWARE\Beckhoff\TwinCAT' -ErrorAction SilentlyContinue | Select-Object InstallDir,Version,AmsNetId)
    tc2_com_registered = (Test-Path 'Registry::HKEY_CLASSES_ROOT\TCatSysManager.TcSysManager')
    candidates = @()
    active_project = 'UNKNOWN'
    device_connection_performed = $false
}
$candidates = @()
foreach ($candidateRoot in $ProjectRoots) {
    # One level only. Explicit directory inputs; no full-disk recursive scan.
    foreach ($file in @(Get-ChildItem -LiteralPath $candidateRoot -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and ($_.Extension -eq '.tsm' -or $_.Extension -eq '.pro') })) {
        $candidates += New-Object PSObject -Property @{path=$file.FullName;source='EXPLICIT_PROJECT_ROOT';size=$file.Length}
    }
}
$report.candidates = $candidates
# PowerShell 2 lacks ConvertTo-Json.
Add-Type -AssemblyName System.Web.Extensions
$serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
# Export-Clixml retains WMI/PS object data faithfully on PS2; JSON summary avoids serializer recursion.
$report | Export-Clixml -Path ($OutputPath + '.clixml')
$summary = @{source=$report.source;observed_at=$report.observed_at;process_bits=$report.process_bits;tc2_com_registered=$report.tc2_com_registered;device_connection_performed=$false;details_file=($OutputPath + '.clixml');candidate_paths=@($candidates | ForEach-Object {$_.path})}
[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath), $serializer.Serialize($summary), [Text.Encoding]::UTF8)
Write-Output "Read-only report saved: $OutputPath"
