# Release script for docu-crawler (PowerShell)
# Usage: .\scripts\release.ps1 <version>
# Example: .\scripts\release.ps1 1.1.0

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

# Validate version format
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "Error: Invalid version format. Expected format: X.Y.Z (e.g., 1.1.0)" -ForegroundColor Red
    exit 1
}

$Tag = "v$Version"

Write-Host "Releasing version $Version..." -ForegroundColor Cyan

# Check if we're on main branch
$CurrentBranch = git branch --show-current
if ($CurrentBranch -ne "main") {
    Write-Host "Warning: You're not on the main branch (current: $CurrentBranch)" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Check if working directory is clean
$status = git status --porcelain
if ($status) {
    Write-Host "Error: Working directory is not clean. Please commit or stash changes first." -ForegroundColor Red
    exit 1
}

# Verify version matches code
try {
    $PythonVersion = python -c "import src; print(src.__version__)" 2>$null
    if ($PythonVersion -and $PythonVersion.Trim() -ne $Version) {
        Write-Host "Error: Version mismatch!" -ForegroundColor Red
        Write-Host "  Code version: $PythonVersion" -ForegroundColor Red
        Write-Host "  Release version: $Version" -ForegroundColor Red
        Write-Host "Please update version in setup.py and src/__init__.py first" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Warning: Could not verify version from code" -ForegroundColor Yellow
}

# Check if tag already exists
$tagExists = git rev-parse "$Tag" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Error: Tag $Tag already exists" -ForegroundColor Red
    exit 1
}

# Create and push tag
Write-Host "Creating tag $Tag..." -ForegroundColor Cyan
git tag -a "$Tag" -m "Release $Tag"
git push origin "$Tag"

Write-Host ""
Write-Host "✓ Tag $Tag created and pushed" -ForegroundColor Green
Write-Host "✓ GitHub Actions will automatically:" -ForegroundColor Green
Write-Host "  - Run tests" -ForegroundColor Gray
Write-Host "  - Build the package" -ForegroundColor Gray
Write-Host "  - Publish to PyPI" -ForegroundColor Gray
Write-Host "  - Create a GitHub release" -ForegroundColor Gray
Write-Host ""
Write-Host "Monitor progress at: https://github.com/dataiscool/docu-crawler/actions" -ForegroundColor Cyan

