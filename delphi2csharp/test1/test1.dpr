program test1;

{$APPTYPE CONSOLE}

uses
  IDLUtils in '..\shared\IDLUtils.pas',
  TestModule_DLLHandler,
  TestModuleIntf,
  TestModule;

var
  Obj: ICommunicator;

begin
  TTestModule.Load;

  Obj := TCommunicator.Create;
  Obj.SetID(42);

  if Obj.GetID = 42 then
  begin
    WriteLn('Ok');
    ExitCode := 0;
  end
  else
  begin
    WriteLn('Error');
    ExitCode := 1;
  end;

//  TTestModule.Unload;
end.
