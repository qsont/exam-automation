@echo off
taskkill /F /IM brave.exe /T 2>nul
timeout /t 2 /nobreak >nul
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" ^
    --remote-debugging-port=9222 ^
    --restore-last-session ^
    --profile-directory="Default"