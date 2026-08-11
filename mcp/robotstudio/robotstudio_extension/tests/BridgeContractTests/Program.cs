using System;
using System.IO;
using System.Net;
using System.Text;

using RobotStudioMcpExtension.Bridge;

namespace BridgeContractTests
{
    internal static class Program
    {
        private static int Main()
        {
            string directory = Path.Combine(Path.GetTempPath(), "RobotStudioMcpContract-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(directory);
            try
            {
                string tokenPath = Path.Combine(directory, "token");
                File.WriteAllText(tokenPath, new string('a', 64), Encoding.UTF8);
                AuthenticationService authentication = new AuthenticationService(tokenPath);
                Assert(authentication.Authenticate(new string('a', 64)), "valid token accepted");
                Assert(!authentication.Authenticate(new string('b', 64)), "invalid token rejected");
                Assert(!authentication.Authenticate(new string('a', 63)), "short token rejected");

                LengthPrefixedJson framing = new LengthPrefixedJson(1024);
                byte[] invalidHeader = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(2048));
                using (MemoryStream stream = new MemoryStream(invalidHeader))
                {
                    bool rejected = false;
                    try { framing.ReadRequest(stream); }
                    catch (BridgeFault fault) { rejected = fault.Code == "RS_PAYLOAD_TOO_LARGE"; }
                    Assert(rejected, "oversized request rejected");
                }
                Console.WriteLine("Bridge contract tests passed: 4");
                return 0;
            }
            catch (Exception exception)
            {
                Console.Error.WriteLine(exception.ToString());
                return 1;
            }
            finally
            {
                if (Directory.Exists(directory)) { Directory.Delete(directory, true); }
            }
        }

        private static void Assert(bool condition, string name)
        {
            if (!condition) { throw new InvalidOperationException("Assertion failed: " + name); }
        }
    }
}
