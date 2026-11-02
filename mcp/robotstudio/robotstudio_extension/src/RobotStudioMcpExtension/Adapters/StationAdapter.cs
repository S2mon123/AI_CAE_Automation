using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

using ABB.Robotics.RobotStudio;
using ABB.Robotics.RobotStudio.Stations;

using RobotStudioMcpExtension.Bridge;

namespace RobotStudioMcpExtension.Adapters
{
    internal sealed class StationAdapter
    {
        private static Station ActiveStation()
        {
            Station station = Station.ActiveStation;
            if (station == null)
            {
                throw new BridgeFault("RS_NO_ACTIVE_STATION", "RobotStudio has no active Station.", true);
            }
            return station;
        }

        internal object GetActive()
        {
            Station station = ActiveStation();
            return new Dictionary<string, object>
            {
                { "name", station.Name },
                { "display_name", station.DisplayName },
                { "unique_id", station.UniqueId },
                { "file", station.FileInfo != null ? station.FileInfo.FullName : null },
                { "format", station.Format.ToString() },
                { "is_dirty", station.IsDirty },
                { "is_loading", Station.IsLoading },
                { "read_only", station.ReadOnly },
                { "active_task", station.ActiveTask != null ? station.ActiveTask.Name : null },
                { "controller_count", station.Irc5Controllers.Count }
            };
        }

        internal object GetSummary()
        {
            Station station = ActiveStation();
            ProjectObject[] objects = station.GetAllObjects();
            List<Dictionary<string, object>> controllers = station.Irc5Controllers
                .Cast<RsIrc5Controller>()
                .Select(ControllerSummary)
                .ToList();
            return new Dictionary<string, object>
            {
                { "station", GetActive() },
                { "object_count", objects.Length },
                { "graphic_component_count", station.GraphicComponents.Count },
                { "controller_count", station.Irc5Controllers.Count },
                { "mechanism_count", objects.OfType<Mechanism>().Count() },
                { "tool_count", objects.OfType<RsToolData>().Count() },
                { "workobject_count", objects.OfType<RsWorkObject>().Count() },
                { "robtarget_declaration_count", objects.OfType<RsRobTarget>().Count() },
                { "jointtarget_declaration_count", objects.OfType<RsJointTarget>().Count() },
                { "station_target_count", objects.OfType<RsTarget>().Count() },
                { "path_count", objects.OfType<RsPathProcedure>().Count() },
                { "controllers", controllers }
            };
        }

        internal object ListComponents(int offset, int limit)
        {
            IEnumerable<Dictionary<string, object>> items = ActiveStation().GetAllObjects()
                .OrderBy(item => item.GetType().FullName)
                .ThenBy(item => item.Name)
                .Select(Serialization.ProjectObject);
            return Serialization.Page(items, offset, limit);
        }

        internal object ListRobots(int offset, int limit)
        {
            Station station = ActiveStation();
            List<Dictionary<string, object>> items = new List<Dictionary<string, object>>();
            foreach (RsIrc5Controller controller in station.Irc5Controllers)
            {
                foreach (RsMechanicalUnit unit in controller.MechanicalUnits)
                {
                    Dictionary<string, object> value = Serialization.ProjectObject(unit);
                    value["source"] = "controller_mechanical_unit";
                    value["controller_name"] = controller.Name;
                    value["system_id"] = controller.SystemId;
                    value["mechanical_unit_type"] = unit.MechanicalUnitType.ToString();
                    value["mechanism_name"] = unit.Mechanism != null ? unit.Mechanism.Name : null;
                    value["base_frame"] = Serialization.Transform(unit.BaseFrame);
                    items.Add(value);
                }
            }
            foreach (Mechanism mechanism in station.GetAllObjects().OfType<Mechanism>())
            {
                items.Add(MechanismDetails(mechanism, false));
            }
            return Serialization.Page(items.OrderBy(item => item["name"]), offset, limit);
        }

        internal object GetRobot(string name)
        {
            Station station = ActiveStation();
            StringComparison comparison = StringComparison.OrdinalIgnoreCase;
            foreach (RsIrc5Controller controller in station.Irc5Controllers)
            {
                foreach (RsMechanicalUnit unit in controller.MechanicalUnits)
                {
                    if (string.Equals(unit.Name, name, comparison) ||
                        (unit.Mechanism != null && string.Equals(unit.Mechanism.Name, name, comparison)))
                    {
                        Dictionary<string, object> value = Serialization.ProjectObject(unit);
                        value["source"] = "controller_mechanical_unit";
                        value["controller"] = ControllerSummary(controller);
                        value["mechanical_unit_type"] = unit.MechanicalUnitType.ToString();
                        value["base_frame"] = Serialization.Transform(unit.BaseFrame);
                        value["mechanism"] = unit.Mechanism != null ? MechanismDetails(unit.Mechanism, true) : null;
                        return value;
                    }
                }
            }
            Mechanism found = station.GetAllObjects().OfType<Mechanism>()
                .FirstOrDefault(item => string.Equals(item.Name, name, comparison));
            if (found == null)
            {
                throw new BridgeFault("RS_ENTITY_NOT_FOUND", "Robot or mechanical unit was not found.");
            }
            return MechanismDetails(found, true);
        }

