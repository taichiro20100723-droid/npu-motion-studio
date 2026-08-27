$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$Source = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Downloads\Murata Night.mp4'
$Backgrounds = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Downloads\WasedaSaga-MV-backgrounds'
$Output = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Downloads\WasedaSaga-Festival-MV-dynamic-object-safe.mp4'

if (-not (Test-Path -LiteralPath $Source)) {
    throw "Murata Night.mp4 がDownloadsにありません。"
}
if (-not (Test-Path -LiteralPath $Backgrounds)) {
    throw "WasedaSaga-MV-backgrounds フォルダーがDownloadsにありません。"
}

& $Python (Join-Path $ProjectRoot 'scripts\make_music_video.py') $Source `
    --work-dir (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Downloads\WasedaSaga-Safe-MV-work') `
    --mode wow --anchors 12 --backgrounds $Backgrounds --photo-every 4 --transition-seconds 0.55 --output $Output
Write-Host "完成しました: $Output"
Read-Host 'Enterで閉じます'
