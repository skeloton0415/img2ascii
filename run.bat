@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Image to ASCII Art Converter...
python img2ascii.py
pause
