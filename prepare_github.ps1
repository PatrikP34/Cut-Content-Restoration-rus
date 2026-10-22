$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found. Install Git for Windows, then reopen PyCharm."
}

$requiredFiles = @(
    ".gitignore",
    "build_russian_patch.py",
    "build_russian_patch.bat",
    "README.ru.md",
    "prepare_github.ps1",
    "LICENSE",
    "THIRD_PARTY.md",
    "test_russian_merge.py",
    "russian_merge\__init__.py",
    "russian_merge\build_all.py",
    "russian_merge\convert_scene.py",
    "russian_merge\fpd.py",
    "russian_merge\merge_scene.py"
)

$missingFiles = @($requiredFiles | Where-Object {
    -not (Test-Path -LiteralPath $_ -PathType Leaf)
})
if ($missingFiles.Count -gt 0) {
    throw "Required project files are missing: $($missingFiles -join ', ')"
}

$ignoredExtensions = @(
    ".bin", ".exe", ".dll", ".dat", ".xp3", ".obb", ".pak", ".zip", ".7z", ".rar"
)
$unsafeFiles = @($requiredFiles | Where-Object {
    $ignoredExtensions -contains [IO.Path]::GetExtension($_).ToLowerInvariant()
})
if ($unsafeFiles.Count -gt 0) {
    throw "Refusing to stage binary/game data: $($unsafeFiles -join ', ')"
}

$gitDirectory = Join-Path $projectRoot ".git"
if (-not (Test-Path -LiteralPath $gitDirectory)) {
    & git init
    if ($LASTEXITCODE -ne 0) {
        throw "git init failed."
    }
}

& git add -- $requiredFiles
if ($LASTEXITCODE -ne 0) {
    throw "git add failed."
}

$stagedPaths = @(& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect the Git staging area."
}

$allowedExactPaths = @(
    ".gitignore",
    "build_russian_patch.py",
    "build_russian_patch.bat",
    "README.ru.md",
    "prepare_github.ps1",
    "LICENSE",
    "THIRD_PARTY.md",
    "test_russian_merge.py"
)
$unexpectedPaths = @($stagedPaths | Where-Object {
    $path = $_ -replace "\\", "/"
    ($allowedExactPaths -notcontains $path) -and
    ($path -notmatch "^russian_merge/[^/]+\.py$")
})

if ($unexpectedPaths.Count -gt 0) {
    Write-Host "STOP: unexpected files are staged. Nothing was committed or pushed." -ForegroundColor Red
    Write-Host "Review these paths before continuing:"
    $unexpectedPaths | ForEach-Object { Write-Host "  $_" }
    throw "The staging area contains files outside the allowed source/documentation list."
}

Write-Host ""
Write-Host "Only source code and project documentation are staged:"
$stagedPaths | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "No commit or upload was performed. Review the list, then commit and push from PyCharm."
