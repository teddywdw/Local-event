# setup-dev.ps1
# PowerShell helper to create a venv, install dependencies and enable pre-commit hooks
param(
    [string]$venvName = ".venv"
)

Write-Host "Creating virtual environment in $venvName"
python -m venv $venvName

Write-Host "Activating venv"
. .\$venvName\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing requirements"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

Write-Host "Installing pre-commit hooks"
pre-commit install

Write-Host "Done. Activate the venv with `. .\$venvName\Scripts\Activate.ps1` if not already active."
