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
    outfile.write('  class %s {\n' % (interface.name))
    for m in interface.methods:
        if m.returns.name == 'void':
            outfile.write('    virtual void %s(' % m.name)
        else:
            outfile.write('    virtual %s %s(' % (m.returns.name, m.name))

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

        outfile.write(') = 0;\n')

    outfile.write('  };\n\n')

def printStruct(struct):
    outfile.write('  struct %s {\n' % struct.name)
    for m in struct.members:
        outfile.write('    %s %s;\n' % (m.type.name, m.name))
    outfile.write('  };\n\n')

def printTypeDef(typedef):
    outfile.write('  typedef %s %s;\n\n' % (typedef.type.name, typedef.name))

def printEnum(enum):
    outfile.write('  enum class %s {\n' % enum.name)
    first = 1
    for v in enum.values:
        if not first:
            outfile.write(',\n')
        else:
            first = 0
        outfile.write('    %s = %s' % (v.name, v.value))
    outfile.write('\n  };\n\n')

def printMod(module):
    global outfile
    outfile = open(module.name + outextension, "w")
    outfile.write('#pragma once\n\n')
    outfile.write('#include "IDLUtils.h"\n\n')
    outfile.write('using namespace std;\n\n')
    outfile.write('namespace %s {\n' % module.name)
    module.for_each_typedef(printTypeDef)
    module.for_each_enum(printEnum)
    module.for_each_struct(printStruct)
    module.for_each_interface(printInterface)
    outfile.write('};\n')
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
