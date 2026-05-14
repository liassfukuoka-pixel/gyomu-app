@echo off
cd C:\Users\liass\Desktop\gyomu_app
call venv\Scripts\activate
start "gyomu-app" cmd /k "python app.py"
timeout /t 3 /nobreak
start "ngrok" cmd /k "ngrok http 5000 --domain=clone-chosen-squeegee.ngrok-free.dev"
pause