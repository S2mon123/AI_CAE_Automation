namespace RobotStudioMcpExtension.Configuration
{
    internal sealed class BridgeSettings
    {
        public string host { get; set; }
        public int port { get; set; }
        public string token_file { get; set; }
        public int max_payload_bytes { get; set; }
        public int max_request_timeout_ms { get; set; }
        public string controller_scope { get; set; }
    }
}
