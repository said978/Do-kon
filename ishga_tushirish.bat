@echo off
title DUKON POS Kassa Tizimi
cd /d "%~dp0"

echo DUKON POS Tizimi ishga tushmoqda...
echo Iltimos, ushbu oynani yopmang!

:: Virtual muhitni faollashtirish
call venv\Scripts\activate.bat

:: Brauzerda Kassa sahifasini 2 soniyadan so'ng ochish
start timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000/api/sales/pos/

:: Django serverini yurgazish
python manage.py runserver 127.0.0.1:8000