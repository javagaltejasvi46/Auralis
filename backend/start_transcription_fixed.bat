@echo off
echo Starting Transcription Server with OpenMP fix...
set KMP_DUPLICATE_LIB_OK=TRUE
python transcription_server.py
