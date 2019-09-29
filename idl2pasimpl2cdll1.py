import sys

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".pas"
classsuffix = "_CDll1"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0
currentModule = 0

def getDelphiTypeForCType(typename):
    if typename.lower() == "string":
        return 'cstring'
    return typename

def needsProcessing(typename):
    if typename.lower() == 'string':
        return 1
    return 0

def writeVarDelphiTypeToCType(varname, typename):
    outfile.write('  _%s: %s;\n' % (varname, getDelphiTypeForCType(typename)))

def writePreprocessDelphiTypeToCType(varname, typename):
    if needsProcessing(typename):
        outfile.write('  _%s := TIDLUtils.DelphiTypeToCType(%s);\n' % (varname, varname))
    else:
        outfile.write('  _%s := %s;\n' % (varname, varname))

def writePostprocessDelphiTypeToCType(varname, typename):
    if needsProcessing(typename):
        outfile.write('  %s := TIDLUtils.CTypeToDelphiType(_%s);\n' % (varname, varname))
    else:
        outfile.write('  %s := _%s;\n' % (varname, varname))

def printInterface(interface):
    for m in interface.methods:
        outfile.write('  TFunc%s%s = ' % (interface.name, m.name))
        if m.returns.name == 'void':
            outfile.write('procedure(')
        else:
            outfile.write('function(')

        firstarg = 1
        for a in m.arguments:
            if firstarg:
                firstarg = 0
            else:
                outfile.write(", ")

            if 'out' in a.direction:
                outfile.write('var %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))
            else:
                outfile.write('const %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))

        if m.returns.name == 'void':
            outfile.write(');')
        else:
            outfile.write('): %s;' % (getDelphiTypeForCType(m.returns.name)))

        outfile.write(' cdecl;\n')

    outfile.write('\n')
    outfile.write('  T%s%s = class(TInterfacedObject, %s)\n' % (interface.name, classsuffix, interface.name))
    outfile.write('  protected\n')
    outfile.write('    FDLLHandle: Cardinal;\n')

    for m in interface.methods:
        outfile.write('    F%s: TFunc%s%s;\n' % (m.name, interface.name, m.name))

    outfile.write('  public\n')
    outfile.write('    constructor Create;\n')
    outfile.write('    destructor Destroy; override;\n')
    outfile.write('\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('    procedure %s(' % m.name)
        else:
            outfile.write('    function %s(' % m.name)

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

        if m.returns.name == 'void':
            outfile.write(');\n')
        else:
            outfile.write('): %s;\n' % m.returns.name)

    outfile.write('  end;\n\n')

def printImplementation(interface):
    module = currentModule
    outfile.write('constructor T%s%s.Create;\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  inherited Create;\n\n')
    outfile.write('  FDLLHandle := LoadLibrary(\'%s.dll\');\n' % (module.name))
    outfile.write('  if FDLLHandle = 0 then raise EDLLLoadError.Create(\'DLL %s.dll could not be loaded\');\n\n' % (module.name))

    for m in interface.methods:
        outfile.write('  F%s := TFunc%s%s(GetProcAddress(FDLLHandle, \'%s\'));\n' % (m.name, interface.name, m.name, m.name))
        outfile.write('  if not Assigned(F%s) then raise EDLLMethodMissing.Create(\'Missing method %s in %s.dll\');\n\n' % (m.name, m.name, module.name))

    outfile.write('end;\n\n')

    outfile.write('destructor T%s%s.Destroy;\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  FreeLibrary(FDLLHandle);\n')
    outfile.write('end;\n\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('procedure T%s%s.%s(' % (interface.name, classsuffix, m.name))
        else:
            outfile.write('function T%s%s.%s(' % (interface.name, classsuffix, m.name))

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

    for a in m.arguments:
        if needsProcessing(a.type.name) or ('out' in a.direction):
            writePreprocessDelphiTypeToCType(a.name, a.type.name)

    outfile.write('\n')

    if m.returns.name == 'void':
        outfile.write('  F%s(' % (m.name))
    else:
        if needsProcessing(m.returns.name):
            outfile.write('  _Result := F%s(' % (m.name))
        else:
            outfile.write('  Result := F%s(' % (m.name))

    firstarg = 1
    for a in m.arguments:
        if firstarg:
            firstarg = 0
        else:
            outfile.write(", ")
        if needsProcessing(a.type.name) or ('out' in a.direction):
            outfile.write('_%s' % (a.name))
        else:
            outfile.write('%s' % (a.name))

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
    outfile = open(module.name + "_cdll" + outextension, "w")
    outfile.write('unit %s_cdll;\n\n' % module.name)
    outfile.write('interface\n\n')
    outfile.write('uses\n')
    outfile.write('  Classes, Windows, IDLUtils, %s;\n\n' % (module.name))
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
