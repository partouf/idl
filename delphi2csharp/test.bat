@echo off

pip install -r ../requirements.txt

cd test1

REM Generate Pascal interfaces
python ../idl2pasintf.py test1.idl
REM Generate Pascal DLL handler
python ../idl2pasdllhandler.py test1.idl
REM Generate Pascal implementation of interfaces to call DLL
python ../idl2pasimpl2cdll.py test1.idl

REM Generate C# interfaces
python ../idl2csintf.py test1.idl
REM Generate C# DLL export
python ../idl2csharpdllexport.py test1.idl

REM Build C# test project (DLL part)
call "E:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars32.bat"
msbuild.exe TestModule/TestModule.sln /p:Configuration=Debug /p:Platform="Any CPU"

REM Build Delphi test project (executable)
del *.exe
del *.dll
del *.xml
del *.pdb
dcc32 -Q -CC -B -NSSystem;WinAPI test1.dpr
echo ----
del *.dcu

REM Copy C# DLL and requirements to current directory
copy TestModule\bin\Debug\*.dll .
copy TestModule\bin\Debug\*.xml .
copy TestModule\bin\Debug\*.pdb .

REM Run test
test1.exe

cd ..
