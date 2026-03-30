$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️ $args" -ForegroundColor Blue }
function Write-Warning { Write-Host "⚠️ $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "❌ $args" -ForegroundColor Red }

# Проверка winget
function Test-Winget {
    try {
        $null = Get-Command winget -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Установка через winget
function Install-WithWinget {
    param([string]$PackageId, [string]$DisplayName)
    
    Write-Info "Installing $DisplayName via winget..."
    $result = winget install -e --id $PackageId --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$DisplayName installed"
        return $true
    } else {
        Write-Err "Failed to install $DisplayName via winget"
        return $false
    }
}

# Скачивание и установка через официальные сайты
function Install-Manual {
    param([string]$Component)
    
    Write-Warning "$Component not found"
    Write-Host ""
    Write-Info "Please install $Component manually:"
    
    switch ($Component) {
        "Python" {
            Write-Host "  Option 1: Download from https://www.python.org/downloads/"
            Write-Host "  Option 2: Install via Microsoft Store (search 'Python 3.12')"
        }
        "Node.js" {
            Write-Host "  Option 1: Download from https://nodejs.org/ (LTS version)"
            Write-Host "  Option 2: Install via Microsoft Store (search 'Node.js')"
        }
    }
    Write-Host ""
}

# Запрос на установку
function Confirm-Install {
    param([string]$Message)
    
    $response = Read-Host "$Message (y/n)"
    return ($response -eq 'y' -or $response -eq 'Y' -or $response -eq 'yes' -or $response -eq 'Yes')
}

# Обработка флага --clean
if ($args -contains "--clean") {
    Write-Warning "Full reinstall..."
    $venvDir = Join-Path $ROOT "server\.venv"
    $nodeModules = Join-Path $ROOT "frontend\node_modules"
    $staticDir = Join-Path $ROOT "server\static"
    if (Test-Path $venvDir) { Remove-Item -Recurse -Force $venvDir }
    if (Test-Path $nodeModules) { Remove-Item -Recurse -Force $nodeModules }
    if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
    Write-Success "Cleanup completed"
}

Write-Info "====================================="
Write-Info "   Home Server Setup for Windows"
Write-Info "====================================="
Write-Host ""

# Проверка Python
$PYTHON = $null
$pythonInstalled = $false
foreach ($py in @("python", "python3", "py")) {
    try {
        $ver = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($ver) {
            $major, $minor = $ver -split '\.'
            if ([int]$major -ge 3 -and [int]$minor -ge 10) {
                $PYTHON = $py
                $pythonInstalled = $true
                Write-Success "Python $major.$minor found"
                break
            }
        }
    } catch {}
}

# Проверка Node.js
$nodeInstalled = $false
try {
    $nodeVersion = (node -v 2>$null) -replace '^v(\d+).*', '$1'
    if ($nodeVersion) {
        if ([int]$nodeVersion -ge 18) {
            $nodeInstalled = $true
            Write-Success "Node.js v$nodeVersion found"
        } else {
            Write-Warning "Node.js v$nodeVersion found, but v18+ is required"
        }
    }
} catch {}

# Проверка npm
$npmInstalled = $false
try {
    $npmVersion = (npm -v 2>$null)
    if ($npmVersion) {
        $npmInstalled = $true
        Write-Success "npm v$npmVersion found"
    }
} catch {}

# Проверка наличия всех зависимостей
$allInstalled = $pythonInstalled -and $nodeInstalled -and $npmInstalled

if (-not $allInstalled) {
    Write-Host ""
    Write-Warning "Missing dependencies detected"
    Write-Host ""
    
    if (Test-Winget) {
        Write-Info "winget detected. Can install automatically."
        if (Confirm-Install "Install missing components using winget?") {
            $allSuccess = $true
            
            if (-not $pythonInstalled) {
                if (-not (Install-WithWinget -PackageId "Python.Python.3.12" -DisplayName "Python 3.12")) {
                    $allSuccess = $false
                    Install-Manual -Component "Python"
                }
            }
            
            if (-not $nodeInstalled) {
                if (-not (Install-WithWinget -PackageId "OpenJS.NodeJS.LTS" -DisplayName "Node.js LTS")) {
                    $allSuccess = $false
                    Install-Manual -Component "Node.js"
                }
            }
            
            if ($allSuccess) {
                Write-Success "All components installed via winget!"
                Write-Warning "Please close and reopen terminal, then run script again"
                exit 0
            }
        } else {
            if (-not $pythonInstalled) { Install-Manual -Component "Python" }
            if (-not $nodeInstalled) { Install-Manual -Component "Node.js" }
        }
    } else {
        Write-Err "winget not found. Manual installation required:"
        if (-not $pythonInstalled) { Install-Manual -Component "Python" }
        if (-not $nodeInstalled) { Install-Manual -Component "Node.js" }
    }
    
    Write-Host ""
    Write-Warning "After manual installation, run this script again"
    exit 1
}

Write-Success "All dependencies found!"
Write-Info "Python: $PYTHON"
Write-Info "Node.js: OK"
Write-Info "npm: OK"
Write-Host ""

# --- Создание директорий ---
Write-Info "Creating directories..."
$dataDir = Join-Path $ROOT "server\data"
$logsDir = Join-Path $ROOT "server\logs"
$staticDir = Join-Path $ROOT "server\static"
foreach ($d in @($dataDir, $logsDir, $staticDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# --- Виртуальное окружение Python ---
$VENV_DIR = Join-Path $ROOT "server\.venv"
if (-not (Test-Path $VENV_DIR)) {
    Write-Info "Creating Python virtual environment..."
    & $PYTHON -m venv $VENV_DIR
}
$ACTIVATE = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $ACTIVATE

# --- Обновление pip и установка зависимостей Python ---
Write-Info "Updating pip..."
python -m pip install -q --upgrade pip
$reqPath = Join-Path $ROOT "server\requirements.txt"
if (Test-Path $reqPath) {
    Write-Info "Installing Python dependencies..."
    pip install -q -r $reqPath
    Write-Success "Python dependencies installed"
} else {
    Write-Warning "server\requirements.txt not found"
}

# --- Фронтенд ---
Write-Info "Setting up frontend..."
$frontendPath = Join-Path $ROOT "frontend"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    if (Test-Path "package-lock.json") {
        npm ci --no-audit --no-fund
    } else {
        npm install --no-audit --no-fund
    }
    Write-Info "Building frontend..."
    npm run build
    Set-Location $ROOT
    Write-Success "Frontend built successfully"
} else {
    Write-Warning "frontend directory not found"
}

# --- Копирование статики ---
if (Test-Path (Join-Path $ROOT "frontend\build")) {
    Write-Info "Deploying frontend..."
    $BUILD_DIR = Join-Path $ROOT "frontend\build"
    if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
    Copy-Item -Recurse $BUILD_DIR $staticDir
    Write-Success "Frontend copied to server\static"
}

# --- Загрузка .env ---
$envFiles = @(
    (Join-Path $ROOT ".env"),
    (Join-Path $ROOT "server\.env")
)
foreach ($ef in $envFiles) {
    if (Test-Path $ef) {
        Write-Info "Loading environment from $ef"
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
Write-Success "All ready! Starting server..."
Write-Host ""
$serverPath = Join-Path $ROOT "server"
if (Test-Path $serverPath) {
    Set-Location $serverPath
    $env:STATIC_DIR = $staticDir
    Write-Info "Server starting at http://localhost:5000"
    Write-Host ""
    python -m src
} else {
    Write-Err "server directory not found"
    exit 1
}