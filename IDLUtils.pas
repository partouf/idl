unit IDLUtils;

interface

uses
  SysUtils;

type
  sequence<T> = Array of T;
  long = Int64;

  TCString = record
  public
    Len: Int64;
    Data: Pointer;
    Codepage: Int32;
    OwnedByDelphi: Boolean;
  end;

  cstring = ^TCString;

  EDLLLoadError = class(Exception);
  EDLLMethodMissing = class(Exception);

  TIDLUtils = class
  public
    class function DelphiTypeToCType(const Value: unicodestring): cstring; overload;
    class function CTypeToDelphiType(const Value: cstring): unicodestring; overload;
  end;

implementation

uses
  Windows;

class function TIDLUtils.DelphiTypeToCType(const Value: unicodestring): cstring;
var
  StrLength: Integer;
begin
  StrLength := Length(Value) * sizeof(Char);

  Result := cstring(GetMemory(sizeof(TCString)));
  Result.Len := StrLength;
  Result.Data := GetMemory(StrLength);
  Result.Codepage := 1200;  // UTF-16LE
  Result.OwnedByDelphi := True;

  Move(Value[1], Result.Data, Result.Len);
end;

class function TIDLUtils.CTypeToDelphiType(const Value: cstring): unicodestring;
var
  flags: Integer;
  StrLength: Integer;
begin
  if Value.Codepage = 0 then
  begin
    SetLength(Result, Value.Len);
    Move(Value.Data, Result[1], Value.Len);
  end
  else if Value.Codepage = 1200 then
  begin
    SetLength(Result, Value.Len);
    Move(Value.Data, Result[1], Value.Len);
  end
  else
  begin
    flags := WC_COMPOSITECHECK or WC_DISCARDNS or WC_SEPCHARS or WC_DEFAULTCHAR;
    StrLength := MultiByteToWideChar(Value.Codepage, flags, Value.Data, -1, nil, 0);
    SetLength(Result, StrLength);
    MultiByteToWideChar(Value.Codepage, flags, Value.Data, Value.Len, @Result[1], StrLength);
  end;

  if Value.OwnedByDelphi then
  begin
    FreeMemory(Value.Data);
    FreeMemory(Value);
  end;
end;

end.
