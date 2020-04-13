import sys

targetfolder = "."

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
    if len(sys.argv) > 2:
        targetfolder = sys.argv[2]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".cs"
unitsuffix = "Intf"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0

def translateType(typename):
    if typename == 'integer':
        return 'int'
    elif typename == 'boolean':
        return 'bool'
    else:
        return typename

def printFunctionArguments(m):
    firstarg = 1
    for a in m.arguments:
        if firstarg:
            firstarg = 0
        else:
            outfile.write(", ")

        if 'out' in a.direction:
            outfile.write('out %s %s' % (translateType(a.type.name), a.name))
        else:
            outfile.write('%s %s' % (translateType(a.type.name), a.name))

def printInterface(interface):
    outfile.write('    public interface I%s\n' % (interface.name))
    outfile.write('    {\n')
    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('        void %s(' % m.name)
        else:
            outfile.write('        %s %s(' % (translateType(m.returns.name), m.name))

        printFunctionArguments(m)

        outfile.write(');\n')

    outfile.write('    }\n\n')

def printStruct(struct):
    outfile.write('    public struct %s\n' % struct.name)
    outfile.write('    {\n')
    for m in struct.members:
        outfile.write('    %s %s;\n' % (m.type.name, m.name))
    outfile.write('    }\n\n')

def printTypeDef(typedef):
    outfile.write('  %s = %s;\n\n' % (typedef.name, typedef.type.name))

def printEnum(enum):
    outfile.write('  public enum %s = (\n' % enum.name)
    first = 1
    for v in enum.values:
        if not first:
            outfile.write(',\n')
        else:
            first = 0
        outfile.write('    %s = %s' % (v.name, v.value))
    outfile.write('\n  );\n\n')

def writeListVars(interface):
    outfile.write('        private static IDictionary<int, I%s> _%sList;\n' % (interface.name, interface.name))

def writeListInit(interface):
    outfile.write('            _%sList = new Dictionary<int, I%s>();\n' % (interface.name, interface.name))

def writeObjGetters(interface):
    outfile.write('        public static I%s Get%s(int ptr)\n' % (interface.name, interface.name))
    outfile.write('        {\n')
    outfile.write('            return _%sList[ptr];\n' % (interface.name))
    outfile.write('        }\n\n')

def writeObjNewers(interface):
    outfile.write('        public static int New%s()\n' % (interface.name))
    outfile.write('        {\n')
    outfile.write('            var obj = InteropContainer.Resolve<I%s>();\n' % (interface.name))

    outfile.write('            int id = rand.Next(1, int.MaxValue - 1);\n')
    outfile.write('            while (_%sList.ContainsKey(id)) id = rand.Next(1, int.MaxValue - 1);\n' % (interface.name))

    outfile.write('            _%sList.Add(id, obj);\n' % (interface.name))

    outfile.write('            return id;\n')
    outfile.write('        }\n\n')

def writeObjFreeers(interface):
    outfile.write('        public static void Free%s(int ptr)\n' % (interface.name))
    outfile.write('        {\n')
    outfile.write('            if (!_%sList.ContainsKey(ptr)) return;\n' % (interface.name))
    outfile.write('            _%sList.Remove(ptr);\n' % (interface.name))
    outfile.write('        }\n\n')

def printMod(module):
    global outfile
    outfile = open(targetfolder + "/" + module.name + unitsuffix + outextension, "w")
    outfile.write('namespace %s\n' % (module.name))
    outfile.write('{\n')
    outfile.write('    using System;\n')
    outfile.write('    using System.Collections.Generic;\n')
    outfile.write('    using IDLInterop;\n\n')

    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)
    module.for_each_interface(printInterface)

    outfile.write('    public class %s\n' % (module.name))
    outfile.write('    {\n')
    outfile.write('        private static Random rand;\n')
    module.for_each_interface(writeListVars)

    outfile.write('\n')

    outfile.write('        static %s()\n' % (module.name))
    outfile.write('        {\n')
    outfile.write('            rand = new Random();\n')

    module.for_each_interface(writeListInit)

    outfile.write('        }\n\n')

    module.for_each_interface(writeObjGetters)

    module.for_each_interface(writeObjNewers)

    module.for_each_interface(writeObjFreeers)

    outfile.write('    }\n')

    outfile.write('}\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
