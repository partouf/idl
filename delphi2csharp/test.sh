#!/bin/sh

cd test1

python ../idl2pasintf.py test1.idl
python ../idl2pasdllhandler.py test1.idl
python ../idl2pasimpl2cdll.py test1.idl

python ../idl2csintf.py test1.idl
python ../idl2csharpdllexport.py test1.idl

cd ..
