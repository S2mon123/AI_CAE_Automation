using System;
using System.Collections.Generic;
using System.Linq;

using ABB.Robotics.Controllers;
using ABB.Robotics.Controllers.Discovery;
using ABB.Robotics.Controllers.EventLogDomain;
using ABB.Robotics.Controllers.IOSystemDomain;
using ABB.Robotics.Controllers.RapidDomain;
using ABB.Robotics.RobotStudio.Stations;

using RobotStudioMcpExtension.Bridge;

using RapidModule = ABB.Robotics.Controllers.RapidDomain.Module;
using RapidTask = ABB.Robotics.Controllers.RapidDomain.Task;

namespace RobotStudioMcpExtension.Adapters
{
    internal sealed class ControllerAdapter
    {
        internal object Scan()
        {
            NetworkScanner scanner = new NetworkScanner();
            scanner.Scan();
            List<Dictionary<string, object>> controllers = scanner.Controllers
                .Cast<ControllerInfo>()
                .Select(ControllerInfoDetails)
                .OrderByDescending(item => (bool)item["is_virtual"])
                .ThenBy(item => Convert.ToString(item["system_name"]))
                .ToList();
            return new Dictionary<string, object>
            {
                { "controllers", controllers },
                { "count", controllers.Count },
                { "virtual_count", controllers.Count(item => (bool)item["is_virtual"]) },
                { "real_count", controllers.Count(item => !(bool)item["is_virtual"]) },
                { "real_controller_connection_performed", false }
            };
        }

        internal object Status()
        {
            return WithVirtualController(controller => new Dictionary<string, object>
            {
                { "identity", ControllerDetails(controller) },
                { "connected", controller.Connected },
                { "state", controller.State.ToString() },
                { "operating_mode", controller.OperatingMode.ToString() },
                { "run_level", controller.RunLevel.ToString() },
                { "rapid_execution_status", controller.Rapid.ExecutionStatus.ToString() },
                { "rapid_cycle", controller.Rapid.Cycle.ToString() },
                { "current_user", controller.CurrentUser != null ? controller.CurrentUser.Name : null },
                { "is_master", controller.IsMaster },
                { "is_virtual", controller.IsVirtual }
            });
        }

        internal object ProgramPointers()
        {
            return WithVirtualController(controller => new Dictionary<string, object>
            {
                { "system_id", controller.SystemId.ToString() },
                { "tasks", controller.Rapid.GetTasks().Select(task => new Dictionary<string, object>
                    {
                        { "name", task.Name },
                        { "execution_status", task.ExecutionStatus.ToString() },
                        { "program_pointer", ProgramPositionDetails(task.ProgramPointer) },
                        { "motion_pointer", ProgramPositionDetails(task.MotionPointer) }
                    }).ToList() }
            });
        }

        internal object RapidTasks()
        {
            return WithVirtualController(controller => new Dictionary<string, object>
            {
                { "system_id", controller.SystemId.ToString() },
                { "execution_status", controller.Rapid.ExecutionStatus.ToString() },
                { "tasks", controller.Rapid.GetTasks().Select(TaskDetails).ToList() }
            });
        }

        internal object RapidModules(string taskName)
        {
            return WithVirtualController(controller =>
            {
                IEnumerable<RapidTask> tasks = controller.Rapid.GetTasks();
                if (!string.IsNullOrWhiteSpace(taskName))
                {
                    tasks = tasks.Where(item => string.Equals(item.Name, taskName, StringComparison.OrdinalIgnoreCase));
                }
                List<Dictionary<string, object>> values = new List<Dictionary<string, object>>();
                foreach (RapidTask task in tasks)
                {
                    foreach (RapidModule module in task.GetModules())
                    {
                        values.Add(ModuleDetails(task, module));
                    }
                }
                if (!string.IsNullOrWhiteSpace(taskName) && values.Count == 0 &&
                    !controller.Rapid.GetTasks().Any(item => string.Equals(item.Name, taskName, StringComparison.OrdinalIgnoreCase)))
                {
                    throw new BridgeFault("RS_ENTITY_NOT_FOUND", "RAPID task was not found.");
                }
                return new Dictionary<string, object>
                {
                    { "system_id", controller.SystemId.ToString() },
                    { "task_filter", taskName },
                    { "modules", values },
                    { "count", values.Count },
                    { "module_text_exported", false },
                    { "module_text_note", "Controller file transfer requires a separately reviewed Phase 3 workflow." }
                };
            });
        }

