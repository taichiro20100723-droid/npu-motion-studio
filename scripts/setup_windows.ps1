$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$ModelDirectory = Join-Path $ProjectRoot '.runtime\models\LCM_Dreamshaper_v7-int8-ov'
$TranslationDirectory = Join-Path $ProjectRoot '.runtime\models\opus-mt-ja-en'
$RifeDirectory = Join-Path $ProjectRoot '.runtime\tools\rife-ncnn-vulkan'
$CacheDirectory = Join-Path $ProjectRoot '.runtime\compile_cache'

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $Python312 = Get-Command py -ErrorAction SilentlyContinue
    if (-not $Python312) {
        throw 'Python 3.12 is required. Install it from https://www.python.org/downloads/'
    }
    & py -3.12 -m venv (Join-Path $ProjectRoot '.venv')
}

Write-Host '1/5 Installing the app'
& $VenvPython -m pip install --disable-pip-version-check --upgrade pip
& $VenvPython -m pip install --disable-pip-version-check -e "$ProjectRoot[production]"

Write-Host '2/5 Downloading the NPU image model (about 1 GB)'
& $VenvPython (Join-Path $PSScriptRoot 'download_model.py') $ModelDirectory

Write-Host '3/5 Downloading the local Japanese translator'
& $VenvPython (Join-Path $PSScriptRoot 'download_translation_model.py') $TranslationDirectory

Write-Host '4/5 Downloading Arc GPU frame interpolation (about 230 MB)'
& $VenvPython (Join-Path $PSScriptRoot 'download_rife.py') $RifeDirectory

Write-Host '5/5 Optimizing the model for the NPU'
& $VenvPython (Join-Path $PSScriptRoot 'prewarm.py') $ModelDirectory $CacheDirectory

Write-Host ''
Write-Host 'Setup complete. Double-click run_windows.bat.' -ForegroundColor Green
