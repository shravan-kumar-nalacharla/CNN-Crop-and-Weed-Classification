$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 first from python.org.' }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-local.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
python -m ipykernel install --user --name crop-weed-vgg16 --display-name 'Crop Weed VGG16'
python scripts/verify_environment.py
