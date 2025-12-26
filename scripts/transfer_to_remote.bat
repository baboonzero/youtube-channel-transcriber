@echo off
REM Transfer files to remote GPU instance
REM Usage: transfer_to_remote.bat <remote-ip> <ssh-port>

if "%~1"=="" (
    echo Usage: transfer_to_remote.bat ^<remote-ip^> ^<ssh-port^>
    echo Example: transfer_to_remote.bat 123.45.67.89 12345
    exit /b 1
)

set REMOTE_IP=%1
set SSH_PORT=%2
set REMOTE_USER=root
set PROJECT_DIR=~/youtube-transcriber

echo ================================
echo Transferring to Remote GPU
echo ================================
echo Remote: %REMOTE_USER%@%REMOTE_IP%:%SSH_PORT%
echo.

REM Create remote directories
echo [1/5] Creating remote directories...
ssh -p %SSH_PORT% %REMOTE_USER%@%REMOTE_IP% "mkdir -p %PROJECT_DIR%/{data,config,src,scripts}"

REM Transfer source code
echo [2/5] Transferring source code...
scp -P %SSH_PORT% -r ..\src\*.py %REMOTE_USER%@%REMOTE_IP%:%PROJECT_DIR%/src/

REM Transfer config
echo [3/5] Transferring config...
scp -P %SSH_PORT% ..\config\config.py %REMOTE_USER%@%REMOTE_IP%:%PROJECT_DIR%/config/

REM Transfer scripts
echo [4/5] Transferring scripts...
scp -P %SSH_PORT% run_transcriber.py setup_remote_gpu.sh %REMOTE_USER%@%REMOTE_IP%:%PROJECT_DIR%/scripts/

REM Transfer database
echo [5/5] Transferring database...
scp -P %SSH_PORT% data\transcription_progress.db %REMOTE_USER%@%REMOTE_IP%:%PROJECT_DIR%/data/

echo.
echo ✅ Transfer complete!
echo.
echo Next: SSH into instance and run setup
echo   ssh -p %SSH_PORT% %REMOTE_USER%@%REMOTE_IP%
echo   cd ~/youtube-transcriber/scripts
echo   chmod +x setup_remote_gpu.sh
echo   ./setup_remote_gpu.sh
