@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 iniciar_local.py %*
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Instala Python 3.11 o superior desde https://www.python.org/downloads/
        echo Marca la opcion Add Python to PATH y vuelve a abrir este archivo.
        pause
        exit /b 1
    )
    python iniciar_local.py %*
)
if errorlevel 1 (
    echo.
    echo No se pudo iniciar. Revisa el mensaje anterior.
    pause
)
endlocal
