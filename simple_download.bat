@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo      Starting SMART Download (Python)
echo ==========================================

:: 1. Check/Download yt-dlp
echo [1/3] Checking yt-dlp...
if not exist "yt-dlp.exe" (
    echo yt-dlp.exe not found. Downloading...
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -o yt-dlp.exe
)

:: 2. Check/Download FFmpeg
echo [2/3] Checking FFmpeg...
if not exist "ffmpeg.exe" (
    echo ffmpeg.exe not found. Downloading...
    curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip -o ffmpeg.zip
    powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath . -Force"
    copy "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" .
    copy "ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" .
    rmdir /s /q "ffmpeg-master-latest-win64-gpl"
    del ffmpeg.zip
)

    del ffmpeg.zip
)

:: 3. Check/Download Node.js
echo [3/4] Checking Node.js (Required for YouTube challenge)...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js not found. Auto-downloading portable version...
    
    :: Download Node.js LTS
    echo Downloading Node.js...
    curl -L https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip -o nodejs.zip
    
    echo Extracting Node.js...
    powershell -Command "Expand-Archive -Path nodejs.zip -DestinationPath . -Force"
    
    :: Rename generic folder to 'node_bin' to avoid long paths or version issues
    move node-v20.11.0-win-x64 node_bin
    
    :: Cleanup
    del nodejs.zip
    
    :: Add to temporary PATH for this session
    set "PATH=%~dp0node_bin;%PATH%"
    
    echo Node.js installed locally.
) else (
    echo Node.js found.
)

:: 4. Run Python Script
echo [4/4] Running Smart Download Logic...
echo.
python smart_download.py

pause
