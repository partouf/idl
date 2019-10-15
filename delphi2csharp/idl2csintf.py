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
    outfile.write('  interface I%s\n' % (interface.name))
    outfile.write('  {\n')
    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('    void %s(' % m.name)
        else:
            outfile.write('    %s %s(' % (translateType(m.returns.name), m.name))

        printFunctionArguments(m)

        outfile.write(');\n')

    outfile.write('  }\n')

def printStruct(struct):
    outfile.write('  %s = record\n' % struct.name)
    for m in struct.members:
        outfile.write('    %s: %s;\n' % (m.name, m.type.name))
    outfile.write('  end;\n\n')

def printTypeDef(typedef):
    outfile.write('  %s = %s;\n\n' % (typedef.name, typedef.type.name))

def printEnum(enum):
    outfile.write('  %s = (\n' % enum.name)
    first = 1
    for v in enum.values:
        if not first:
            outfile.write(',\n')
        else:
            first = 0
        outfile.write('    %s = %s' % (v.name, v.value))
    outfile.write('\n  );\n\n')

def printMod(module):
    global outfile
    outfile = open(targetfolder + "/" + module.name + unitsuffix + outextension, "w")
    outfile.write('namespace %s\n' % (module.name))
    outfile.write('{\n')
    outfile.write('  using System;\n\n')

    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)
    module.for_each_interface(printInterface)

    outfile.write('}\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
