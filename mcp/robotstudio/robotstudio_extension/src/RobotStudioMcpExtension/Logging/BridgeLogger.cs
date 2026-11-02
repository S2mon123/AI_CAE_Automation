using System;
using System.IO;
using System.Text;

using RobotStudioMcpExtension.Configuration;

namespace RobotStudioMcpExtension.Logging
{
    internal sealed class BridgeLogger
    {
        private readonly object sync = new object();
        private readonly string path;

        internal BridgeLogger()
        {
            string directory = Path.Combine(SettingsLoader.LocalRoot, "logs");
            Directory.CreateDirectory(directory);
            path = Path.Combine(directory, "bridge.log");
        }

        internal void Info(string message)
        {
            Write("INFO", message);
        }

        internal void Error(string message)
        {
            Write("ERROR", message);
        }

        private void Write(string level, string message)
        {
            string safe = (message ?? string.Empty).Replace("\r", " ").Replace("\n", " ");
            lock (sync)
            {
                File.AppendAllText(
                    path,
                    DateTime.UtcNow.ToString("O") + " " + level + " " + safe + Environment.NewLine,
                    new UTF8Encoding(false));
            }
        }
    }
}
