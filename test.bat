@echo off
chcp 65001 >nul
echo ========================================
echo    DIAGNOSTIKA
echo ========================================
echo.

echo [1] Python bor-yo'qligi:
python --version
echo ErrorLevel: %errorlevel%
echo.

echo [2] Python yo'li:
where python
echo.

echo [3] venv mavjudligi:
if exist "venv" (
    echo venv/ papka BOR
) else (
    echo venv/ papka YO'Q
)
echo.

echo [4] requirements.txt mavjudligi:
if exist "requirements.txt" (
    echo requirements.txt BOR
) else (
    echo requirements.txt YO'Q
)
echo.

echo [5] manage.py mavjudligi:
if exist "manage.py" (
    echo manage.py BOR
) else (
    echo manage.py YO'Q
)
echo.

echo ========================================
echo    Tugadi!
echo ========================================
pause
