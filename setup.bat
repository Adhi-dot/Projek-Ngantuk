@echo off
setlocal enabledelayedexpansion

REM ============================================
REM MabaOps Setup Script (Windows)
REM Sets up venv, installs package, init data
REM ============================================

cd /d "%~dp0"

echo.
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.11+ dari python.org dulu.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   %%i

echo.
echo [2/4] Setting up virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo   .venv sudah ada, skip.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Gagal membuat virtual environment.
        pause
        exit /b 1
    )
    echo   .venv berhasil dibuat.
)

echo.
echo [3/4] Installing MabaOps...
.venv\Scripts\pip.exe install -e .[dev] --quiet
if errorlevel 1 (
    echo [ERROR] Gagal install package.
    pause
    exit /b 1
)
echo   MabaOps terinstall.

echo.
echo [4/4] Initializing data...
if exist "data\schedule.json" (
    echo   Data sudah ada, skip. Jalankan "mabaops init --demo" manual jika mau reset.
) else (
    .venv\Scripts\mabaops.exe init --demo
)

echo.
echo ============================================
echo   Setup selesai! Cara pakai:
echo.
echo   .venv\Scripts\mabaops.exe dashboard
echo   .venv\Scripts\mabaops.exe task add "Tugas" --due 2026-10-01
echo   .venv\Scripts\mabaops.exe --help
echo.
echo   Atau jalankan mabaops.bat dari mana saja
echo   (tambahkan folder ini ke PATH).
echo ============================================
pause
