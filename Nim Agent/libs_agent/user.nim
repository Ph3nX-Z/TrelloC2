import winim/lean
import std/strformat
import os
import strutils
import system
import winim/inc/lm
import winim/clr
import winim/lean

proc GetUser():string =
    var
        buffer = newString(UNLEN + 1)
        cb = DWORD buffer.len
    GetUserNameA(&buffer, &cb)
    buffer.setLen(cb - 1)
    return buffer

proc getWinHostName(): string =
  let kind:COMPUTER_NAME_FORMAT = 1
  var size: DWORD = 0
  discard GetComputerNameExW(kind, nil, addr size)
  if size == 0: return ""
  var buf = newSeq[WCHAR](int(size) + 1)
  if GetComputerNameExW(kind, addr buf[0], addr size) != 0:
    result = $cast[WideCString](addr buf[0])