import sys
from idlcommon import getDllMethodExternalName

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".cs"
classsuffix = "_CDll0"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0
currentModule = 0

def shouldBeMarshalled(typename):
    return (typename == 'string')

def getMarshalAs(typename):
    if (typename == 'string'):
        return "MarshalAs(UnmanagedType.LPWStr)"
    else:
        return ""

def getArgMarshalType(typename):
    if shouldBeMarshalled(typename):
        return '[%s] %s' % (getMarshalAs(typename), typename)
    else:
        return typename

def printImplementation(interface):
    outfile.write('    public class %sExports\n' % (interface.name))
    outfile.write('    {\n')

    outfile.write('        [DllExport(CallingConvention = CallingConvention.StdCall)]\n')
    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('        public static void %s(' % (getDllMethodExternalName(interface, m)))
        else:
            if shouldBeMarshalled(m.returns.name):
                outfile.write("        [return: %s]\n" % getMarshalAs(m.returns.name))
            outfile.write('        public static %s %s(' % (m.returns.name, getDllMethodExternalName(interface, m)))

        outfile.write(')\n')

    outfile.write('        {\n')
    outfile.write('            // call real implementation\n')
    outfile.write('        }\n')

    outfile.write('    }\n')

def printStruct(struct):
    outfile.write('    public struct %s\n' % struct.name)
    outfile.write('    {\n')
    for m in struct.members:
        outfile.write('        %s %s;\n' % (m.type.name, m.name))
    outfile.write('    }\n\n')

def printTypeDef(typedef):
    outfile.write('    using %s = %s;\n\n' % (typedef.name, typedef.type.name))

def printEnum(enum):
    outfile.write('    public enum %s = (\n' % enum.name)
    first = 1
    for v in enum.values:
        if not first:
            outfile.write(',\n')
        else:
            first = 0
        outfile.write('    %s = %s' % (v.name, v.value))
    outfile.write('\n    );\n\n')

def printMod(module):
    global outfile, currentModule
    currentModule = module
    outfile = open(module.name + "_cdll" + outextension, "w")

    outfile.write('using System;\n')
    outfile.write('using System.Runtime.InteropServices;\n\n')

    outfile.write('namespace %s\n' % (module.name))
    outfile.write('{\n')

    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)

    module.for_each_interface(printImplementation)

    outfile.write('}\n')

    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
