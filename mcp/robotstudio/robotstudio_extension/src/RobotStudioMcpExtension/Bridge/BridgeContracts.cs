using System;
using System.Collections.Generic;

namespace RobotStudioMcpExtension.Bridge
{
    internal sealed class RequestEnvelope
    {
        public string request_id { get; set; }
        public string token { get; set; }
        public string method { get; set; }
        public Dictionary<string, object> @params { get; set; }
        public int timeout_ms { get; set; }
        public string client { get; set; }
    }

    internal sealed class ErrorEnvelope
    {
        public string code { get; set; }
        public string message { get; set; }
        public Dictionary<string, object> details { get; set; }
        public bool retryable { get; set; }
    }

    internal sealed class ResponseEnvelope
    {
        public string request_id { get; set; }
        public bool ok { get; set; }
        public object result { get; set; }
        public ErrorEnvelope error { get; set; }
        public List<string> warnings { get; set; }
        public List<object> evidence { get; set; }
        public long elapsed_ms { get; set; }

        public static ResponseEnvelope Success(string requestId, object result, long elapsedMs)
        {
            return new ResponseEnvelope
            {
                request_id = requestId,
                ok = true,
                result = result,
                error = null,
                warnings = new List<string>(),
                evidence = new List<object>(),
                elapsed_ms = elapsedMs
            };
        }

        public static ResponseEnvelope Failure(string requestId, BridgeFault fault, long elapsedMs)
        {
            return new ResponseEnvelope
            {
                request_id = requestId,
                ok = false,
                result = null,
                error = new ErrorEnvelope
                {
                    code = fault.Code,
                    message = fault.Message,
                    details = fault.Details,
                    retryable = fault.Retryable
                },
                warnings = new List<string>(),
                evidence = new List<object>(),
                elapsed_ms = elapsedMs
            };
        }
    }

    internal sealed class BridgeFault : Exception
    {
        public BridgeFault(string code, string message, bool retryable = false, Dictionary<string, object> details = null)
            : base(message)
        {
            Code = code;
            Retryable = retryable;
            Details = details ?? new Dictionary<string, object>();
        }

        public string Code { get; private set; }
        public bool Retryable { get; private set; }
        public Dictionary<string, object> Details { get; private set; }
    }
}
