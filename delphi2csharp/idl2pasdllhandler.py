import sys
from idlcommon import getDllMethodExternalName
from idlcommon import getDllMethodExternalNameByName

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".pas"
classsuffix = "_DLLHandler"
unitsuffix = "_DLLHandler"
varnameDLLHandle = "_DLLHandle"
callingConvention = "cdecl"

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

def getDLLHandleVarname(module):
    return '%s%s' % (varnameDLLHandle, module.name)

def getDllMethodVariableNameByName(interface, name):
    return "_%s_%s" % (interface.name, name)

def getDllMethodVariableName(interface, m):
    return getDllMethodVariableNameByName(interface, m.name)

def getDllMethodVariableDefinitionNameByName(interface, name):
    return 'TFunc%s%s' % (interface.name, name)

def getDllMethodVariableDefinitionName(interface, m):
    return getDllMethodVariableDefinitionNameByName(interface, m.name)

def writeDllVariableDecl(module):
    outfile.write('  %s: Cardinal;\n' % getDLLHandleVarname(module))

def writeMethodArgumentDecl(m):
    outfile.write('const ObjPtr: IntPtr')
    for a in m.arguments:
        outfile.write("; ")

        if 'out' in a.direction:
            outfile.write('var %s: %s' % (a.name, a.type.name))
        else:
            outfile.write('const %s: %s' % (a.name, a.type.name))

