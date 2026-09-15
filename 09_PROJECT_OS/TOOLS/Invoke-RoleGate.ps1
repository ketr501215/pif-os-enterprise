#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Policy = (Join-Path $PSScriptRoot '..\SCHEMA\rayflow-role-gates-v0.1.json'),
    [string]$GateRun,
    [string]$Assignment,
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'
$verifier = Join-Path $PSScriptRoot 'verify_role_gates.py'
if (-not (Test-Path -LiteralPath $verifier -PathType Leaf)) {
    throw 'ROLE_GATE_VERIFIER_MISSING'
}

$candidates = @(
    $env:PIF_PYTHON,
    (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'),
    (Join-Path $env:LOCALAPPDATA 'codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'),
    ((Get-Command python3.exe -ErrorAction SilentlyContinue).Source),
    ((Get-Command python.exe -ErrorAction SilentlyContinue).Source)
) | Where-Object { $_ } | Select-Object -Unique

$python = $null
foreach ($candidate in $candidates) {
    try {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf -ErrorAction Stop)) {
            continue
        }
        & $candidate -c 'import sys; assert sys.version_info >= (3, 9)' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $python = $candidate
            break
        }
    } catch { }
}
if (-not $python) {
    throw 'ROLE_GATE_PYTHON_RUNTIME_MISSING'
}

$arguments = @($verifier, '--policy', $Policy)
if ($SelfTest) { $arguments += '--self-test' }
if ($GateRun) {
    if (-not $Assignment) { throw 'ROLE_GATE_ASSIGNMENT_REQUIRED' }
    $arguments += @('--gate-run', $GateRun, '--assignment', $Assignment, '--repo-root', $RepoRoot)
}
if (-not $SelfTest -and -not $GateRun) {
    throw 'ROLE_GATE_SELECT_SELF_TEST_OR_GATE_RUN'
}

& $python @arguments
exit $LASTEXITCODE
