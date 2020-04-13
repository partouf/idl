import sys
from idlcommon import getDllMethodExternalName
from idlcommon import getDllMethodExternalNameByName
from idlcommon import getDllExceptionMethodExternalName

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".cs"
classsuffix = "_CDll0"
callingConvention = "Cdecl"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0
currentModule = 0

def shouldBeMarshalled(typename):
    return (typename == 'string')

def getTypeTranslation(typename):
    if typename == 'integer':
        return "int"
    elif typename == 'boolean':
        return 'bool'
    else:
        return typename

def getMarshalAs(typename):
    if (typename == 'string'):
        return "MarshalAs(UnmanagedType.LPWStr)"
    else:
        return ""

def getArgMarshalType(typename):
    if shouldBeMarshalled(typename):
        return '[%s] %s' % (getMarshalAs(typename), getTypeTranslation(typename))
    else:
        return getTypeTranslation(typename)

def writeArguments(m):
    for a in m.arguments:
        outfile.write(', ')
        if 'out' in a.direction:
            outfile.write('out ')
        outfile.write('%s %s' % (getArgMarshalType(a.type.name), a.name))

def writeArgumentPassing(m):
    firstArg = 1
    for a in m.arguments:
        if firstArg:
            firstArg = 0
        else:
            outfile.write(', ')

        outfile.write('%s' % (a.name))

def writeNew(interface):
    outfile.write('        [DllExport(CallingConvention = CallingConvention.%s)]\n' % callingConvention)
    outfile.write('        public static int %s()\n' % (getDllMethodExternalNameByName(interface, 'NewObject')))
    outfile.write('        {\n')
    outfile.write('            return %s.New%s();\n' % (currentModule.name, interface.name))
    outfile.write('        }\n\n')

def writeFree(interface):
    outfile.write('        [DllExport(CallingConvention = CallingConvention.%s)]\n' % callingConvention)
    outfile.write('        public static void %s(int ObjPtr)\n' % (getDllMethodExternalNameByName(interface, 'FreeObject')))
    outfile.write('        {\n')
    outfile.write('            %s.Free%s(ObjPtr);\n' % (currentModule.name, interface.name))
    outfile.write('        }\n\n')

def writeDLLBoundaryExceptionMethods(module):
    outfile.write('    public static class DLLBoundaryHelper\n')
    outfile.write('    {\n')
    outfile.write('        private static string exceptionClass;\n')
    outfile.write('        private static string exceptionMessage;\n')
    outfile.write('        private static string exceptionStacktrace;\n')
    outfile.write('\n')
    outfile.write('        [DllExport(CallingConvention = CallingConvention.Cdecl)]\n')
    outfile.write('        [return: MarshalAs(UnmanagedType.LPWStr)]\n')
    outfile.write('        public static string %s()\n' % (getDllExceptionMethodExternalName(module, 'Class')))
    outfile.write('        {\n')
    outfile.write('            return exceptionClass;\n')
    outfile.write('        }\n')
    outfile.write('\n')
    outfile.write('        [DllExport(CallingConvention = CallingConvention.Cdecl)]\n')
    outfile.write('        [return: MarshalAs(UnmanagedType.LPWStr)]\n')
    outfile.write('        public static string %s()\n' % (getDllExceptionMethodExternalName(module, 'Message')))
    outfile.write('        {\n')
    outfile.write('            return exceptionMessage;\n')
    outfile.write('        }\n')
    outfile.write('\n')
    outfile.write('        [DllExport(CallingConvention = CallingConvention.Cdecl)]\n')
    outfile.write('        [return: MarshalAs(UnmanagedType.LPWStr)]\n')
    outfile.write('        public static string %s()\n' % (getDllExceptionMethodExternalName(module, 'Stacktrace')))
    outfile.write('        {\n')
    outfile.write('            return exceptionStacktrace;\n')
    outfile.write('        }\n')
    outfile.write('\n')
    outfile.write('        public static void SetException(Exception e)\n')
    outfile.write('        {\n')
    outfile.write('            exceptionClass = e.GetType().Name;\n')
    outfile.write('            exceptionMessage = e.Message;\n')
    outfile.write('            exceptionStacktrace = e.StackTrace.ToString();\n')
    outfile.write('        }\n')
    outfile.write('    }\n')
    outfile.write('\n')

def printImplementation(interface):
    outfile.write('    public static class %sExports\n' % (interface.name))
    outfile.write('    {\n')

    writeNew(interface)
    writeFree(interface)

    for m in interface.methods:
        outfile.write('        [DllExport(CallingConvention = CallingConvention.%s)]\n' % callingConvention)
        if m.returns.name == 'void':
            outfile.write('        public static void %s(int ObjPtr' % (getDllMethodExternalName(interface, m)))
        else:
            if shouldBeMarshalled(m.returns.name):
                outfile.write("        [return: %s]\n" % getMarshalAs(m.returns.name))
            outfile.write('        public static %s %s(int ObjPtr' % (getTypeTranslation(m.returns.name), getDllMethodExternalName(interface, m)))

        writeArguments(m)

        outfile.write(')\n')

        outfile.write('        {\n')
        outfile.write('            try\n')
        outfile.write('            {\n')

        outfile.write('                var obj = %s.Get%s(ObjPtr);\n' % (currentModule.name, interface.name))

        if m.returns.name == 'void':
            outfile.write('                obj.%s(' % (m.name))
        else:
            outfile.write('                return obj.%s(' % (m.name))
        writeArgumentPassing(m)
        outfile.write(');\n')

        outfile.write('            } catch(Exception e) {\n')
        outfile.write('                DLLBoundaryHelper.SetException(e);\n')
        outfile.write('                throw e;\n')
        outfile.write('            }\n')
        outfile.write('        }\n\n')

    outfile.write('    }\n')

def printMod(module):
    global outfile, currentModule
    currentModule = module
    outfile = open(module.name + "Exports" + outextension, "w")

    outfile.write('namespace %s\n' % (module.name))
    outfile.write('{\n')
    outfile.write('    using System;\n')
    outfile.write('    using System.Runtime.InteropServices;\n\n')

    writeDLLBoundaryExceptionMethods(module)

    module.for_each_interface(printImplementation)

    outfile.write('}\n')

    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
