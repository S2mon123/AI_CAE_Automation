using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;

namespace RobotStudioMcpExtension.Adapters
{
    internal sealed class EnvironmentAdapter
    {
        internal object Ping()
        {
            string executable = Process.GetCurrentProcess().MainModule.FileName;
            FileVersionInfo version = FileVersionInfo.GetVersionInfo(executable);
            return new Dictionary<string, object>
            {
                { "bridge_version", Assembly.GetExecutingAssembly().GetName().Version.ToString() },
                { "robotstudio_version", version.FileVersion },
                { "robotstudio_product_version", version.ProductVersion },
                { "process_id", Process.GetCurrentProcess().Id },
                { "process_name", Process.GetCurrentProcess().ProcessName },
                { "framework", Environment.Version.ToString() },
                { "architecture", Environment.Is64BitProcess ? "x64" : "x86" },
                { "utc", DateTime.UtcNow.ToString("O") },
                { "read_only", true },
                { "controller_scope", "virtual_only" }
            };
        }
    }
}
