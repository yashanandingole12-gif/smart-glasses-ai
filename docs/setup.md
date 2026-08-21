# Smart Glasses AI Assistant - Setup Guide

## 1. Setup Environment
Open PowerShell and run:
```powershell
cd smart-glasses-ai
.\scripts\setup_env.ps1
```

## 2. Configuration (`.env`)
Create or edit `.env`:
```env
LLM_PROVIDER=mock          # Options: "mock", "openai", "gemini", "anthropic", "ollama"
LLM_MODEL=gemini-2.0-flash # Or gpt-4o, claude-3-5-sonnet-20241022, etc.
LLM_API_KEY=               # Add your key if using real cloud LLM
DEFAULT_LOCATION_CITY=Nagpur
DEFAULT_LOCATION_COUNTRY=India
```

## 3. Running Backend
```powershell
.\scripts\run_backend.ps1
```

## 4. Running Simulator
```powershell
.\scripts\run_simulator.ps1
```
