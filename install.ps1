$ErrorActionPreference = "Stop"

$Branch = if ($env:ACHERON_BRANCH) { $env:ACHERON_BRANCH } else { "master" }
if ($Branch -notmatch '^[A-Za-z0-9._/-]+$') {
    throw "Invalid ACHERON_BRANCH value."
}

$Root = Join-Path $env:LOCALAPPDATA "Acheron"
$Source = Join-Path $Root "source"
$Bin = Join-Path $Root "bin"
$Venv = Join-Path $Root "venv"
$Raw = "https://raw.githubusercontent.com/ak495867/Acheron/$Branch"

$PythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($PythonCommand) {
    $Python = $PythonCommand.Source
    $PythonPrefix = @("-3")
} else {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $PythonCommand) {
        throw "Acheron needs Python 3.9 or newer. Install Python from python.org, then run the installer again."
    }
    $Python = $PythonCommand.Source
    $PythonPrefix = @()
}

$Version = & $Python @PythonPrefix -c "import sys; print(sys.version_info >= (3, 9))"
if ($Version -ne "True") {
    throw "Acheron needs Python 3.9 or newer."
}

New-Item -ItemType Directory -Force -Path $Source, $Bin | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$Raw/pyproject.toml" -OutFile (Join-Path $Source "pyproject.toml")
Invoke-WebRequest -UseBasicParsing -Uri "$Raw/README.md" -OutFile (Join-Path $Source "README.md")
Invoke-WebRequest -UseBasicParsing -Uri "$Raw/LICENSE" -OutFile (Join-Path $Source "LICENSE")
New-Item -ItemType Directory -Force -Path (Join-Path $Source "src") | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$Raw/src/acheron.py" -OutFile (Join-Path $Source "src/acheron.py")

& $Python @PythonPrefix -m venv $Venv
if ($LASTEXITCODE -ne 0) {
    throw "Could not create Acheron's Python environment."
}
$VenvPython = Join-Path $Venv "Scripts/python.exe"
& $VenvPython -m pip install --upgrade --force-reinstall --disable-pip-version-check $Source
if ($LASTEXITCODE -ne 0) {
    throw "Acheron installation failed."
}

$Launcher = Join-Path $Bin "acheron.cmd"
$Command = "@echo off`r`n`"$Venv\Scripts\acheron.exe`" %*`r`n"
Set-Content -Encoding ASCII -Path $Launcher -Value $Command
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
$PathEntries = @($UserPath -split ';' | Where-Object { $_ })
if ($PathEntries -notcontains $Bin) {
    $UpdatedPath = (@($PathEntries) + $Bin) -join ';'
    [Environment]::SetEnvironmentVariable("Path", $UpdatedPath, "User")
}
$env:Path = "$Bin;$env:Path"

Write-Host "Acheron is ready. Run: acheron"
Write-Host "If this terminal cannot find it, open a fresh terminal and run acheron."
