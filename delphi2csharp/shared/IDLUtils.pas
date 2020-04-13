unit IDLUtils;

interface

uses
  SysUtils;

type
  sequence<T> = Array of T;
  long = Int64;

  EDLLLoadError = class(Exception);
  EDLLMethodMissing = class(Exception);

  EDLLBoundaryExternalException = class(Exception)
  protected
    FExternalClassname: string;
    FStackTrace: string;
  public
    property ExternalClassname: string
      read FExternalClassname write FExternalClassname;
    property StackTrace: string
      read FStackTrace write FStackTrace;

    constructor Create(const Msg: string; const InternalClass: string; const InternalStacktrace: string);
  end;

implementation

uses
  Windows;

{ EDLLBoundaryExternalException }

constructor EDLLBoundaryExternalException.Create(const Msg, InternalClass, InternalStacktrace: string);
begin
  inherited Create(Msg);
  FExternalClassname := InternalClass;
  FStacktrace := InternalStacktrace;
end;

end.
