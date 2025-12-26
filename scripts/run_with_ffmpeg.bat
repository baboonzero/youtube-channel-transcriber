@echo off
REM Add ffmpeg from imageio-ffmpeg to PATH
set PATH=C:\Users\anshu\AppData\Roaming\Python\Python313\site-packages\imageio_ffmpeg\binaries;%PATH%

REM Run the transcriber
python run_transcriber.py