        internal object ListTools(int offset, int limit)
        {
            IEnumerable<Dictionary<string, object>> items = ActiveStation().GetAllObjects()
                .OfType<RsToolData>()
                .OrderBy(item => item.ModuleName)
                .ThenBy(item => item.Name)
                .Select(ToolDetails);
            return Serialization.Page(items, offset, limit);
        }

        internal object ListWorkObjects(int offset, int limit)
        {
            IEnumerable<Dictionary<string, object>> items = ActiveStation().GetAllObjects()
                .OfType<RsWorkObject>()
                .OrderBy(item => item.ModuleName)
                .ThenBy(item => item.Name)
                .Select(WorkObjectDetails);
            return Serialization.Page(items, offset, limit);
        }

        internal object ListTargets(int offset, int limit)
        {
            Station station = ActiveStation();
            List<Dictionary<string, object>> items = new List<Dictionary<string, object>>();
            items.AddRange(station.GetAllObjects().OfType<RsTarget>().Select(StationTargetDetails));
            items.AddRange(station.GetAllObjects().OfType<RsRobTarget>().Select(RobTargetDetails));
            items.AddRange(station.GetAllObjects().OfType<RsJointTarget>().Select(JointTargetDetails));
            return Serialization.Page(
                items.OrderBy(item => Convert.ToString(item["name"]))
                    .ThenBy(item => Convert.ToString(item["kind"])),
                offset,
                limit);
        }

        internal object GetTarget(string name, string moduleName)
        {
            Station station = ActiveStation();
            StringComparison comparison = StringComparison.OrdinalIgnoreCase;
            List<object> matches = new List<object>();
            matches.AddRange(station.GetAllObjects().OfType<RsTarget>()
                .Where(item => string.Equals(item.Name, name, comparison))
                .Select(StationTargetDetails));
            matches.AddRange(station.GetAllObjects().OfType<RsRobTarget>()
                .Where(item => string.Equals(item.Name, name, comparison) && ModuleMatches(item.ModuleName, moduleName))
                .Select(RobTargetDetails));
            matches.AddRange(station.GetAllObjects().OfType<RsJointTarget>()
                .Where(item => string.Equals(item.Name, name, comparison) && ModuleMatches(item.ModuleName, moduleName))
                .Select(JointTargetDetails));
            if (matches.Count == 0)
            {
                throw new BridgeFault("RS_ENTITY_NOT_FOUND", "Target was not found.");
            }
            return new Dictionary<string, object> { { "matches", matches }, { "count", matches.Count } };
        }

        internal object ListPaths(int offset, int limit)
        {
            IEnumerable<Dictionary<string, object>> items = ActiveStation().GetAllObjects()
                .OfType<RsPathProcedure>()
                .OrderBy(item => item.ModuleName)
                .ThenBy(item => item.Name)
                .Select(PathSummary);
            return Serialization.Page(items, offset, limit);
        }

        internal object GetPath(string name, string moduleName)
        {
            StringComparison comparison = StringComparison.OrdinalIgnoreCase;
            RsPathProcedure path = ActiveStation().GetAllObjects().OfType<RsPathProcedure>()
                .FirstOrDefault(item => string.Equals(item.Name, name, comparison) && ModuleMatches(item.ModuleName, moduleName));
            if (path == null)
            {
                throw new BridgeFault("RS_ENTITY_NOT_FOUND", "Path procedure was not found.");
            }
            Dictionary<string, object> result = PathSummary(path);
            result["instructions"] = path.Instructions.Cast<RsInstruction>().Select(InstructionDetails).ToList();
            return result;
        }

        private static bool ModuleMatches(string actual, string expected)
        {
            return string.IsNullOrWhiteSpace(expected) || string.Equals(actual, expected, StringComparison.OrdinalIgnoreCase);
        }

        private static Dictionary<string, object> ControllerSummary(RsIrc5Controller controller)
        {
            return new Dictionary<string, object>
            {
                { "name", controller.Name },
                { "system_id", controller.SystemId },
                { "system_path", controller.SystemPath },
                { "system_state", controller.SystemState.ToString() },
                { "task_count", controller.Tasks.Count },
                { "mechanical_unit_count", controller.MechanicalUnits.Count },
                { "tasks", controller.Tasks.Cast<RsTask>().Select(task => task.Name).ToList() }
            };
        }

