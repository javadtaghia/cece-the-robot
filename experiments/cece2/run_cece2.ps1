param([int]$Steps = 40)
$ErrorActionPreference = 'Stop'
$cece2Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$cece2Workspace = Split-Path -Parent $cece2Repo
$cece2Python = Join-Path $cece2Workspace 'cece_bullet_env\python.exe'
if (-not (Test-Path -LiteralPath $cece2Python)) {
    throw 'The local cece_bullet_env runtime was not found. See README.md for the portable Python command.'
}
& $cece2Python (Join-Path $PSScriptRoot 'simulate.py') --gui --name gui_cece2 --steps $Steps --hip-deg 15 --roll-deg 12 --phase-seconds 1 --phase-weights '.14,.06,.20,.06,.10' --command-hz 50 --normalized-controller
if ($LASTEXITCODE -ne 0) { throw "Simulator exited with code $LASTEXITCODE" }
