#!/usr/bin/env pwsh
# Home Server — установка и запуск для Windows

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️ $args" -ForegroundColor Blue }
function Write-Warning { Write-Host "⚠️ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }

# Проверка Python
$PYTHON = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PYTHON = "python3"
} else {
    Write-Error "Python не найден. Установите Python 3.10+"
    exit 1
}

# Проверка Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js не найден. Установите Node.js 18+"
    exit 1
}

# Виртуальное окружение Python
$VENV_DIR = Join-Path $ROOT "server\venv"
if (-not (Test-Path $VENV_DIR)) {
    Write-Info "Создание виртуального окружения..."
    & $PYTHON -m venv $VENV_DIR
}

# Активация виртуального окружения
$ACTIVATE = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $ACTIVATE

# Установка Python зависимостей
Write-Info "Установка Python зависимостей..."
pip install -q -r "$ROOT\server\requirements.txt"

# Установка фронтенда
Write-Info "Установка фронтенда..."
Set-Location "$ROOT\frontend"
npm ci --no-audit --no-fund
npm run build

# Копирование статики
Write-Info "Копирование статики..."
$STATIC_DIR = "$ROOT\server\static"
if (Test-Path $STATIC_DIR) {
    Remove-Item -Recurse -Force $STATIC_DIR
}
Copy-Item -Recurse "$ROOT\frontend\build" $STATIC_DIR

# Запуск
Write-Success "Запуск сервера..."
Set-Location "$ROOT\server"
$env:STATIC_DIR = $STATIC_DIR
python -m src