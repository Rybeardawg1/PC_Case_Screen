Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.Run chr(34) & scriptDir & "\run_server.bat" & Chr(34), 0, False
Set WshShell = Nothing
