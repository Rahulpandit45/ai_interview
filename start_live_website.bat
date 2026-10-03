@echo off
title AI Video Interview Assessment System - Live Custom Domain Launcher
echo ====================================================================
echo   Starting AI Video Interview Assessment System (Custom Domain Mode)
echo ====================================================================
echo.
echo 1. Launching Python Flask Backend on port 5000...
start "AI Interview Backend" cmd /k "python run.py"

echo 2. Launching Cloudflare Tunnel for your custom domain...
start "Cloudflare Custom Domain Tunnel" cmd /k "cloudflared tunnel run ai-interview"

echo.
echo ====================================================================
echo   Services are active!
echo   - Local Portal:   http://localhost:5000
echo   - Custom Domain:  https://interview.rahulkumarpandit.com.np
echo ====================================================================
pause
