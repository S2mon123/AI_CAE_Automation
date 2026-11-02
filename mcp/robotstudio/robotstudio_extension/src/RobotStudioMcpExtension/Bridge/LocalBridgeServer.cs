using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;

using RobotStudioMcpExtension.Configuration;
using RobotStudioMcpExtension.Dispatch;
using RobotStudioMcpExtension.Logging;

namespace RobotStudioMcpExtension.Bridge
{
    internal sealed class LocalBridgeServer : IDisposable
    {
        private readonly BridgeSettings settings;
        private readonly AuthenticationService authentication;
        private readonly MethodRegistry registry;
        private readonly UiThreadDispatcher dispatcher;
        private readonly LengthPrefixedJson framing;
        private readonly BridgeLogger logger;
        private TcpListener listener;
        private Thread acceptThread;
        private volatile bool stopping;

        internal LocalBridgeServer(
            BridgeSettings settings,
            AuthenticationService authentication,
            MethodRegistry registry,
            UiThreadDispatcher dispatcher,
            BridgeLogger logger)
        {
            this.settings = settings;
            this.authentication = authentication;
            this.registry = registry;
            this.dispatcher = dispatcher;
            this.logger = logger;
            framing = new LengthPrefixedJson(settings.max_payload_bytes);
        }

        internal void Start()
        {
            IPAddress address;
            if (!IPAddress.TryParse(settings.host, out address) || !IPAddress.Loopback.Equals(address))
            {
                throw new BridgeFault("RS_CONFIG_INVALID", "Bridge may listen only on IPv4 loopback.");
            }
            listener = new TcpListener(IPAddress.Loopback, settings.port);
            listener.Start(16);
            acceptThread = new Thread(AcceptLoop)
            {
                IsBackground = true,
                Name = "RobotStudioMcpBridgeAccept"
            };
            acceptThread.Start();
            logger.Info("Bridge listening on 127.0.0.1:" + settings.port + " with read-only method registry.");
        }

        private void AcceptLoop()
        {
            while (!stopping)
            {
                try
                {
                    TcpClient client = listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(state => ProcessClient((TcpClient)state), client);
                }
                catch (SocketException)
                {
                    if (!stopping) { logger.Error("Bridge accept failed."); }
                }
                catch (ObjectDisposedException)
                {
                    return;
                }
            }
        }

        private void ProcessClient(TcpClient client)
        {
            string requestId = null;
            Stopwatch stopwatch = Stopwatch.StartNew();
            ResponseEnvelope response;
            using (client)
            using (NetworkStream stream = client.GetStream())
            {
                try
                {
                    client.ReceiveTimeout = settings.max_request_timeout_ms;
                    client.SendTimeout = settings.max_request_timeout_ms;
                    client.NoDelay = true;
                    RequestEnvelope request = framing.ReadRequest(stream);
                    requestId = request.request_id;
                    ValidateRequest(request);
                    if (!authentication.Authenticate(request.token))
                    {
                        throw new BridgeFault("RS_BRIDGE_AUTH_FAILED", "Bridge authentication failed.");
                    }
                    int timeout = Math.Min(settings.max_request_timeout_ms, Math.Max(1000, request.timeout_ms));
                    object result = dispatcher.Invoke(
                        () => registry.Execute(request.method, request.@params),
                        timeout);
                    response = ResponseEnvelope.Success(requestId, result, stopwatch.ElapsedMilliseconds);
                    logger.Info("Request " + requestId + " method=" + request.method + " ok=true");
                }
                catch (BridgeFault fault)
                {
                    response = ResponseEnvelope.Failure(requestId, fault, stopwatch.ElapsedMilliseconds);
                    logger.Info("Request " + requestId + " failed code=" + fault.Code);
                }
                catch (EndOfStreamException exception)
                {
                    BridgeFault fault = new BridgeFault("RS_BRIDGE_PROTOCOL_ERROR", exception.Message, true);
                    response = ResponseEnvelope.Failure(requestId, fault, stopwatch.ElapsedMilliseconds);
                    logger.Info("Request " + requestId + " failed code=" + fault.Code);
                }
                catch (Exception exception)
                {
                    BridgeFault fault = new BridgeFault("RS_INTERNAL_ERROR", "RobotStudio bridge operation failed.");
                    response = ResponseEnvelope.Failure(requestId, fault, stopwatch.ElapsedMilliseconds);
                    logger.Error("Request " + requestId + " internal error type=" + exception.GetType().FullName);
                }

                try
                {
                    framing.WriteResponse(stream, response);
                }
                catch
                {
                    logger.Info("Response could not be returned for request " + requestId + ".");
                }
            }
        }

        private static void ValidateRequest(RequestEnvelope request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.request_id) || request.request_id.Length > 128)
            {
                throw new BridgeFault("RS_BRIDGE_PROTOCOL_ERROR", "request_id is required and must be <= 128 characters.");
            }
            if (string.IsNullOrWhiteSpace(request.method) || request.method.Length > 128)
            {
                throw new BridgeFault("RS_BRIDGE_PROTOCOL_ERROR", "method is required and must be <= 128 characters.");
            }
            if (string.IsNullOrWhiteSpace(request.client) || request.client.Length > 128)
            {
                throw new BridgeFault("RS_BRIDGE_PROTOCOL_ERROR", "client is required and must be <= 128 characters.");
            }
        }

        public void Dispose()
        {
            stopping = true;
            if (listener != null)
            {
                listener.Stop();
                listener = null;
            }
            if (acceptThread != null && acceptThread.IsAlive)
            {
                acceptThread.Join(2000);
            }
            logger.Info("Bridge stopped.");
        }
    }
}