        private static Dictionary<string, object> MechanismDetails(Mechanism mechanism, bool includeJoints)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(mechanism);
            value["source"] = "station_mechanism";
            value["model_name"] = mechanism.ModelName;
            value["mechanism_type"] = mechanism.MechanismType.ToString();
            value["active_joint_count"] = mechanism.NumActiveJoints;
            value["transform"] = Serialization.Transform(mechanism.Transform);
            value["task"] = mechanism.Task != null ? mechanism.Task.Name : null;
            if (includeJoints)
            {
                try
                {
                    double[] minimum;
                    double[] maximum;
                    mechanism.GetJointLimits(out minimum, out maximum);
                    value["joint_values"] = mechanism.GetJointValues();
                    value["joint_minimum"] = minimum;
                    value["joint_maximum"] = maximum;
                    value["joint_types"] = mechanism.GetJointTypes().Select(item => item.ToString()).ToArray();
                }
                catch (Exception exception)
                {
                    value["joint_read_warning"] = exception.Message;
                }
            }
            return value;
        }

        private static Dictionary<string, object> ToolDetails(RsToolData tool)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(tool);
            value["kind"] = "tooldata";
            value["module_name"] = tool.ModuleName;
            value["storage_type"] = tool.StorageType.ToString();
            value["local"] = tool.Local;
            value["robot_hold"] = tool.RobotHold;
            value["frame"] = Serialization.Transform(tool.Frame);
            return value;
        }

        private static Dictionary<string, object> WorkObjectDetails(RsWorkObject workObject)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(workObject);
            value["kind"] = "wobjdata";
            value["module_name"] = workObject.ModuleName;
            value["storage_type"] = workObject.StorageType.ToString();
            value["local"] = workObject.Local;
            value["robot_hold"] = workObject.RobotHold;
            value["user_frame_programmed"] = workObject.UserFrameProgrammed;
            value["user_frame_mechanical_unit"] = workObject.UserFrameMechanicalUnit;
            value["user_frame"] = Serialization.Transform(workObject.UserFrame);
            value["object_frame"] = Serialization.Transform(workObject.ObjectFrame);
            return value;
        }

        private static Dictionary<string, object> StationTargetDetails(RsTarget target)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(target);
            value["kind"] = "station_target";
            value["workobject"] = target.WorkObject != null ? target.WorkObject.Name : null;
            value["robtarget"] = target.RobTarget != null ? target.RobTarget.Name : null;
            value["transform"] = Serialization.Transform(target.Transform);
            value["reference_frame"] = Serialization.Transform(target.ReferenceFrame);
            return value;
        }

        private static Dictionary<string, object> RobTargetDetails(RsRobTarget target)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(target);
            value["kind"] = "robtarget_declaration";
            value["module_name"] = target.ModuleName;
            value["storage_type"] = target.StorageType.ToString();
            value["local"] = target.Local;
            value["inline"] = target.IsInline;
            value["frame"] = Serialization.Transform(target.Frame);
            value["configuration"] = Serialization.Configuration(target.ConfigurationData);
            value["configuration_status"] = target.ConfigurationStatus.ToString();
            value["external_axes_si"] = Serialization.ExternalAxes(target.GetExternalAxes(true));
            return value;
        }

        private static Dictionary<string, object> JointTargetDetails(RsJointTarget target)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(target);
            value["kind"] = "jointtarget_declaration";
            value["module_name"] = target.ModuleName;
            value["storage_type"] = target.StorageType.ToString();
            value["local"] = target.Local;
            value["inline"] = target.IsInline;
            value["robot_axes_si"] = Serialization.RobotAxes(target.GetRobotAxes(true));
            value["external_axes_si"] = Serialization.ExternalAxes(target.GetExternalAxes(true));
            return value;
        }

        private static Dictionary<string, object> PathSummary(RsPathProcedure path)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(path);
            value["module_name"] = path.ModuleName;
            value["local"] = path.Local;
            value["synchronize"] = path.Synchronize;
            value["instruction_count"] = path.Instructions.Count;
            return value;
        }

        private static Dictionary<string, object> InstructionDetails(RsInstruction instruction)
        {
            Dictionary<string, object> value = Serialization.ProjectObject(instruction);
            RsMoveInstruction move = instruction as RsMoveInstruction;
            if (move != null)
            {
                value["kind"] = "move";
                value["process_definition"] = move.ProcessDefinitionName;
                value["process_template"] = move.ProcessTemplateName;
                value["to_point"] = SafeArgument(move.GetToPointArgument);
                value["via_point"] = SafeArgument(move.GetViaPointArgument);
                value["circular_point"] = SafeArgument(move.GetCirPointArgument);
                value["tool"] = SafeArgument(move.GetToolArgument);
                value["workobject"] = SafeArgument(move.GetWObjArgument);
                value["reachability"] = move.Reachable.ToString();
            }
            else
            {
                value["kind"] = "instruction";
            }
            return value;
        }

        private static string SafeArgument(Func<RsInstructionArgument> getter)
        {
            try
            {
                RsInstructionArgument argument = getter();
                return argument != null && argument.Enabled ? argument.Value : null;
            }
            catch
            {
                return null;
            }
        }
    }
}
