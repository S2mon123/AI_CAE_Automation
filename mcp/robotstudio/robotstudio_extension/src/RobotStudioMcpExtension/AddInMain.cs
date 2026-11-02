using System;

using RobotStudioMcpExtension.Adapters;
using RobotStudioMcpExtension.Bridge;
using RobotStudioMcpExtension.Configuration;
using RobotStudioMcpExtension.Dispatch;
using RobotStudioMcpExtension.Logging;

namespace RobotStudioMcpExtension
{
    public static class AddInEntry
    {
        private static LocalBridgeServer server;
        private static UiThreadDispatcher dispatcher;
        private static BridgeLogger logger;

        public static void AddinMain()
        {
            logger = new BridgeLogger();
            try
            {
                BridgeSettings settings = SettingsLoader.LoadOrCreate();
                dispatcher = new UiThreadDispatcher();
                MethodRegistry registry = new MethodRegistry(
                    new EnvironmentAdapter(),
                    new StationAdapter(),
                    new ControllerAdapter());
                server = new LocalBridgeServer(
                    settings,
                    new AuthenticationService(settings.token_file),
                    registry,
                    dispatcher,
                    logger);
                server.Start();
                AppDomain.CurrentDomain.ProcessExit += Shutdown;
                AppDomain.CurrentDomain.DomainUnload += Shutdown;
                logger.Info("RobotStudio MCP Add-In initialized.");
            }
            catch (Exception exception)
            {
                logger.Error("Add-In initialization failed type=" + exception.GetType().FullName + " message=" + exception.Message);
                DisposeResources();
            }
        }

        private static void Shutdown(object sender, EventArgs eventArgs)
        {
            DisposeResources();
        }

        private static void DisposeResources()
        {
            if (server != null)
            {
                server.Dispose();
                server = null;
            }
            if (dispatcher != null)
            {
                dispatcher.Dispose();
                dispatcher = null;
            }
        }
    }
}
