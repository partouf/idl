using System.Runtime.InteropServices;
using IDLInterop;

namespace TestModule
{
    class TestModuleSetup
    {

        [DllExport(CallingConvention = CallingConvention.Cdecl)]
        public static void TestModule_Load()
        {
            InteropContainer.RegisterType<ICommunicator, Communicator>();
        }
    }
}