        internal object EventLog(int startSequence, int limit, int? categoryId)
        {
            if (startSequence < 0 || limit < 1 || limit > 1000)
            {
                throw new BridgeFault("RS_INVALID_ARGUMENT", "Invalid Event Log range.");
            }
            return WithVirtualController(controller =>
            {
                List<EventLogMessage> messages = categoryId.HasValue
                    ? controller.EventLog.GetMessagesByCategory(categoryId.Value, startSequence, limit)
                    : controller.EventLog.GetAllMessages(startSequence, limit);
                return new Dictionary<string, object>
                {
                    { "system_id", controller.SystemId.ToString() },
                    { "start_sequence", startSequence },
                    { "category_id", categoryId },
                    { "limit", limit },
                    { "messages", messages.Select(EventLogMessageDetails).ToList() },
                    { "count", messages.Count }
                };
            });
        }

        internal object ListIo(int offset, int limit)
        {
            if (offset < 0 || limit < 1 || limit > 1000)
            {
                throw new BridgeFault("RS_INVALID_ARGUMENT", "Invalid I/O pagination.");
            }
            return WithVirtualController(controller =>
            {
                IEnumerable<Dictionary<string, object>> signals = controller.IOSystem
                    .GetSignals(IOFilterTypes.All)
                    .Cast<Signal>()
                    .OrderBy(signal => signal.Name)
                    .Select(SignalDetails);
                Dictionary<string, object> page = Serialization.Page(signals, offset, limit);
                page["system_id"] = controller.SystemId.ToString();
                return page;
            });
        }

        internal object ReadIoSignal(string name)
        {
            return WithVirtualController(controller =>
            {
                Signal signal;
                try
                {
                    signal = controller.IOSystem.GetSignal(name);
                }
                catch (Exception exception)
                {
                    throw new BridgeFault(
                        "RS_ENTITY_NOT_FOUND",
                        "I/O signal was not found.",
                        false,
                        new Dictionary<string, object> { { "reason", exception.Message } });
                }
                if (signal == null)
                {
                    throw new BridgeFault("RS_ENTITY_NOT_FOUND", "I/O signal was not found.");
                }
                Dictionary<string, object> result = SignalDetails(signal);
                result["system_id"] = controller.SystemId.ToString();
                return result;
            });
        }

        private static object WithVirtualController(Func<Controller, object> operation)
        {
            Controller controller = null;
            bool loggedOn = false;
            try
            {
                ControllerInfo info = FindActiveVirtualController();
                controller = Controller.Connect(info, ConnectionType.RobotStudio, false);
                if (!controller.IsVirtual)
                {
                    throw new BridgeFault("RS_CONTROLLER_NOT_VIRTUAL", "The resolved controller is not virtual.");
                }
                try
                {
                    controller.Logon(UserInfo.DefaultLocalUser);
                }
                catch
                {
                    controller.Logon(UserInfo.DefaultUser);
                }
                loggedOn = true;
                return operation(controller);
            }
            catch (BridgeFault)
            {
                throw;
            }
            catch (Exception exception)
            {
                throw new BridgeFault(
                    "RS_CONTROLLER_NOT_CONNECTED",
                    "Could not read the active virtual controller: " + exception.Message,
                    true);
            }
            finally
            {
                if (controller != null)
                {
                    if (loggedOn)
                    {
                        try { controller.Logoff(); } catch { }
                    }
                    controller.Dispose();
                }
            }
        }

        private static ControllerInfo FindActiveVirtualController()
        {
            Station station = Station.ActiveStation;
            if (station == null || station.Irc5Controllers.Count == 0)
            {
                throw new BridgeFault("RS_CONTROLLER_NOT_CONNECTED", "The active Station has no controller.", true);
            }
            RsIrc5Controller stationController = station.Irc5Controllers[0];
            Guid systemId;
            if (!Guid.TryParse(stationController.SystemId, out systemId))
            {
                throw new BridgeFault("RS_CONTROLLER_NOT_CONNECTED", "The Station controller SystemId is invalid.");
            }
            NetworkScanner scanner = new NetworkScanner();
            scanner.Scan();
            ControllerInfo info = scanner.Controllers.Cast<ControllerInfo>().FirstOrDefault(item => item.SystemId == systemId);
            if (info == null)
            {
                throw new BridgeFault("RS_CONTROLLER_NOT_CONNECTED", "The Station controller was not found by PC SDK.", true);
            }
            if (!info.IsVirtual)
            {
                throw new BridgeFault(
                    "RS_CONTROLLER_NOT_VIRTUAL",
                    "Phase 0/1 refuses to connect because the active Station controller is not virtual.");
            }
            return info;
        }

