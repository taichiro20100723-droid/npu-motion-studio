@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\make_waseda_saga_festival_mv.ps1"
endlocal
