param([ValidateSet('drive','crank','bench','walk','check')][string]$Mode='drive')
$chickPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $chickPython)) {
    $chickPython = Join-Path (Split-Path $PSScriptRoot -Parent) 'coffee-robot\.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $chickPython)) {
    throw 'Install requirements-sim.txt into a local .venv first.'
}
if ($Mode -eq 'drive') {
    & $chickPython (Join-Path $PSScriptRoot 'drive_study.py') --view
} elseif ($Mode -eq 'crank') {
    & $chickPython (Join-Path $PSScriptRoot 'crank_drive.py') --view
} else {
    & $chickPython (Join-Path $PSScriptRoot 'chick_sim.py') "--$Mode"
}
