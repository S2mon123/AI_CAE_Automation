using System;
using System.IO;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Web.Script.Serialization;

using RobotStudioMcpExtension.Bridge;

namespace RobotStudioMcpExtension.Configuration
{
    internal static class SettingsLoader
    {
        internal static string LocalRoot
        {
            get
            {
                return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RobotStudioMCP");
            }
        }

        internal static string SharedConfigPath
        {
            get { return Path.Combine(LocalRoot, "bridge-settings.json"); }
        }

        internal static BridgeSettings LoadOrCreate()
        {
            Directory.CreateDirectory(LocalRoot);
            BridgeSettings settings;
            JavaScriptSerializer serializer = new JavaScriptSerializer();
            if (File.Exists(SharedConfigPath))
            {
                settings = serializer.Deserialize<BridgeSettings>(File.ReadAllText(SharedConfigPath, Encoding.UTF8));
            }
            else
            {
                settings = new BridgeSettings
                {
                    host = "127.0.0.1",
                    port = 47625,
                    token_file = Path.Combine(LocalRoot, "bridge-token"),
                    max_payload_bytes = 4 * 1024 * 1024,
                    max_request_timeout_ms = 300000,
                    controller_scope = "virtual_only"
                };
                File.WriteAllText(SharedConfigPath, serializer.Serialize(settings), new UTF8Encoding(false));
            }

            Validate(settings);
            EnsureToken(settings.token_file);
            return settings;
        }

        private static void Validate(BridgeSettings settings)
        {
            if (settings == null)
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge settings are missing.");
            }
            if (!string.Equals(settings.host, "127.0.0.1", StringComparison.Ordinal))
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge host must be exactly 127.0.0.1.");
            }
            if (settings.port < 1024 || settings.port > 65535)
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge port must be between 1024 and 65535.");
            }
            if (!string.Equals(settings.controller_scope, "virtual_only", StringComparison.Ordinal))
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Only virtual_only controller scope is supported.");
            }
            if (settings.max_payload_bytes < 1024 || settings.max_payload_bytes > 16 * 1024 * 1024)
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge payload limit is outside the safe range.");
            }
            if (settings.max_request_timeout_ms < 1000 || settings.max_request_timeout_ms > 300000)
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge request timeout is outside the safe range.");
            }
            if (string.IsNullOrWhiteSpace(settings.token_file) || !Path.IsPathRooted(settings.token_file))
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge token path must be absolute.");
            }
        }

        private static void EnsureToken(string path)
        {
            if (!File.Exists(path))
            {
                byte[] bytes = new byte[32];
                using (RandomNumberGenerator random = RandomNumberGenerator.Create())
                {
                    random.GetBytes(bytes);
                }
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, Convert.ToBase64String(bytes), new UTF8Encoding(false));
            }
            string token = File.ReadAllText(path, Encoding.UTF8).Trim();
            if (token.Length < 32)
            {
                throw new BridgeFault("RS_BRIDGE_AUTH_FAILED", "Bridge token is invalid.");
            }
            RestrictToCurrentUser(path);
        }

        private static void RestrictToCurrentUser(string path)
        {
            try
            {
                SecurityIdentifier user = WindowsIdentity.GetCurrent().User;
                FileSecurity security = new FileSecurity();
                security.SetAccessRuleProtection(true, false);
                security.AddAccessRule(
                    new FileSystemAccessRule(user, FileSystemRights.FullControl, AccessControlType.Allow));
                File.SetAccessControl(path, security);
            }
            catch (UnauthorizedAccessException)
            {
                throw new BridgeFault("RS_BRIDGE_AUTH_FAILED", "Could not restrict bridge token permissions.");
            }
        }
    }
}
