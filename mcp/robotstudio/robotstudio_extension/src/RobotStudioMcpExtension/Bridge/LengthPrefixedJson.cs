using System;
using System.IO;
using System.Net;
using System.Text;
using System.Web.Script.Serialization;

namespace RobotStudioMcpExtension.Bridge
{
    internal sealed class LengthPrefixedJson
    {
        private readonly int maximumPayload;
        private readonly JavaScriptSerializer serializer;

        internal LengthPrefixedJson(int maximumPayload)
        {
            this.maximumPayload = maximumPayload;
            serializer = new JavaScriptSerializer { MaxJsonLength = maximumPayload };
        }

        internal RequestEnvelope ReadRequest(Stream stream)
        {
            byte[] header = ReadExactly(stream, 4);
            int size = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(header, 0));
            if (size <= 0 || size > maximumPayload)
            {
                throw new BridgeFault(
                    "RS_PAYLOAD_TOO_LARGE",
                    "Request frame length is invalid.",
                    false,
                    new System.Collections.Generic.Dictionary<string, object> { { "size", size } });
            }
            string json = Encoding.UTF8.GetString(ReadExactly(stream, size));
            try
            {
                RequestEnvelope request = serializer.Deserialize<RequestEnvelope>(json);
                if (request == null)
                {
                    throw new BridgeFault("RS_BRIDGE_PROTOCOL_ERROR", "Request JSON is empty.");
                }
                return request;
            }
            catch (InvalidOperationException exception)
            {
                throw new BridgeFault(
                    "RS_BRIDGE_PROTOCOL_ERROR",
                    "Request is not valid JSON: " + exception.Message);
            }
        }

        internal void WriteResponse(Stream stream, ResponseEnvelope response)
        {
            byte[] payload = Encoding.UTF8.GetBytes(serializer.Serialize(response));
            if (payload.Length > maximumPayload)
            {
                BridgeFault fault = new BridgeFault("RS_PAYLOAD_TOO_LARGE", "Response exceeds maximum payload.");
                payload = Encoding.UTF8.GetBytes(serializer.Serialize(ResponseEnvelope.Failure(response.request_id, fault, 0)));
            }
            byte[] header = BitConverter.GetBytes(IPAddress.HostToNetworkOrder(payload.Length));
            stream.Write(header, 0, header.Length);
            stream.Write(payload, 0, payload.Length);
            stream.Flush();
        }

        private static byte[] ReadExactly(Stream stream, int count)
        {
            byte[] buffer = new byte[count];
            int offset = 0;
            while (offset < count)
            {
                int read = stream.Read(buffer, offset, count - offset);
                if (read == 0)
                {
                    throw new EndOfStreamException("Connection closed before a full frame was received.");
                }
                offset += read;
            }
            return buffer;
        }
    }
}