def writeDllMethodArgumentDecl(m):
    outfile.write('const ObjPtr: IntPtr')
    for a in m.arguments:
        outfile.write("; ")

        if 'out' in a.direction:
            outfile.write('var %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))
        else:
            outfile.write('const %s: %s' % (a.name, getDelphiTypeForCType(a.type.name)))

def writeDllMethodsDecl(interface):
    outfile.write('  %s = function: IntPtr; %s;\n' % (getDllMethodVariableDefinitionNameByName(interface, 'NewObject'), callingConvention))
    outfile.write('  %s = procedure(const ObjPtr: IntPtr); %s;\n' % (getDllMethodVariableDefinitionNameByName(interface, 'FreeObject'), callingConvention))

    for m in interface.methods:
        outfile.write('  %s = ' % (getDllMethodVariableDefinitionName(interface, m)))
        if m.returns.name == 'void':
            outfile.write('procedure(')
        else:
            outfile.write('function(')

        writeDllMethodArgumentDecl(m)

        if m.returns.name == 'void':
            outfile.write(');')
        else:
            outfile.write('): %s;' % (getDelphiTypeForCType(m.returns.name)))

        outfile.write(' %s;\n' % callingConvention)

def writeDllMethodVariables(interface):
    outfile.write('  %s: %s;\n' % (getDllMethodVariableNameByName(interface, 'NewObject'), getDllMethodVariableDefinitionNameByName(interface, 'NewObject')))
    outfile.write('  %s: %s;\n' % (getDllMethodVariableNameByName(interface, 'FreeObject'), getDllMethodVariableDefinitionNameByName(interface, 'FreeObject')))
    for m in interface.methods:
        outfile.write('  %s: %s;\n' % (getDllMethodVariableName(interface, m), getDllMethodVariableDefinitionName(interface, m)))

def printInterface(interface):
    outfile.write('  T%s%s = class\n' % (interface.name, classsuffix))
    outfile.write('  public\n')

    outfile.write('    class function NewObject: IntPtr;\n')
    outfile.write('    class procedure FreeObject(const ObjPtr: IntPtr);\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('    class procedure %s(' % m.name)
        else:
            outfile.write('    class function %s(' % m.name)

        writeMethodArgumentDecl(m)

        if m.returns.name == 'void':
            outfile.write(');\n')
        else:
            outfile.write('): %s;\n' % m.returns.name)

    outfile.write('  end;\n\n')

def writeDllLoading(module):
    outfile.write('  {$IFDEF MSWINDOWS}\n')
    outfile.write('  %s := LoadLibrary(\'%s.dll\');\n' % (getDLLHandleVarname(module), module.name))
    outfile.write('  if %s = 0 then raise EDLLLoadError.Create(\'DLL %s.dll could not be loaded\');\n' % (getDLLHandleVarname(module), module.name))
    outfile.write('  {$ELSE}\n')
    outfile.write('  %s := LoadLibrary(\'%s.so\');\n' % (getDLLHandleVarname(module), module.name))
    outfile.write('  if %s = 0 then raise EDLLLoadError.Create(\'DLL %s.so could not be loaded\');\n' % (getDLLHandleVarname(module), module.name))
    outfile.write('  {$ENDIF};\n\n')

def writeDllMethodLoading(module, interface):
    outfile.write('  %s := %s(GetProcAddress(%s, \'%s\'));\n' % (getDllMethodVariableNameByName(interface, 'NewObject'), getDllMethodVariableDefinitionNameByName(interface, 'NewObject'), getDLLHandleVarname(module), getDllMethodExternalNameByName(interface, 'NewObject')))
    outfile.write('  if not Assigned(%s) then raise EDLLMethodMissing.Create(\'Missing method %s in %s.dll\');\n\n' % (getDllMethodVariableNameByName(interface, 'NewObject'), getDllMethodExternalNameByName(interface, 'NewObject'), module.name))
    outfile.write('  %s := %s(GetProcAddress(%s, \'%s\'));\n' % (getDllMethodVariableNameByName(interface, 'FreeObject'), getDllMethodVariableDefinitionNameByName(interface, 'FreeObject'), getDLLHandleVarname(module), getDllMethodExternalNameByName(interface, 'FreeObject')))
    outfile.write('  if not Assigned(%s) then raise EDLLMethodMissing.Create(\'Missing method %s in %s.dll\');\n\n' % (getDllMethodVariableNameByName(interface, 'FreeObject'), getDllMethodExternalNameByName(interface, 'FreeObject'), module.name))
    
    for m in interface.methods:
        outfile.write('  %s := %s(GetProcAddress(%s, \'%s\'));\n' % (getDllMethodVariableName(interface, m), getDllMethodVariableDefinitionName(interface, m), getDLLHandleVarname(module), getDllMethodExternalName(interface, m)))
        outfile.write('  if not Assigned(%s) then raise EDLLMethodMissing.Create(\'Missing method %s in %s.dll\');\n\n' % (getDllMethodVariableName(interface, m), m.name, module.name))

def writeDllFree(module):
    outfile.write('  FreeLibrary(%s);\n' % getDLLHandleVarname(module))

def writeMethodCallArguments(m):
    outfile.write('ObjPtr')

    for a in m.arguments:
        outfile.write(", ")
        if needsProcessing(a.type.name) or ('out' in a.direction):
            outfile.write('_%s' % (a.name))
        else:
            outfile.write('%s' % (a.name))

def printImplementation(interface):
    outfile.write('class function T%s%s.NewObject: IntPtr;\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  Result := _%s();\n' % (getDllMethodExternalNameByName(interface, 'NewObject')))
    outfile.write('end;\n\n')

    outfile.write('class procedure T%s%s.FreeObject(const ObjPtr: IntPtr);\n' % (interface.name, classsuffix))
    outfile.write('begin\n')
    outfile.write('  _%s(ObjPtr);\n' % (getDllMethodExternalNameByName(interface, 'FreeObject')))
    outfile.write('end;\n\n')

    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('class procedure T%s%s.%s(' % (interface.name, classsuffix, m.name))
        else:
            outfile.write('class function T%s%s.%s(' % (interface.name, classsuffix, m.name))

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

        for a in m.arguments:
            if needsProcessing(a.type.name) or ('out' in a.direction):
                writePreprocessDelphiTypeToCType(a.name, a.type.name)

        outfile.write('\n')

        if m.returns.name == 'void':
            outfile.write('  %s(' % (getDllMethodVariableName(interface, m)))
        else:
            if needsProcessing(m.returns.name):
                outfile.write('  _Result := %s(' % (getDllMethodVariableName(interface, m)))
            else:
                outfile.write('  Result := %s(' % (getDllMethodVariableName(interface, m)))

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
    outfile.write('')

def printTypeDef(typedef):
    outfile.write('')

def printEnum(enum):
    outfile.write('')

def printDllMethodLoading(interface):
    writeDllMethodLoading(currentModule, interface)

def writeInitializeDLL(module):
    outfile.write('class procedure T%s.Load;\n' % (module.name))
    outfile.write('begin\n')
    outfile.write('  if %s <> 0 then Exit;\n\n' % (getDLLHandleVarname(module)))
    writeDllLoading(module)
    module.for_each_interface(printDllMethodLoading)
    outfile.write('end;\n')

def printDllMethodUnloading(interface):
    for m in interface.methods:
        outfile.write('  %s := nil;\n' % getDllMethodVariableName(interface, m))

def writeFinalizeDLL(module):
    dllHandleVarname = getDLLHandleVarname(module)
    outfile.write('class procedure T%s.Unload;\n' % (module.name))
    outfile.write('begin\n')
    outfile.write('  if %s = 0 then Exit;\n\n' % dllHandleVarname)
    module.for_each_interface(printDllMethodUnloading)
    outfile.write('  FreeLibrary(%s);\n' % dllHandleVarname)
    outfile.write('  %s := 0;\n' % dllHandleVarname)
    outfile.write('end;\n')

def writeModuleClass(module):
    outfile.write('  T%s = class\n' % (module.name))
    outfile.write('  public\n')
    outfile.write('    class procedure Load;\n')
    outfile.write('    class procedure Unload;\n')
    outfile.write('  end;\n\n')

def printMod(module):
    global outfile, currentModule
    currentModule = module
    outfile = open(module.name + unitsuffix + outextension, "w")
    outfile.write('unit %s%s;\n\n' % (module.name, unitsuffix))
    outfile.write('interface\n\n')
    outfile.write('uses\n')
    outfile.write('  Classes, IDLUtils;\n\n')
    outfile.write('type\n')
    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)
    module.for_each_interface(printInterface)

    writeModuleClass(module)

    outfile.write('implementation\n\n')

    outfile.write('uses\n')
    outfile.write('  {$IFDEF MSWINDOWS}\n')
    outfile.write('  Windows\n')
    outfile.write('  {$ELSE}\n')
    outfile.write('  dynlibs\n')
    outfile.write('  {$ENDIF};\n\n')

    outfile.write('type\n')
    module.for_each_interface(writeDllMethodsDecl)
    outfile.write('\n')

    outfile.write('var\n')
    writeDllVariableDecl(currentModule)
    module.for_each_interface(writeDllMethodVariables)
    outfile.write('\n')

    writeInitializeDLL(currentModule)
    outfile.write('\n')
    writeFinalizeDLL(currentModule)
    outfile.write('\n')

    module.for_each_interface(printImplementation)

    outfile.write('end.\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
