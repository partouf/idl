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

def printStruct(struct):
    outfile.write('string xmlSerialize(XMLDocument &doc, XMLNode &parent, const %s &object)\n' % struct.name)
    outfile.write('{\n')
    for m in struct.members:
        outfile.write('  AddElementToDoc(doc, parent, "%s", object.%s);\n' % (m.name, m.name))
    outfile.write('}\n\n')

def printMod(module):
    global outfile
    outfile = open(module.name + "_tinyxml" + outextension, "w")
    outfile.write('#pragma once\n\n')
    outfile.write('#include "IDLUtils.h"\n')
    outfile.write('#include "IDLTinyXML.h"\n')
    outfile.write('#include "%s_tinyxml.h"\n\n' % (module.name))
    outfile.write('using namespace std;\n')
    outfile.write('using namespace tinyxml2;\n')
    outfile.write('using namespace %s;\n\n' % (module.name))
    module.for_each_struct(printStruct)
    outfile.close()

global_module = parser_.load(idl_str)
global_module.for_each_module(printMod)
