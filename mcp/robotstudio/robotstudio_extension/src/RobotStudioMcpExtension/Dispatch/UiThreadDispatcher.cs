using System;
using System.Threading;
using System.Windows.Forms;

using RobotStudioMcpExtension.Bridge;

namespace RobotStudioMcpExtension.Dispatch
{
    internal sealed class UiThreadDispatcher : IDisposable
    {
        private readonly Control control;
        private readonly int uiThreadId;

        internal UiThreadDispatcher()
        {
            uiThreadId = Thread.CurrentThread.ManagedThreadId;
            control = new Control();
            control.CreateControl();
        }

        internal object Invoke(Func<object> operation, int timeoutMilliseconds)
        {
            if (Thread.CurrentThread.ManagedThreadId == uiThreadId)
            {
                return operation();
            }

            object result = null;
            Exception captured = null;
            using (ManualResetEventSlim completed = new ManualResetEventSlim(false))
            {
                control.BeginInvoke(new Action(delegate
                {
                    try
                    {
                        result = operation();
                    }
                    catch (Exception exception)
                    {
                        captured = exception;
                    }
                    finally
                    {
                        completed.Set();
                    }
                }));
                if (!completed.Wait(timeoutMilliseconds))
                {
                    throw new BridgeFault("RS_TIMEOUT", "RobotStudio UI-thread request timed out.", true);
                }
            }
            if (captured != null)
            {
                throw captured;
            }
            return result;
        }

        public void Dispose()
        {
            if (!control.IsDisposed)
            {
                control.Dispose();
            }
        }
    }
}
