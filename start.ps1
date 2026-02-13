#!/usr/bin/env pwsh
# Home Server — установка и запуск для Windows
# При отсутствии Python/Node — предложение установить (yes/no) через winget.

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Blue }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "❌ $args" -ForegroundColor Red }

# --- Проверка зависимостей ---
function Test-Dependencies {
    $script:PYTHON = $null
    $script:missing = @()

    # Python 3.10+
    foreach ($py in @("python", "python3", "py")) {
        try {
            $ver = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($ver) {
                $major, $minor = $ver -split '\.'
                if ([int]$major -ge 3 -and [int]$minor -ge 10) {
                    $script:PYTHON = $py
                    break
                }
            }
        } catch {}
    }
    if (-not $script:PYTHON) { $script:missing += "Python 3.10+" }

    # Node.js 18+
    try {
        $nodeVersion = (node -v 2>$null) -replace '^v(\d+).*', '$1'
        if (-not $nodeVersion -or [int]$nodeVersion -lt 18) {
            if ($nodeVersion) { Write-Warning "Обнаружен Node.js v$nodeVersion, рекомендуется 18+" }
            $script:missing += "Node.js 18+"
        }
    } catch {
        $script:missing += "Node.js 18+"
    }

    # npm
    try {
        $null = Get-Command npm -ErrorAction Stop
    } catch {
        $script:missing += "npm"
    }

    return ($script:missing.Count -eq 0)
}

# --- Обработка флага --clean ---
if ($args -contains "--clean") {
    Write-Warning "Полная переустановка..."
    $venvDir = Join-Path $ROOT "server\venv"
    $nodeModules = Join-Path $ROOT "frontend\node_modules"
    $staticDir = Join-Path $ROOT "server\static"
    if (Test-Path $venvDir) { Remove-Item -Recurse -Force $venvDir }
    if (Test-Path $nodeModules) { Remove-Item -Recurse -Force $nodeModules }
    if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
    Write-Success "Очистка завершена."
}

# --- Проверка зависимостей и установка при необходимости ---
if (-not (Test-Dependencies)) {
    Write-Err "Отсутствуют зависимости: $($script:missing -join ', ')"
    $installScript = Join-Path $ROOT "scripts\install-deps.ps1"
    if (Test-Path $installScript) {
        & $installScript
        if ($LASTEXITCODE -ne 0) { exit 1 }
        Write-Host ""
        Write-Info "После установки перезапустите терминал и снова выполните: .\start.ps1"
        exit 0
    } else {
        Write-Host ""
        Write-Info "Установите вручную:"
        Write-Host "  Python:  winget install -e --id Python.Python.3.11"
        Write-Host "  Node.js: winget install -e --id OpenJS.NodeJS.LTS"
        Write-Host "  Или скачайте с https://python.org и https://nodejs.org"
        exit 1
    }
}

$PYTHON = $script:PYTHON

# --- Создание директорий ---
$dataDir = Join-Path $ROOT "server\data"
$logsDir = Join-Path $ROOT "server\logs"
$staticDir = Join-Path $ROOT "server\static"
foreach ($d in @($dataDir, $logsDir, $staticDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# --- Виртуальное окружение Python ---
$VENV_DIR = Join-Path $ROOT "server\venv"
if (-not (Test-Path $VENV_DIR)) {
    Write-Info "Создание виртуального окружения..."
    & $PYTHON -m venv $VENV_DIR
}
$ACTIVATE = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $ACTIVATE

# --- Обновление pip и установка зависимостей Python ---
Write-Info "Обновление pip..."
python -m pip install -q --upgrade pip
$reqPath = Join-Path $ROOT "server\requirements.txt"
if (Test-Path $reqPath) {
    Write-Info "Установка Python зависимостей..."
    pip install -q -r $reqPath
} else {
    Write-Warning "server\requirements.txt не найден"
}

# --- Фронтенд ---
Write-Info "Настройка фронтенда..."
Set-Location (Join-Path $ROOT "frontend")
if (Test-Path "package-lock.json") {
    npm ci --no-audit --no-fund
} else {
    npm install --no-audit --no-fund
}
Write-Info "Сборка фронтенда..."
npm run build
Set-Location $ROOT

# --- Копирование статики ---
Write-Info "Развертывание фронтенда..."
$BUILD_DIR = Join-Path $ROOT "frontend\build"
if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
Copy-Item -Recurse $BUILD_DIR $staticDir
Write-Success "Фронтенд скопирован в server\static"

# --- Загрузка .env ---
$envFiles = @(
    (Join-Path $ROOT ".env"),
    (Join-Path $ROOT "server\.env")
)
foreach ($ef in $envFiles) {
    if (Test-Path $ef) {
        Get-Content $ef | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim().Trim('"').Trim("'")
                Set-Item -Path "Env:$name" -Value $value
            }
        }
    }
}

# --- Запуск сервера ---
Write-Success "Все готово! Запуск сервера..."
Write-Host ""
Set-Location (Join-Path $ROOT "server")
$env:STATIC_DIR = $staticDir
python -m src
