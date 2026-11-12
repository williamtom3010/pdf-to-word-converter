
@echo off
title PDF to Word Converter

:: Get the directory where this BAT file is located
set "ROOT_DIR=%~dp0"

:: Define application directory
set "APP_DIR=%ROOT_DIR%code_files"

:: Define virtual environment paths
set "VENV_DIR=%APP_DIR%\venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

echo ==========================================
echo       PDF TO WORD CONVERTER
echo ==========================================
echo.

:: Check whether code_files directory exists
if not exist "%APP_DIR%\app.py" (
    echo ERROR: app.py not found inside code_files.
    pause
    exit /b 1
)

:: Check whether Python is installed
where py >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

:: Create virtual environment if it doesn't exist
if not exist "%PYTHON_EXE%" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Display Python version
echo Using Python version:
"%PYTHON_EXE%" --version

:: Check and install dependencies
"%PYTHON_EXE%" -c "import streamlit, pdf2docx" >nul 2>&1

if errorlevel 1 (
    echo.
    echo Installing dependencies...
    "%PYTHON_EXE%" -m pip install -r "%APP_DIR%\requirements.txt"

    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
)

echo.
echo Starting PDF to Word Converter...
echo.

:: Start Streamlit server
start "PDF to Word Server" cmd /k ""%PYTHON_EXE%" -m streamlit run "%APP_DIR%\app.py" --server.headless true --server.port 8501"

:: Wait for Streamlit to initialize
timeout /t 4 /nobreak >nul

:: Open application in browser
start "" "http://localhost:8501"

exit
