import sys

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".h"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0

def printInterface(interface):
    outfile.write('  __declspec(dllexport) %s *__stdcall %s_new();\n' % (interface.name, interface.name))
    outfile.write('  __declspec(dllexport) void __stdcall %s_delete(const %s *instance);\n\n' % (interface.name, interface.name))
    for m in interface.methods:
        outfile.write('  __declspec(dllexport) %s __stdcall %s_%s(const %s *instance' % (m.returns.name, interface.name, m.name, interface.name))

        for a in m.arguments:
            outfile.write(", ")

            if 'out' in a.direction:
                outfile.write('%s *%s' % (a.type, a.name))
            else:
                outfile.write('const %s %s' % (a.type, a.name))

        outfile.write(');\n')
    outfile.write('\n')

def printMod(module):
    global outfile
    outfile = open(module.name + "_cdll1" + outextension, "w")
    outfile.write('#pragma once\n\n')
    outfile.write('#include "%s.h"\n' % module.name)
    outfile.write('#include "%s_impl.h"\n' % module.name)
    outfile.write('#include "IDLUtils.h"\n\n')
    outfile.write('using namespace std;\n')
    outfile.write('using namespace %s;\n\n' % module.name)
    outfile.write('extern "C" {\n')
    module.for_each_interface(printInterface)
    outfile.write('};\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
