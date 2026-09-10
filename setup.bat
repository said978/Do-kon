@echo off
cd /d "%~dp0"
echo ========================================
echo    DO'KON ERP — O'rnatish
echo ========================================
echo.
echo Papka: %CD%
echo.

echo Fayllar:
dir /b
echo.

echo [1] Python tekshirish...
python --version
if %errorlevel% neq 0 (
    echo XATO: Python topilmadi!
    pause
    exit /b 1
)
echo OK
echo.

echo [2] Virtual environment...
if not exist "venv" (
    python -m venv venv
)
echo OK
echo.

echo [3] Kutubxonalar o'rnatish...
call venv\Scripts\activate.bat
if not exist "requirements.txt" (
    echo.
    echo !!! XATO: requirements.txt topilmadi !!!
    echo Papkada quyidagilar bor:
    dir /b
    echo.
    pause
    exit /b 1
)
pip install -r requirements.txt
echo OK
echo.

echo [4] Migratsiya...
python manage.py migrate
echo OK
echo.

echo [5] Admin yaratish...
python manage.py createsuperuser
echo.

echo ========================================
echo    TUGADI! Serverni: start.bat
echo ========================================
pause
