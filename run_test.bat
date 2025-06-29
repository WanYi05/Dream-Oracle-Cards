@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python -c "from linebot.v3 import Configuration; print(Configuration)"
pause