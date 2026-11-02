using System;
using System.Collections.Generic;
using System.Linq;

using RobotStudioMcpExtension.Adapters;

namespace RobotStudioMcpExtension.Bridge
{
    internal sealed class MethodRegistry
    {
        private sealed class Registration
        {
            internal string Name;
            internal string SideEffect;
            internal Func<Dictionary<string, object>, object> Handler;
        }

        private readonly Dictionary<string, Registration> methods =
            new Dictionary<string, Registration>(StringComparer.Ordinal);

        internal MethodRegistry(EnvironmentAdapter environment, StationAdapter station, ControllerAdapter controller)
        {
            Register("environment.ping", "none", parameters => environment.Ping());
            Register("capabilities.get", "none", parameters => Capabilities());
            Register("station.active", "none", parameters => station.GetActive());
            Register("station.summary", "none", parameters => station.GetSummary());
            Register("station.components", "none", parameters => station.ListComponents(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.robots", "none", parameters => station.ListRobots(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.robot", "none", parameters => station.GetRobot(
                Serialization.StringParameter(parameters, "name", true)));
            Register("station.tools", "none", parameters => station.ListTools(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.workobjects", "none", parameters => station.ListWorkObjects(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.targets", "none", parameters => station.ListTargets(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.target", "none", parameters => station.GetTarget(
                Serialization.StringParameter(parameters, "name", true),
                Serialization.StringParameter(parameters, "module_name")));
            Register("station.paths", "none", parameters => station.ListPaths(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("station.path", "none", parameters => station.GetPath(
                Serialization.StringParameter(parameters, "name", true),
                Serialization.StringParameter(parameters, "module_name")));
            Register("controller.scan", "controller_read", parameters => controller.Scan());
            Register("controller.status", "controller_read", parameters => controller.Status());
            Register("controller.program_pointer", "controller_read", parameters => controller.ProgramPointers());
            Register("rapid.tasks", "controller_read", parameters => controller.RapidTasks());
            Register("rapid.modules", "controller_read", parameters => controller.RapidModules(
                Serialization.StringParameter(parameters, "task_name")));
            Register("controller.eventlog", "controller_read", parameters => controller.EventLog(
                Serialization.IntParameter(parameters, "start_sequence", 0),
                Serialization.IntParameter(parameters, "limit", 100),
                Serialization.NullableIntParameter(parameters, "category_id")));
            Register("controller.io", "controller_read", parameters => controller.ListIo(
                Serialization.IntParameter(parameters, "offset", 0),
                Serialization.IntParameter(parameters, "limit", 200)));
            Register("controller.io_signal", "controller_read", parameters => controller.ReadIoSignal(
                Serialization.StringParameter(parameters, "name", true)));
        }

        internal object Execute(string method, Dictionary<string, object> parameters)
        {
            Registration registration;
            if (string.IsNullOrWhiteSpace(method) || !methods.TryGetValue(method, out registration))
            {
                throw new BridgeFault(
                    "RS_CAPABILITY_NOT_AVAILABLE",
                    "Bridge method is not registered.",
                    false,
                    new Dictionary<string, object> { { "method", method } });
            }
            return registration.Handler(parameters ?? new Dictionary<string, object>());
        }

        private void Register(string name, string sideEffect, Func<Dictionary<string, object>, object> handler)
        {
            methods.Add(name, new Registration { Name = name, SideEffect = sideEffect, Handler = handler });
        }

        private object Capabilities()
        {
            return new Dictionary<string, object>
            {
                { "release_phase", new[] { "phase_0", "phase_1" } },
                { "read_only", true },
                { "controller_scope", "virtual_only" },
                { "method_count", methods.Count },
                { "methods", methods.Values.OrderBy(item => item.Name).Select(item => new Dictionary<string, object>
                    {
                        { "name", item.Name },
                        { "side_effect", item.SideEffect }
                    }).ToList() },
                { "arbitrary_dispatch", false },
                { "reflection_dispatch", false },
                { "real_controller_connect", false },
                { "write_methods", new string[0] }
            };
        }
    }
}
