@echo off
REM Launch the slice. Double-click this file.
REM
REM There is no standalone .exe: this is a Godot project, so the editor
REM binary runs it straight from godot/project.godot. The path below is
REM relative to THIS file, so moving the whole 7270 folder is fine; moving
REM this repository out from beside the Godot download is not.
setlocal
set "GODOT=%~dp0..\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe"
if not exist "%GODOT%" (
  echo Could not find Godot at:
  echo   %GODOT%
  echo Edit the GODOT line in this file to point at your Godot executable.
  pause
  exit /b 1
)
start "" "%GODOT%" --path "%~dp0godot"
