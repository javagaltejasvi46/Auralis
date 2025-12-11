#!/bin/bash

echo "========================================"
echo "   AURALIS - Medical Voice Transcription"
echo "========================================"
echo

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

echo "Starting Auralis Backend..."
echo

cd backend
python3 startup.py