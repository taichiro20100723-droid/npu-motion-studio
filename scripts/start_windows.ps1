$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$ModelDirectory = Join-Path $ProjectRoot '.runtime\models\LCM_Dreamshaper_v7-int8-ov'
$TranslationDirectory = Join-Path $ProjectRoot '.runtime\models\opus-mt-ja-en'
$RifeDirectory = Join-Path $ProjectRoot '.runtime\tools\rife-ncnn-vulkan'

try {
    $Running = Invoke-RestMethod -Uri 'http://127.0.0.1:7862/api/health' -TimeoutSec 2
    if ($Running.status -eq 'ok') {
        Start-Process 'http://127.0.0.1:7862/'
        exit 0
    }
} catch {
    # No running app. Continue with normal startup.
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw 'Setup is not complete. Run setup_windows.bat first.'
}

$env:NMS_ENGINE = 'openvino-lcm'
$env:NMS_MODEL_DIRECTORY = $ModelDirectory
$env:NMS_TRANSLATION_MODEL_DIRECTORY = $TranslationDirectory
$env:NMS_RIFE_DIRECTORY = $RifeDirectory
$env:NMS_COMPILE_CACHE_DIRECTORY = Join-Path $ProjectRoot '.runtime\compile_cache'
$env:NMS_OUTPUT_DIRECTORY = Join-Path $ProjectRoot '.runtime\outputs'
$env:NMS_OPEN_BROWSER = 'true'
$env:NMS_DEADLINE_SECONDS = '180'

& $VenvPython -m npu_motion_studio
