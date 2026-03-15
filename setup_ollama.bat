@echo off
echo Setting up Ollama for AI-GitHub Dashboard...

where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Ollama is not installed or not in PATH.
    echo Please install Ollama from https://ollama.com/
    pause
    exit /b
)

echo Pulling Llama 3.1 model...
ollama pull llama3.1

echo Pulling Mistral model...
ollama pull mistral

echo Pulling Llama 3.2 1B (Lightweight)...
ollama pull llama3.2:1b

echo models pulled successfully!
echo You can now start the dashboard.
pause
