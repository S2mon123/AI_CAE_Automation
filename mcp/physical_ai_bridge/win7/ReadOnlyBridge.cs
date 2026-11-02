// .NET Framework 4.x / x86. No ADS variable writes or COM activation entry points.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;

namespace PhysicalAI
{
    internal static class Wire
    {
        internal const string Protocol = "physical-ai/4.0";
        internal static readonly JavaScriptSerializer Json = new JavaScriptSerializer { MaxJsonLength = 1048576 };
        internal static long Now() { return (long)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalSeconds; }
        internal static string Mac(string b64, byte[] key, string direction)
        {
            using (var h = new HMACSHA256(key))
                return BitConverter.ToString(h.ComputeHash(Encoding.UTF8.GetBytes(Protocol + "\n" + direction + "\n" + b64))).Replace("-", "").ToLowerInvariant();
        }
        internal static bool Equal(string a, string b)
        {
            if (a == null || b == null || a.Length != b.Length) return false;
            int diff = 0; for (int i = 0; i < a.Length; i++) diff |= a[i] ^ b[i];
            return diff == 0;
        }
        internal static Dictionary<string, object> Decode(string raw, byte[] key)
        {
            var e = Json.Deserialize<Dictionary<string, object>>(raw);
            if (e.Count != 3 || (string)e["protocol"] != Protocol) throw new Exception("PROTOCOL_MISMATCH");
            string b64 = (string)e["payload_b64"];
            if (!Equal((string)e["signature"], Mac(b64, key, "request"))) throw new Exception("BAD_SIGNATURE");
            var p = Json.Deserialize<Dictionary<string, object>>(Encoding.UTF8.GetString(Convert.FromBase64String(b64)));
            if (!(p["issued_at"] is int || p["issued_at"] is long)) throw new Exception("INVALID_TIME");
            if (Math.Abs(Now() - Convert.ToInt64(p["issued_at"])) > 30) throw new Exception("EXPIRED_SIGNATURE");
            foreach (string field in new[] { "request_id", "nonce" })
                if (!Regex.IsMatch((string)p[field], "\\A[a-f0-9]{32}\\z")) throw new Exception("INVALID_BINDING");
            return p;
        }
        internal static byte[] Encode(object payload, byte[] key)
        {
            string b64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(Json.Serialize(payload)));
            return Encoding.UTF8.GetBytes(Json.Serialize(new { protocol = Protocol, payload_b64 = b64, signature = Mac(b64, key, "response") }));
        }
    }

    internal sealed class BridgeConfig
    {
        public string bind_ip { get; set; }
        public int port { get; set; }
        public string[] allowed_clients { get; set; }
        public string key_file { get; set; }
        public string bridge_id { get; set; }
        public bool target_confirmed { get; set; }
        public string ams_net_id { get; set; }
        public int ads_port { get; set; }
        public string ads_dll { get; set; }
        public Dictionary<string, string> aliases { get; set; }
        internal void Validate()
        {
            IPAddress ip;
            if (!IPAddress.TryParse(bind_ip, out ip) || ip.AddressFamily != System.Net.Sockets.AddressFamily.InterNetwork)
                throw new Exception("EXPLICIT_BIND_IPV4_REQUIRED");
            byte[] b = ip.GetAddressBytes();
            if (!(b[0] == 127 || b[0] == 10 || b[0] == 172 && b[1] >= 16 && b[1] <= 31 || b[0] == 192 && b[1] == 168))
                throw new Exception("PRIVATE_MANAGEMENT_INTERFACE_REQUIRED");
            if (!target_confirmed || string.IsNullOrEmpty(bridge_id)) throw new Exception("TARGET_NOT_CONFIRMED");
            string[] parts = (ams_net_id ?? "").Split('.');
            if (parts.Length != 6 || parts.Any(x => { byte v; return !byte.TryParse(x, out v); })) throw new Exception("INVALID_AMS");
            if (!new[] {801, 811, 821, 831}.Contains(ads_port)) throw new Exception("TC2_RUNTIME_PORT_REQUIRED");
            if (port < 1024 || port > 65535 || allowed_clients == null || allowed_clients.Length == 0)
                throw new Exception("INVALID_LISTENER_CONFIG");
            if (!Path.IsPathRooted(key_file) || !Path.IsPathRooted(ads_dll)) throw new Exception("ABSOLUTE_LOCAL_PATH_REQUIRED");
            if (aliases == null || aliases.Keys.Any(x => x != "start" && x != "done") || aliases.Count != 2)
                throw new Exception("START_DONE_READ_ALIASES_REQUIRED");
            foreach (string name in aliases.Values)
                if (string.IsNullOrEmpty(name) || name.Length > 255 || name.Any(c => c < 32 || c > 126))
                    throw new Exception("ASCII_SYMBOL_REQUIRED");
        }
    }

    internal sealed class AdsReader : IDisposable
    {
        [StructLayout(LayoutKind.Sequential, Pack = 1)]
        private struct Address { [MarshalAs(UnmanagedType.ByValArray, SizeConst = 6)] public byte[] net; public ushort port; }
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern IntPtr LoadLibraryEx(string path, IntPtr reserved, uint flags);
        [DllImport("kernel32.dll", CharSet = CharSet.Ansi)] private static extern IntPtr GetProcAddress(IntPtr module, string name);
        [DllImport("kernel32.dll")] private static extern bool FreeLibrary(IntPtr module);
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] private delegate int PortFn();
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] private delegate int StateFn(ref Address a, out ushort state, out ushort device);
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] private delegate int ReadFn(ref Address a, uint group, uint offset, uint len, [Out] byte[] data);
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] private delegate int InfoFn(ref Address a, uint group, uint offset, uint readLen, [Out] byte[] read, uint writeLen, byte[] write);
        private IntPtr module;
        private PortFn close;
        private ReadFn read;
        private InfoFn info;
        private StateFn state;
        private Address address;
        private bool opened;
        private T Function<T>(string name) where T : class
        {
            IntPtr p = GetProcAddress(module, name);
            if (p == IntPtr.Zero) throw new Exception("ADS_EXPORT_MISSING");
            return Marshal.GetDelegateForFunctionPointer(p, typeof(T)) as T;
        }
        internal AdsReader(BridgeConfig c)
        {
            if (IntPtr.Size != 4) throw new Exception("WIN7_X86_REQUIRED");
            if (!File.Exists(c.ads_dll) || !string.Equals(Path.GetFileName(c.ads_dll), "TcAdsDll.dll", StringComparison.OrdinalIgnoreCase))
                throw new Exception("INSTALLED_ADS_DLL_REQUIRED");
            module = LoadLibraryEx(c.ads_dll, IntPtr.Zero, 8); // Absolute installed vendor path; never package the DLL.
            if (module == IntPtr.Zero) throw new Exception("ADS_DLL_LOAD_FAILED");
            try
            {
                close = Function<PortFn>("AdsPortClose"); read = Function<ReadFn>("AdsSyncReadReq");
                info = Function<InfoFn>("AdsSyncReadWriteReq"); state = Function<StateFn>("AdsSyncReadStateReq");
                opened = Function<PortFn>("AdsPortOpen")() != 0;
                if (!opened) throw new Exception("ADS_ROUTER_UNAVAILABLE");
                address = new Address { net = c.ams_net_id.Split('.').Select(byte.Parse).ToArray(), port = (ushort)c.ads_port };
            }
            catch { Dispose(); throw; }
        }
        private static void Check(int code) { if (code != 0) throw new Exception("ADS_ERROR_" + code); }
        internal object State()
        {
            ushort ads, device; Check(state(ref address, out ads, out device));
            return new { ads_state = ads, device_state = device, source = "ADS_RUNTIME", profinet_status = "UNKNOWN" };
        }
        private byte SymbolVersion()
        {
            byte[] data = new byte[1]; Check(read(ref address, 0xF008, 0, 1, data)); return data[0];
        }
        internal object ReadBool(string name)
        {
            byte version = SymbolVersion();
            byte[] symbol = Encoding.ASCII.GetBytes(name + "\0"), entry = new byte[65535];
            // This R&W service only queries declaration metadata; there is no PLC value write.
            Check(info(ref address, 0xF009, 0, (uint)entry.Length, entry, (uint)symbol.Length, symbol));
            uint length = BitConverter.ToUInt32(entry, 0), size = BitConverter.ToUInt32(entry, 12);
            uint type = BitConverter.ToUInt32(entry, 16);
            int nameLength = BitConverter.ToUInt16(entry, 24), typeLength = BitConverter.ToUInt16(entry, 26);
            if (length < 30 || length > entry.Length || 30 + nameLength + 1 + typeLength + 1 > length)
                throw new Exception("ADS_SYMBOL_METADATA_INVALID");
            string actualName = Encoding.ASCII.GetString(entry, 30, nameLength);
            string actualType = Encoding.ASCII.GetString(entry, 31 + nameLength, typeLength);
            if (actualName != name || size != 1 || type != 33 || actualType != "BOOL")
                throw new Exception("ADS_SYMBOL_BOOL_TYPE_MISMATCH");
            uint group = BitConverter.ToUInt32(entry, 4), offset = BitConverter.ToUInt32(entry, 8);
            byte[] value = new byte[1]; Check(read(ref address, group, offset, 1, value));
            if (SymbolVersion() != version) throw new Exception("ADS_SYMBOL_VERSION_CHANGED");
            if (value[0] > 1) throw new Exception("ADS_BOOL_VALUE_INVALID");
            return new { symbol = name, type = actualType, value = value[0] == 1, symbol_version = version,
                         source = "ADS_RUNTIME", abb_input_observed = false, motion_completed = false };
        }
        public void Dispose()
        {
            if (opened && close != null) { close(); opened = false; }
            if (module != IntPtr.Zero) { FreeLibrary(module); module = IntPtr.Zero; }
        }
    }

    internal static class Program
    {
        private static readonly Dictionary<string, long> Seen = new Dictionary<string, long>();
        internal static object Dispatch(BridgeConfig c, Dictionary<string, object> p)
        {
            string operation = (string)p["operation"];
            var parameters = (Dictionary<string, object>)p["parameters"];
            if (operation == "system.capabilities")
                return new { operations = new[] { "system.capabilities", "plc.state", "plc.read_bool" },
                             device_writes = false, stop_available = false, source = "BRIDGE_LOCAL" };
            if (operation != "plc.state" && operation != "plc.read_bool") throw new Exception("WRITE_OPERATION_NOT_EXPOSED");
            string alias = null;
            if (operation == "plc.read_bool")
            {
                if (parameters.Count != 1 || !parameters.ContainsKey("alias")) throw new Exception("ALIAS_REQUIRED");
                alias = (string)parameters["alias"];
                if (!c.aliases.ContainsKey(alias)) throw new Exception("ALIAS_NOT_ALLOWED");
            }
            else if (parameters.Count != 0) throw new Exception("UNEXPECTED_PARAMETERS");
            using (var ads = new AdsReader(c)) return operation == "plc.state" ? ads.State() : ads.ReadBool(c.aliases[alias]);
        }
        private static int Main(string[] args)
        {
            try
            {
                // Offline protocol fixture mode never opens an ADS port or a network listener.
                if (args.Length == 4 && args[0] == "--protocol-test")
                {
                    byte[] testKey = Convert.FromBase64String(File.ReadAllText(args[1]).Trim());
                    var request = Wire.Decode(File.ReadAllText(args[2]), testKey);
                    Console.Write(Encoding.UTF8.GetString(Wire.Encode(new { request_id = request["request_id"],
                        nonce = request["nonce"], issued_at = Wire.Now(), source = "TEST_DOUBLE", test = args[3] }, testKey)));
                    return 0;
                }
                if (args.Length != 1) throw new Exception("USAGE_CONFIG_REQUIRED");
                var c = Wire.Json.Deserialize<BridgeConfig>(File.ReadAllText(args[0])); c.Validate();
                byte[] key = Convert.FromBase64String(File.ReadAllText(c.key_file).Trim());
                if (key.Length < 32) throw new Exception("KEY_TOO_SHORT");
                using (var listener = new HttpListener())
                {
                    listener.Prefixes.Add("http://" + c.bind_ip + ":" + c.port + "/");
                    listener.Start();
                    Console.Error.WriteLine("Read-only Physical AI v4 bridge listening. No Stop or write support.");
                    while (true)
                    {
                        var context = listener.GetContext();
                        try { Handle(context, c, key); }
                        catch { context.Response.StatusCode = 403; }
                        finally { context.Response.Close(); }
                    }
                }
            }
            catch (Exception e) { Console.Error.WriteLine("BRIDGE_FAILED:" + e.GetType().Name); return 1; }
        }
        private static void Handle(HttpListenerContext context, BridgeConfig c, byte[] key)
        {
            var r = context.Request;
            if (r.HttpMethod != "POST" || r.RawUrl != "/rpc" || !c.allowed_clients.Contains(r.RemoteEndPoint.Address.ToString()) ||
                r.ContentLength64 < 1 || r.ContentLength64 > 1048576) throw new Exception("REQUEST_DENIED");
            byte[] raw = new byte[(int)r.ContentLength64];
            int read = 0;
            while (read < raw.Length) { int count = r.InputStream.Read(raw, read, raw.Length - read); if (count == 0) throw new Exception("TRUNCATED"); read += count; }
            var p = Wire.Decode(Encoding.UTF8.GetString(raw), key);
            long now = Wire.Now(); string nonce = (string)p["nonce"];
            foreach (string expired in Seen.Where(x => x.Value < now).Select(x => x.Key).ToArray()) Seen.Remove(expired);
            if (Seen.ContainsKey(nonce) || Seen.Count >= 4096) throw new Exception("REPLAY_REJECTED");
            Seen.Add(nonce, Convert.ToInt64(p["issued_at"]) + 30);
            object result = null; string error = null;
            try { result = Dispatch(c, p); }
            catch (Exception e) { error = e.Message.StartsWith("ADS_") || e.Message == "WRITE_OPERATION_NOT_EXPOSED" || e.Message == "ALIAS_NOT_ALLOWED" ? e.Message : "READ_FAILED"; }
            byte[] response = Wire.Encode(new { request_id = p["request_id"], nonce = nonce, issued_at = Wire.Now(),
                target = new { c.bridge_id, c.ams_net_id, c.ads_port }, ok = error == null, code = error,
                result = result, quality = error == null ? "OBSERVED" : "UNKNOWN" }, key);
            context.Response.ContentType = "application/json"; context.Response.ContentLength64 = response.Length;
            context.Response.OutputStream.Write(response, 0, response.Length);
        }
    }
}
