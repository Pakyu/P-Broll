# prepare_frames.ps1 — Windows 版 prepare_frames.sh
# 从 <item>/frames/last-frame-original.png 生成 Gate 3 首尾帧:
#   实测底色采样(4x4 均值) -> bg-hex.txt
#   last-frame.png (1080x1920 scale+crop)
#   first-frame.png (实测底色纯色空场)
# 用法: pwsh prepare_frames.ps1 <item-dir> [采样点x:y, 默认 28:58]
param(
    [Parameter(Mandatory=$true)][string]$ItemDir,
    [string]$XY = "28:58"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$parts = $XY -split ":"
$X = $parts[0]; $Y = $parts[1]

$src = Join-Path $ItemDir "frames\last-frame-original.png"
if (-not (Test-Path $src)) { Write-Error "缺少 $src"; exit 1 }

$framesDir = Join-Path $ItemDir "frames"
$px = Join-Path $env:TEMP ("pf-" + [guid]::NewGuid().ToString("N") + ".raw")

# 采样 4x4 -> 1x1 RGB24，读出底色 hex
ffmpeg -y -v error -i $src -vf "crop=4:4:${X}:${Y},scale=1:1" `
    -frames:v 1 -f rawvideo -pix_fmt rgb24 $px
$bytes = [System.IO.File]::ReadAllBytes($px)
Remove-Item $px -Force
$hex = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ""

$bgHexFile = Join-Path $framesDir "bg-hex.txt"
[System.IO.File]::WriteAllText($bgHexFile, $hex)

# 尾帧 1080x1920
ffmpeg -y -v error -i $src `
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" `
    (Join-Path $framesDir "last-frame.png")

# 纯色空首帧
ffmpeg -y -v error -f lavfi -i "color=c=0x${hex}:s=1080x1920" `
    -frames:v 1 (Join-Path $framesDir "first-frame.png")

Write-Host ("$(Split-Path $ItemDir -Leaf) bg=#$hex frames ready")
