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
    outfile.write('class %s_impl: public %s\n' % (interface.name, interface.name))
    outfile.write('{\n')
    outfile.write('public:\n')
    for m in interface.methods:
        outfile.write('  %s %s(' % (m.returns.name, m.name))

        firstarg = 1
        for a in m.arguments:
            if firstarg:
                firstarg = 0
            else:
                outfile.write(", ")

            if 'out' in a.direction:
                outfile.write('%s *%s' % (a.type, a.name))
            else:
                outfile.write('const %s %s' % (a.type, a.name))

        outfile.write(');\n')
    outfile.write('};\n\n')

def printMod(module):
    global outfile
    outfile = open(module.name + "_impl" + outextension, "w")
    outfile.write('#include "%s.h"\n\n' % (module.name))
    outfile.write('using namespace std;\n')
    outfile.write('using namespace %s;\n\n' % (module.name))
    module.for_each_interface(printInterface)
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
