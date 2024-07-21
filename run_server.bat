@echo off
:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
setlocal DisableDelayedExpansion
set "batchPath=%~f0"
setlocal EnableDelayedExpansion
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%temp%\OEgetPrivileges.vbs"
ECHO UAC.ShellExecute "%batchPath%", "", "", "runas", 1 >> "%temp%\OEgetPrivileges.vbs"
"%temp%\OEgetPrivileges.vbs"
del "%temp%\OEgetPrivileges.vbs"
exit /B

:gotPrivileges
REM Execute your command here
set "scriptDir=%~dp0"
start "" /B "%scriptDir%\dist\server.exe"
