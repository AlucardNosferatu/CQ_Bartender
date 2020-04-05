using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using System.Windows.Automation;
using EventHook.Hooks;

namespace CQCS
{
    public delegate bool CallBack(int hwnd, int lParam);
    class Program
    {
        public delegate bool EnumWindowsProc(IntPtr hwnd, IntPtr lParam);

        private const int BM_CLICK = 0xF5;

        [DllImport("user32.dll", EntryPoint = "SendMessageA")]
        private static extern int SendMessage(IntPtr hwnd, uint wMsg, int wParam, int lParam);

        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, IntPtr lpString, int nMaxCount);

        [DllImport("user32")]
        public static extern int EnumWindows(CallBack x, int y);

        [DllImport("user32.dll")]
        private static extern int GetWindowTextW(IntPtr hWnd, [MarshalAs(UnmanagedType.LPWStr)]StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll")]
        private extern static IntPtr FindWindow(string lpClassName, string lpWindowName);

        [DllImport("user32.dll")]
        private static extern IntPtr FindWindowEx(IntPtr hWnd1, IntPtr hWnd2, string lpsz1, string lpsz2);

        [DllImport("user32.dll")]
        public static extern bool EnumChildWindows(IntPtr hwndParent, EnumWindowsProc lpEnumFunc, IntPtr lParam);

        public static int handle = 0;

        public static List<string> HandleList = new List<string>();
        public static bool Report(int hwnd, int lParam)
        {
            StringBuilder sb = new StringBuilder(256);
            GetWindowTextW((IntPtr)hwnd, sb, sb.Capacity);
            String szWindowName = sb.ToString();
            if (szWindowName == "酷Q Pro 5.15.9") {
                if (Program.handle != hwnd)
                {
                    Program.handle = hwnd;
                    Console.Write("Window handle of" + szWindowName + " is :");
                    Console.WriteLine(hwnd);
                }
            }
            return true;
        }

        public static void UseEnumWin() {
            CallBack myCallBack = new CallBack(Program.Report);
            while (true)
            {
                EnumWindows(myCallBack, 0);
            }
        }

        private static bool EnumWindowsMethod(IntPtr hWnd, IntPtr lParam)
        {
            IntPtr lpString = Marshal.AllocHGlobal(200);
            GetWindowText(hWnd, lpString, 200);
            var text = Marshal.PtrToStringAnsi(lpString);
            if (text == "重新载入应用") {
                Console.WriteLine("Detected");
                if (hWnd != IntPtr.Zero)
                {
                    System.Threading.Thread.Sleep(10000);
                    SendMessage(hWnd, BM_CLICK, 0, 0);
                }
            }
            if (!string.IsNullOrWhiteSpace(text))
                HandleList.Add(text);
            return true;
        }

        public static void SearchAndClick() {
            IntPtr ParenthWnd = new IntPtr(0);
            ParenthWnd = FindWindow(null, "酷Q Pro 5.15.9");
            if (ParenthWnd != IntPtr.Zero)
            {
                Console.WriteLine("找到窗口");
                HandleList.Clear();
                EnumChildWindows(ParenthWnd, EnumWindowsMethod, IntPtr.Zero);
            }
            else
            {
                Console.WriteLine("没有找到窗口");
            }
        }
        static void Main(string[] args)
        {
            while (true) {
                System.Threading.Thread.Sleep(2000);
                SearchAndClick();
            }
        }
        private static void UseEventHook() {
            using (var eventHookFactory = new EventHook.EventHookFactory())
            {
                var WindowWatcher = eventHookFactory.GetApplicationWatcher();
                WindowWatcher.Start();
                WindowWatcher.OnApplicationWindowChange += (s, e) =>
                {
                    Console.WriteLine(
                        string.Format(
                            "Application window of '{0}' with the title '{1}' was {2}",
                            e.ApplicationData.AppName,
                            e.ApplicationData.AppTitle,
                            e.Event
                            )
                        );
                };
                Console.Read();
                WindowWatcher.Stop();
            }
        }
        private static void TypicalWinDetect() {
            System.Windows.Automation.Automation.AddAutomationEventHandler(
                    eventId: WindowPattern.WindowOpenedEvent,
                    element: AutomationElement.RootElement,
                    scope: TreeScope.Children,
                    eventHandler: OnWindowOpened
                    );

            Console.ReadLine();
            Automation.RemoveAllEventHandlers();
        }
        private static void OnWindowOpened(object sender, AutomationEventArgs automationEventArgs)
        {
            try
            {
                var element = sender as AutomationElement;
                if (element != null)
                    Console.WriteLine("New Window opened: {0}", element.Current.ClassName);
            }
            catch (ElementNotAvailableException)
            {
            }
        }
    }
}
