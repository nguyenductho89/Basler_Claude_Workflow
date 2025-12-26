# Development Environment Setup Script
# Run: .\scripts\setup-dev.ps1

Write-Host "=== Setting up development environment ===" -ForegroundColor Cyan

# Check Python
$python = "py -3.11"
try {
    $version = & py -3.11 --version 2>&1
    Write-Host "Found: $version" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.11 not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
& py -3.11 -m pip install --upgrade pip
& py -3.11 -m pip install -r requirements.txt

# Install dev tools
Write-Host "`nInstalling development tools..." -ForegroundColor Yellow
& py -3.11 -m pip install pre-commit ruff mypy types-Pillow

# Setup pre-commit hooks
Write-Host "`nSetting up pre-commit hooks..." -ForegroundColor Yellow
& py -3.11 -m pre_commit install

Write-Host "`n=== Setup complete! ===" -ForegroundColor Green
Write-Host "`nPre-commit hooks installed. They will run automatically on git commit."
Write-Host "`nUseful commands:"
Write-Host "  pre-commit run --all-files  # Run all hooks manually"
Write-Host "  pre-commit run ruff         # Run ruff only"
Write-Host "  pre-commit run mypy         # Run mypy only"
Write-Host "  ruff check src/ --fix       # Fix lint errors"
Write-Host "  ruff format src/            # Format code"
