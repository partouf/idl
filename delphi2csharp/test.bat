@echo off

cd test1

python ../idl2pasintf.py test1.idl
python ../idl2pasdllhandler.py test1.idl
python ../idl2pasimpl2cdll.py test1.idl

python ../idl2csintf.py test1.idl
python ../idl2csharpdllexport.py test1.idl

call "E:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars32.bat"
msbuild.exe TestModule/TestModule.sln /p:Configuration=Debug /p:Platform="Any CPU"

del *.exe
del *.dll
del *.xml
del *.pdb
dcc32 -Q -CC -B -NSSystem;WinAPI test1.dpr
echo ----
del *.dcu


copy TestModule\bin\Debug\*.dll .
copy TestModule\bin\Debug\*.xml .
copy TestModule\bin\Debug\*.pdb .

test1.exe

cd ..
