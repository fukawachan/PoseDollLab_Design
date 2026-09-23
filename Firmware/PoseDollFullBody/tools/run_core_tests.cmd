@echo off
setlocal
cd /d "%~dp0.."
call "D:\ProgramFiles\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
if not exist build_host mkdir build_host
cl /nologo /std:c11 /W4 /WX /I main main\pd41_core.c tests\core_test.c /Fo:build_host\ /Fe:build_host\core_test.exe
if errorlevel 1 exit /b 1
build_host\core_test.exe build_host\golden_pd41.bin
exit /b %errorlevel%
