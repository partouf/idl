import sys

if len(sys.argv) > 1:
    idlfilepath = sys.argv[1]
else:
    print("Please supply .idl filepath")
    exit(1)

outextension = ".cpp"

from idl_parser import parser
parser_ = parser.IDLParser()

idlfile = open(idlfilepath, "r")
idl_str = idlfile.read()
idlfile.close()

outfile = 0

def printInterface(interface):
    outfile.write('  __declspec(dllexport) %s *__stdcall %s_new()\n' % (interface.name, interface.name))
    outfile.write('  {\n')
    outfile.write('    return new %s_impl();\n' % (interface.name))
    outfile.write('  };\n\n')

    outfile.write('  __declspec(dllexport) void __stdcall %s_delete(%s *instance)\n' % (interface.name, interface.name))
    outfile.write('  {\n')
    outfile.write('    delete instance;\n')
    outfile.write('  };\n\n')

    for m in interface.methods:
        outfile.write('  __declspec(dllexport) char *__stdcall %s_%s(%s *instance' % (interface.name, m.name, interface.name))

        params = ""
        for a in m.arguments:
            if not ('out' in a.direction):
                outfile.write(", ")

                if params == "":
                    params = a.name
                else:
                    params = params + ", " + a.name

                outfile.write('const char *%s' % (a.name))

        outfile.write(')\n')
        outfile.write('  {\n')
        #outfile.write('    instance->%s(%s);\n' % (m.name, params))
        outfile.write('    return nullptr;\n')
        outfile.write('  };\n')
    outfile.write('\n')

def printMod(module):
    global outfile
    outfile = open(module.name + "_cdll2_impl" + outextension, "w")
    outfile.write('#pragma once\n\n')
    outfile.write('#include "%s.h"\n' % module.name)
    outfile.write('#include "%s_cdll2.h"\n' % module.name)
    outfile.write('#include "IDLUtils.h"\n\n')
    outfile.write('using namespace std;\n')
    outfile.write('using namespace %s;\n\n' % module.name)
    outfile.write('extern "C" {\n')
    module.for_each_interface(printInterface)
    outfile.write('};\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