        private static Dictionary<string, object> ControllerInfoDetails(ControllerInfo info)
        {
            return new Dictionary<string, object>
            {
                { "system_id", info.SystemId.ToString() },
                { "system_name", info.SystemName },
                { "controller_name", info.ControllerName },
                { "host_name", info.HostName },
                { "ip_address", info.IPAddress != null ? info.IPAddress.ToString() : null },
                { "version", info.Version != null ? info.Version.ToString() : null },
                { "version_name", info.VersionName },
                { "availability", info.Availability.ToString() },
                { "is_virtual", info.IsVirtual },
                { "run_level", info.RunLevel.ToString() }
            };
        }

        private static Dictionary<string, object> ControllerDetails(Controller controller)
        {
            return new Dictionary<string, object>
            {
                { "system_id", controller.SystemId.ToString() },
                { "system_name", controller.SystemName },
                { "name", controller.Name },
                { "ip_address", controller.IPAddress != null ? controller.IPAddress.ToString() : null },
                { "robotware_version", controller.RobotWareVersion != null ? controller.RobotWareVersion.ToString() : null },
                { "is_robotware_7", controller.IsRobotWare7 },
                { "is_virtual", controller.IsVirtual },
                { "start_time", controller.StartTime.ToUniversalTime().ToString("O") }
            };
        }

        private static Dictionary<string, object> TaskDetails(RapidTask task)
        {
            return new Dictionary<string, object>
            {
                { "name", task.Name },
                { "enabled", task.Enabled },
                { "motion", task.Motion },
                { "task_type", task.TaskType.ToString() },
                { "execution_type", task.ExecutionType.ToString() },
                { "execution_status", task.ExecutionStatus.ToString() },
                { "cycle", task.Cycle.ToString() },
                { "module_count", task.GetModules().Length },
                { "program_pointer", ProgramPositionDetails(task.ProgramPointer) },
                { "motion_pointer", ProgramPositionDetails(task.MotionPointer) }
            };
        }

        private static Dictionary<string, object> ModuleDetails(RapidTask task, RapidModule module)
        {
            return new Dictionary<string, object>
            {
                { "task", task.Name },
                { "name", module.Name },
                { "attributes", module.Attributes.ToString() },
                { "is_system", module.IsSystem },
                { "is_read_only", module.IsReadOnly },
                { "is_encoded", module.IsEncoded },
                { "is_no_view", module.IsNoView },
                { "is_view_only", module.IsViewOnly },
                { "is_no_step_in", module.IsNoStepIn },
                { "routine_count", module.GetRoutines().Length }
            };
        }

        private static Dictionary<string, object> ProgramPositionDetails(ProgramPosition position)
        {
            if (position == null)
            {
                return null;
            }
            return new Dictionary<string, object>
            {
                { "module", position.Module },
                { "routine", position.Routine },
                { "range", position.Range.ToString() }
            };
        }

        private static Dictionary<string, object> EventLogMessageDetails(EventLogMessage message)
        {
            return new Dictionary<string, object>
            {
                { "sequence_number", message.SequenceNumber },
                { "number", message.Number },
                { "timestamp", message.Timestamp.ToUniversalTime().ToString("O") },
                { "type", message.Type.ToString() },
                { "category_id", message.CategoryId },
                { "title", message.Title },
                { "body", message.Body },
                { "name", message.Name }
            };
        }

        private static Dictionary<string, object> SignalDetails(Signal signal)
        {
            return new Dictionary<string, object>
            {
                { "name", signal.Name },
                { "type", signal.Type.ToString() },
                { "unit", signal.Unit },
                { "value", signal.Value },
                { "state", signal.State.ToString() },
                { "minimum", signal.MinValue },
                { "maximum", signal.MaxValue },
                { "input_as_physical", signal.InputAsPhysical }
            };
        }
    }
}
