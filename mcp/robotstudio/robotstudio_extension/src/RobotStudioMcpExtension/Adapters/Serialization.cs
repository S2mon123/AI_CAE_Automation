using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

using ABB.Robotics.Math;
using ABB.Robotics.RobotStudio;
using ABB.Robotics.RobotStudio.Stations;

using RobotStudioMcpExtension.Bridge;

namespace RobotStudioMcpExtension.Adapters
{
    internal static class Serialization
    {
        internal static string StringParameter(Dictionary<string, object> parameters, string name, bool required = false)
        {
            object value;
            string text = parameters != null && parameters.TryGetValue(name, out value) && value != null
                ? Convert.ToString(value, CultureInfo.InvariantCulture)
                : null;
            if (required && string.IsNullOrWhiteSpace(text))
            {
                throw new BridgeFault("RS_INVALID_ARGUMENT", "Required parameter is missing: " + name);
            }
            return text;
        }

        internal static int IntParameter(Dictionary<string, object> parameters, string name, int defaultValue)
        {
            object value;
            if (parameters == null || !parameters.TryGetValue(name, out value) || value == null)
            {
                return defaultValue;
            }
            try
            {
                return Convert.ToInt32(value, CultureInfo.InvariantCulture);
            }
            catch (Exception exception)
            {
                throw new BridgeFault("RS_INVALID_ARGUMENT", "Parameter must be an integer: " + name, false,
                    new Dictionary<string, object> { { "reason", exception.Message } });
            }
        }

        internal static int? NullableIntParameter(Dictionary<string, object> parameters, string name)
        {
            object value;
            if (parameters == null || !parameters.TryGetValue(name, out value) || value == null)
            {
                return null;
            }
            return IntParameter(parameters, name, 0);
        }

        internal static Dictionary<string, object> ProjectObject(ProjectObject value)
        {
            return new Dictionary<string, object>
            {
                { "name", value.Name },
                { "display_name", value.DisplayName },
                { "unique_id", value.UniqueId },
                { "type", value.GetType().FullName },
                { "type_display_name", value.TypeDisplayName },
                { "parent_name", value.Parent != null ? value.Parent.Name : null }
            };
        }

        internal static Dictionary<string, object> Transform(Transform value)
        {
            if (value == null)
            {
                return null;
            }
            return Matrix(value.Matrix);
        }

        internal static Dictionary<string, object> Matrix(Matrix4 value)
        {
            Vector3 translation = value.Translation;
            Quaternion quaternion = value.Quaternion;
            return new Dictionary<string, object>
            {
                { "translation", new[] { translation.x, translation.y, translation.z } },
                { "quaternion", new[] { quaternion.q1, quaternion.q2, quaternion.q3, quaternion.q4 } },
                { "matrix_elements", value.Elements },
                { "length_unit", "RobotStudio station unit" }
            };
        }

        internal static Dictionary<string, object> Configuration(ConfigurationData value)
        {
            return new Dictionary<string, object>
            {
                { "cf1", value.Cf1 },
                { "cf4", value.Cf4 },
                { "cf6", value.Cf6 },
                { "cfx", value.Cfx }
            };
        }

        internal static Dictionary<string, object> ExternalAxes(ExternalAxisValues value)
        {
            return new Dictionary<string, object>
            {
                { "eax_a", value.Eax_a },
                { "eax_b", value.Eax_b },
                { "eax_c", value.Eax_c },
                { "eax_d", value.Eax_d },
                { "eax_e", value.Eax_e },
                { "eax_f", value.Eax_f }
            };
        }

        internal static Dictionary<string, object> RobotAxes(RobotAxisValues value)
        {
            return new Dictionary<string, object>
            {
                { "rax_1", value.Rax_1 },
                { "rax_2", value.Rax_2 },
                { "rax_3", value.Rax_3 },
                { "rax_4", value.Rax_4 },
                { "rax_5", value.Rax_5 },
                { "rax_6", value.Rax_6 }
            };
        }

        internal static Dictionary<string, object> Page<T>(IEnumerable<T> source, int offset, int limit)
        {
            if (offset < 0 || limit < 1 || limit > 1000)
            {
                throw new BridgeFault("RS_INVALID_ARGUMENT", "Pagination requires offset >= 0 and 1 <= limit <= 1000.");
            }
            List<T> values = source.ToList();
            return new Dictionary<string, object>
            {
                { "offset", offset },
                { "limit", limit },
                { "total", values.Count },
                { "items", values.Skip(offset).Take(limit).ToList() },
                { "has_more", offset + limit < values.Count }
            };
        }
    }
}
