@echo off
echo Installing required Python packages...

:: Upgrade pip
python -m pip install --upgrade pip

:: Install required packages
pip install pyinstaller transformers torch tokenizers ollama mistral

echo All dependencies are installed.
pause
