@echo off
setlocal
cd /d "%~dp0"

py -3.10 "%~dp0build_russian_patch.py" %*
set "BUILD_EXIT=%ERRORLEVEL%"

if not "%BUILD_EXIT%"=="0" (
    echo.
    echo Russian patch build failed. See the error above.
) else (
    echo.
    echo Russian patch build completed.
)

pause
exit /b %BUILD_EXIT%
