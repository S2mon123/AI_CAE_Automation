// Independent PC SDK host. Does not reference RobotStudio Station SDK or request Mastership.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Web.Script.Serialization;
using ABB.Robotics.Controllers;
using ABB.Robotics.Controllers.IOSystemDomain;

internal sealed class Config
{
    public string sdk_bin { get; set; }
    public string controller_identity { get; set; }
    public string ip_address { get; set; }
    public bool? expected_virtual { get; set; }
    public bool target_confirmed { get; set; }
    public string username_env { get; set; }
    public string password_env { get; set; }
    public string[] allowed_signals { get; set; }
}

internal static class Program
{
    private static int Main(string[] args)
    {
        try
        {
            if (args.Length < 2 || args.Length > 3) throw new Exception("CONFIG_AND_OPERATION_REQUIRED");
            var config = new JavaScriptSerializer().Deserialize<Config>(File.ReadAllText(args[0]));
            if (!config.target_confirmed || !config.expected_virtual.HasValue || !Path.IsPathRooted(config.sdk_bin))
                throw new Exception("TARGET_NOT_CONFIRMED");
            Guid.Parse(config.controller_identity);
            System.Net.IPAddress.Parse(config.ip_address);
            if (!new[] { "status", "inventory", "io" }.Contains(args[1])) throw new Exception("READ_OPERATION_REQUIRED");
            AppDomain.CurrentDomain.AssemblyResolve += (sender, e) => {
                string name = new AssemblyName(e.Name).Name;
                if (!name.StartsWith("ABB.", StringComparison.Ordinal)) return null;
                string path = Path.Combine(config.sdk_bin, name + ".dll");
                return File.Exists(path) ? Assembly.LoadFrom(path) : null;
            };
            string sdk = Path.Combine(config.sdk_bin, "ABB.Robotics.Controllers.PC.dll");
            string version = System.Diagnostics.FileVersionInfo.GetVersionInfo(sdk).FileVersion;
            if (!version.StartsWith("25.3.", StringComparison.Ordinal)) throw new Exception("SDK_VERSION_MISMATCH");
            // Native PC SDK communication components must already be legally installed.
            Environment.SetEnvironmentVariable("PATH", config.sdk_bin + Path.PathSeparator + Environment.GetEnvironmentVariable("PATH"));
            Console.OutputEncoding = new System.Text.UTF8Encoding(false);
            Console.WriteLine(new JavaScriptSerializer().Serialize(Read(config, args[1], args.Length == 3 ? args[2] : null)));
            return 0;
        }
        catch (Exception e) { Console.Error.WriteLine("ABB_READ_FAILED:" + e.GetType().Name); return 1; }
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static object Read(Config c, string operation, string signalName)
    {
        string username = Environment.GetEnvironmentVariable(c.username_env ?? "PHYSICAL_AI_ABB_USER");
        string password = Environment.GetEnvironmentVariable(c.password_env ?? "PHYSICAL_AI_ABB_PASSWORD");
        if (string.IsNullOrEmpty(username) || password == null) throw new Exception("EXPLICIT_CREDENTIALS_REQUIRED");
        using (var controller = Controller.Connect(Guid.Parse(c.controller_identity), ConnectionType.Standalone, true))
        {
            if (controller.SystemId.ToString() != c.controller_identity || controller.IPAddress.ToString() != c.ip_address ||
                controller.IsVirtual != c.expected_virtual.Value) throw new Exception("TARGET_IDENTITY_MISMATCH");
            controller.Logon(new UserInfo(username, password));
            try
            {
                object result;
                if (operation == "status")
                    result = new { state = controller.State.ToString(), operating_mode = controller.OperatingMode.ToString(),
                        robotware = controller.RobotWareVersion.ToString(), rapid_execution = controller.Rapid.ExecutionStatus.ToString(),
                        is_master = controller.IsMaster, pc_interface_option = "UNKNOWN", standstill = "UNKNOWN" };
                else if (operation == "inventory")
                    result = new { tasks = controller.Rapid.GetTasks().Select(t => new {
                        name = t.Name, execution_status = t.ExecutionStatus.ToString(),
                        program_pointer = t.ProgramPointer == null ? null : new { module = t.ProgramPointer.Module, routine = t.ProgramPointer.Routine },
                        modules = t.GetModules().Select(m => new { name = m.Name, is_system = m.IsSystem,
                            is_read_only = m.IsReadOnly, routines = m.GetRoutines().Select(r => r.Name).ToArray() }).ToArray()
                    }).ToArray(), module_source_exported = false, source_hashes = "UNKNOWN" };
                else
                {
                    if (c.allowed_signals == null || !c.allowed_signals.Contains(signalName)) throw new Exception("SIGNAL_NOT_ALLOWED");
                    using (Signal s = controller.IOSystem.GetSignal(signalName))
                        result = new { name = s.Name, value = s.Value, type = s.Type.ToString(), state = s.State.ToString() };
                }
                return new { ok = true, controller_identity = controller.SystemId.ToString(),
                    source = controller.IsVirtual ? "ROBOTSTUDIO_VC" : "ABB_LIVE", observed_at = DateTime.UtcNow.ToString("O"),
                    result = result, mastership_requested = false, real_motion_authorized = false };
            }
            finally { controller.Logoff(); }
        }
    }
}
