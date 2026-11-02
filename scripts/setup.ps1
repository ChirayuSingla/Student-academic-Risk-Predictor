param(
    [string]$PythonExe,
    [string]$EnvironmentName = '.venv',
    [switch]$Recreate
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
# A leaf name keeps environment backups within this project, including on Windows.
if ($EnvironmentName -notmatch '^\.venv[A-Za-z0-9_-]*$') {
    throw 'EnvironmentName must be a project-local name such as .venv312.'
}
$environmentPath = Join-Path $projectRoot $EnvironmentName
$environmentPython = Join-Path $environmentPath 'Scripts\python.exe'
if (-not $PythonExe) {
    $candidate = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
    if (Test-Path -LiteralPath $candidate) { $PythonExe = $candidate }
    elseif (Test-Path -LiteralPath (Join-Path $projectRoot '.runtime\python31210\tools\python.exe')) {
        $PythonExe = Join-Path $projectRoot '.runtime\python31210\tools\python.exe'
    }
    else {
        $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($launcher) {
            $PythonExe = & $launcher.Source -3.12 -c 'import sys; print(sys.executable)'
            if ($LASTEXITCODE -ne 0) { $PythonExe = $null }
        }
    }
}
if (-not $PythonExe -or -not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw 'Install Python 3.12.10 x64 for your user, then pass -PythonExe with its full python.exe path.'
}
$runtimeCheck = 'import struct,sys; print(sys.version); sys.exit(0 if sys.version_info[:2] == (3,12) and struct.calcsize(chr(80)) == 8 else 1)'
& $PythonExe -I -c $runtimeCheck
if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 x64 is required. Python 3.10 cannot run this environment.' }
if ($env:PYTHONHOME -or $env:PYTHONPATH) {
    throw 'Clear PYTHONHOME and PYTHONPATH in this terminal before creating an isolated environment.'
}
if (Test-Path -LiteralPath $environmentPath) {
    if (-not $Recreate) {
        throw "$EnvironmentName already exists. Use -Recreate to back it up and build a fresh environment."
    }
    $resolvedEnvironment = (Resolve-Path -LiteralPath $environmentPath).Path
    if ($resolvedEnvironment -ne [IO.Path]::GetFullPath($environmentPath)) {
        throw 'Refusing to move an environment that resolves outside the expected project path.'
    }
    if ((Get-Item -LiteralPath $environmentPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Refusing to move a linked environment directory.'
    }
    $backupPath = "$environmentPath-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss-fff')"
    Move-Item -LiteralPath $environmentPath -Destination $backupPath
    Write-Host "Previous environment preserved at $backupPath"
}
& $PythonExe -I -m venv $environmentPath
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
Push-Location $projectRoot
try {
    & $environmentPython -m pip install --only-binary=:all: -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Locked dependency installation failed.' }
    & $environmentPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed.' }
    & $environmentPython -m src.doctor
    if ($LASTEXITCODE -ne 0) { throw 'Environment diagnostics failed.' }
} finally { Pop-Location }
Write-Host "Ready. Launch with: & '$environmentPython' -m streamlit run '$projectRoot\app.py'"
