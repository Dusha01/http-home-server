# Проверка системных зависимостей (Python 3.10+, Node.js 18+, npm) на Windows.
# При отсутствии — предложение установить (yes/no). Установка через winget или инструкции.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT = Split-Path -Parent $ScriptDir

function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Blue }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "❌ $args" -ForegroundColor Red }

$missing = @()
$needNode = $false
$needPython = $false

# Node.js
try {
    $nodeVersion = (node -v 2>$null) -replace '^v(\d+).*', '$1'
    if (-not $nodeVersion -or [int]$nodeVersion -lt 18) {
        if ($nodeVersion) { Write-Warning "Обнаружен Node.js v$nodeVersion, рекомендуется 18+" }
        $missing += "Node.js 18+"
        $needNode = $true
    }
} catch {
    $missing += "Node.js 18+"
    $needNode = $true
}

# npm
try {
    $null = Get-Command npm -ErrorAction Stop
} catch {
    $missing += "npm"
    $needNode = $true
}

# Python 3.10+
$PYTHON = $null
foreach ($py in @("python", "python3", "py")) {
    try {
        $ver = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($ver) {
            $major, $minor = $ver -split '\.'
            if ([int]$major -ge 3 -and [int]$minor -ge 10) {
                $PYTHON = $py
                break
            }
        }
    } catch {}
}
if (-not $PYTHON) {
    $missing += "Python 3.10+"
    $needPython = $true
}

if ($missing.Count -eq 0) {
    Write-Success "Все системные зависимости установлены."
    exit 0
}

Write-Host ""
Write-Err "Отсутствуют зависимости: $($missing -join ', ')"
Write-Host ""
Write-Info "Установить недостающие зависимости автоматически? (yes/no)"
$answer = Read-Host
$answer = $answer.Trim().ToLower()
if ($answer -notin @("yes", "y", "да", "д")) {
    Write-Host ""
    Write-Host "Ручная установка:"
    if ($needNode) {
        Write-Host "  Node.js 18+ и npm:"
        Write-Host "    winget install -e --id OpenJS.NodeJS.LTS"
        Write-Host "    или https://nodejs.org/ — скачайте LTS"
        Write-Host ""
    }
    if ($needPython) {
        Write-Host "  Python 3.10+:"
        Write-Host "    winget install -e --id Python.Python.3.11"
        Write-Host "    или https://www.python.org/downloads/"
        Write-Host ""
    }
    exit 1
}

# Установка через winget
$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Err "winget не найден. Установите App Installer (Windows 10/11) или зависимости вручную."
    Write-Host "  Python:  winget install -e --id Python.Python.3.11"
    Write-Host "  Node.js: winget install -e --id OpenJS.NodeJS.LTS"
    exit 1
}

$installed = $false
$failed = $false
if ($needPython) {
    Write-Info "Установка Python через winget..."
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Не удалось установить Python. Выполните вручную: winget install -e --id Python.Python.3.11"
        $failed = $true
    } else {
        Write-Success "Python установлен."
        $installed = $true
    }
}

if ($needNode) {
    Write-Info "Установка Node.js LTS через winget..."
    winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Не удалось установить Node.js. Выполните вручную: winget install -e --id OpenJS.NodeJS.LTS"
        $failed = $true
    } else {
        Write-Success "Node.js установлен."
        $installed = $true
    }
}

if ($failed) { exit 1 }
if ($installed) {
    Write-Host ""
    Write-Warning "Перезапустите терминал (или откройте новый), чтобы подхватить PATH, затем запустите скрипт снова."
}
exit 0
