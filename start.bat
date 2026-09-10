@echo off
cd /d "%~dp0"
echo ========================================
echo    DO'KON ERP — Server ishga tushirilmoqda
echo ========================================
echo.
echo Server manzili: http://127.0.0.1:8000
echo Tarmoq manzili: http://192.168.1.15:8000
echo.
echo Serverni to'xtatish uchun: Ctrl+C
echo ========================================
echo.

call venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
