using System;
using System.IO;
using System.Text;

namespace RobotStudioMcpExtension.Bridge
{
    internal sealed class AuthenticationService
    {
        private readonly byte[] expected;

        internal AuthenticationService(string tokenFile)
        {
            string token = File.ReadAllText(tokenFile, Encoding.UTF8).Trim();
            expected = Encoding.UTF8.GetBytes(token);
        }

        internal bool Authenticate(string token)
        {
            byte[] actual = Encoding.UTF8.GetBytes(token ?? string.Empty);
            int difference = actual.Length ^ expected.Length;
            int length = Math.Max(actual.Length, expected.Length);
            for (int index = 0; index < length; index++)
            {
                byte left = index < actual.Length ? actual[index] : (byte)0;
                byte right = index < expected.Length ? expected[index] : (byte)0;
                difference |= left ^ right;
            }
            return difference == 0;
        }
    }
}
