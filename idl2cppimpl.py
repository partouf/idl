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
    for m in interface.methods:
        outfile.write('%s %s::%s(' % (m.returns.name, interface.name, m.name))

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

        outfile.write(')\n{\n}\n\n')

def printMod(module):
    global outfile
    outfile = open(module.name + outextension, "w")
    outfile.write('#include "%s.h"\n\n' % (module.name))
    outfile.write('using namespace std;\n')
    outfile.write('using namespace %s;\n\n' % (module.name))
    module.for_each_interface(printInterface)
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
