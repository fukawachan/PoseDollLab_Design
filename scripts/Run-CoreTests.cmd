@echo off
setlocal
set "PD_REPO=%~dp0.."
set "PD_VCVARS=%~1"
if not defined PD_VCVARS set "PD_VCVARS=D:\ProgramFiles\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%PD_VCVARS%" (echo Visual Studio C toolchain not found. Pass the vcvars64.bat path. & exit /b 1)
call "%PD_VCVARS%" >nul
if errorlevel 1 exit /b 1
cd /d "%PD_REPO%"
if not exist .local\core mkdir .local\core
cl /nologo /std:c11 /W4 /WX /I Firmware\PoseDollFullBody\main Firmware\PoseDollFullBody\main\pd41_core.c Firmware\PoseDollFullBody\tests\core_test.c /Fo:.local\core\ /Fe:.local\core\core_test.exe
if errorlevel 1 exit /b 1
.local\core\core_test.exe .local\core\golden_pd41.bin
exit /b %errorlevel%
