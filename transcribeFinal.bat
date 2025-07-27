@echo off

REM Activate the virtual environment
pushd "F:\Python scripts\Transcribe anything"
call virtualEnv\Scripts\activate.bat

REM Change directory to where enhanced_transcribe_gui_fixed.py is located
cd /d "F:\Python scripts\transcripeGui"

REM Run the enhanced GUI script with Python
python enhanced_transcribe_gui_playlist_fixed.py

REM Keep the window open if there's an error
pause
