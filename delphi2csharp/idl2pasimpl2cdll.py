import sys
from idlcommon import getDllMethodExternalName

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".pas"
classsuffix = ""
unitsuffix = ""
varnameDLLHandle = "_DLLHandle"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0
currentModule = 0

def getDelphiTypeForCType(typename):
    if typename.lower() == 'string':
        return 'PChar'
    return typename

def needsProcessing(typename):
    if typename.lower() == 'string':
        return 1
    return 0

def writeVarDelphiTypeToCType(varname, typename):
    outfile.write('  _%s: %s;\n' % (varname, getDelphiTypeForCType(typename)))

def writePreprocessDelphiTypeToCType(varname, typename):
    if needsProcessing(typename):
        outfile.write('  _%s := PChar(%s);\n' % (varname, varname))
    else:
        outfile.write('  _%s := %s;\n' % (varname, varname))

def writePostprocessDelphiTypeToCType(varname, typename):
    if needsProcessing(typename):
        outfile.write('  %s := _%s;\n' % (varname, varname))
    else:
        outfile.write('  %s := _%s;\n' % (varname, varname))

def writeMethodArgumentDecl(m):
    firstarg = 1
    for a in m.arguments:
        if firstarg:
            firstarg = 0
        else:
            outfile.write("; ")

        if 'out' in a.direction:
            outfile.write('var %s: %s' % (a.name, a.type.name))
        else:
            outfile.write('const %s: %s' % (a.name, a.type.name))

def writeDllMethodArgumentDecl(m):
    firstarg = 0
    for a in m.arguments:
        if firstarg:
            firstarg = 0
        else:
            outfile.write("; ")

        if 'out' in a.direction:
            outfile.write('var %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))
        else:
            outfile.write('const %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))

def printInterface(interface):
    outfile.write('  T%s%s = class(TInterfacedObject, I%s)\n' % (interface.name, classsuffix, interface.name))
    outfile.write('  private\n')
    outfile.write('    FObjPtr: IntPtr;\n')
    outfile.write('  public\n')

    outfile.write('    constructor Create;\n')
    outfile.write('    destructor Destroy; override;\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('    procedure %s(' % m.name)
        else:
            outfile.write('    function %s(' % m.name)

        writeMethodArgumentDecl(m)

        if m.returns.name == 'void':
            outfile.write(');\n')
        else:
            outfile.write('): %s;\n' % m.returns.name)

    outfile.write('  end;\n\n')

def writeMethodCallArguments(m):
    outfile.write('FObjPtr')
    for a in m.arguments:
        outfile.write(", ")
        if needsProcessing(a.type.name) or ('out' in a.direction):
            outfile.write('_%s' % (a.name))
        else:
            outfile.write('%s' % (a.name))

def printImplementation(interface):
    outfile.write('constructor T%s%s.Create;\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  FObjPtr := T%s_DLLHandler.%s();\n' % (interface.name, 'NewObject'))
    outfile.write('end;\n\n')

    outfile.write('destructor T%s%s.Destroy;\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  T%s_DLLHandler.%s(FObjPtr);\n' % (interface.name, 'FreeObject'))
    outfile.write('  FObjPtr := 0;\n')
    outfile.write('end;\n\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('procedure T%s%s.%s(' % (interface.name, classsuffix, m.name))
        else:
            outfile.write('function T%s%s.%s(' % (interface.name, classsuffix, m.name))

        writeMethodArgumentDecl(m)

        if m.returns.name == 'void':
            outfile.write(');\n')
        else:
            outfile.write('): %s;\n' % m.returns.name)

        firstarg = 1
        if needsProcessing(m.returns.name):
            firstarg = 0
            outfile.write("var\n")
            writeVarDelphiTypeToCType('Result', m.returns.name)

        for a in m.arguments:
            if needsProcessing(a.type.name) or ('out' in a.direction):
                if firstarg:
                    outfile.write("var\n")
                    firstarg = 0
                writeVarDelphiTypeToCType(a.name, a.type.name)

        outfile.write('begin\n')

        if m.returns.name == 'void':
            outfile.write('  T%s_DLLHandler.%s(' % (interface.name, m.name))
        else:
            outfile.write('  Result := T%s_DLLHandler.%s(' % (interface.name, m.name))

        writeMethodCallArguments(m)

        outfile.write(');\n')

        outfile.write('\n')

        if needsProcessing(m.returns.name):
            writePostprocessDelphiTypeToCType('Result', m.returns.name)

        for a in m.arguments:
            if ('out' in a.direction):
                writePostprocessDelphiTypeToCType(a.name, a.type.name)

        outfile.write('end;\n\n')

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
    global outfile, currentModule
    currentModule = module

    outfile = open(module.name + unitsuffix + outextension, "w")
    outfile.write('unit %s%s;\n\n' % (module.name, unitsuffix))
    outfile.write('interface\n\n')
    outfile.write('uses\n')
    outfile.write('  Classes, %s_DLLHandler, %s;\n\n' % (module.name, module.name + 'Intf'))
    outfile.write('type\n')
    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)
    module.for_each_interface(printInterface)

    outfile.write('implementation\n\n')

    module.for_each_interface(printImplementation)

    outfile.write('end.\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
