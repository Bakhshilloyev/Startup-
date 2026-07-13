# Windows (PowerShell) setup.
$ErrorActionPreference = "Stop"

Write-Host "==> Updating pip"
python -m pip install --upgrade pip

Write-Host "==> Installing optional dependencies"
python -m pip install -r requirements-windows.txt

Write-Host "==> (Optional) install as a command"
python -m pip install -e .

Write-Host "==> Done. Try:  python run.py ""list files in the current directory"""
