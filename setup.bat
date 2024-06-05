@echo off

:: Check if venv directory exists, if not, create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    pause
) else (
    echo requirements.txt not found.
)

echo Setup complete.