using System;
using System.Collections.Generic;
using PhysicalAI;

internal static class BridgePolicyTests
{
    private static int Main()
    {
        int count = 0;
        var config = new BridgeConfig { aliases = new Dictionary<string, string> { {"start", "unused"}, {"done", "unused"} } };
        foreach (string operation in new[] { "plc.write_bool", "plc.toggle", "plc.force", "task_execute", "start", "stop" })
            foreach (bool value in new[] {true, false})
            {
                try
                {
                    Program.Dispatch(config, new Dictionary<string, object> {
                        {"operation", operation}, {"parameters", new Dictionary<string, object> {{"alias", "start"}, {"value", value}}} });
                    throw new Exception("Unexpected dispatch success");
                }
                catch (Exception e) { if (e.Message != "WRITE_OPERATION_NOT_EXPOSED") throw; count++; }
            }
        try
        {
            Program.Dispatch(config, new Dictionary<string, object> {
                {"operation", "plc.read_bool"}, {"parameters", new Dictionary<string, object> {{"alias", "safety"}}} });
            throw new Exception("Unexpected alias success");
        }
        catch (Exception e) { if (e.Message != "ALIAS_NOT_ALLOWED") throw; count++; }
        Console.WriteLine(count + " bridge policy tests passed; no ADS library loaded.");
        return 0;
    }
}
