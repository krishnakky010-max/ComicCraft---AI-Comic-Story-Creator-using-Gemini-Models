@echo off
title ComicCraft - AI Comic Story Creator
cd /d "%~dp0"

echo =======================================================
echo          COMICCRAFT - AI COMIC STORY CREATOR
echo     Powered by Gemini AI (Flash ^& Pro) and Diffusers
echo =======================================================
echo.
echo Starting FastAPI Uvicorn Server...
echo Web UI will be live at:  http://127.0.0.1:8000
echo API Docs will be live at: http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
