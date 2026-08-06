# qa_video.ps1 — Windows 版 qa_video.sh
# 单条成片 QA 全家桶:直接读取模型原片，生成逐秒 contact sheet + 首/尾帧 + 模式对应帧对照 + 客观分
# 普通 B-roll 不改音轨；完整讲解片追加 -StripAudio 才生成 -noaudio.mp4。
# 用法: pwsh qa_video.ps1 <video.mp4> <confirmed-still.png> [out-dir] [bg-hex] [-Mode first-last|single-first] [-StripAudio]
param(
    [Parameter(Mandatory=$true)][string]$Video,
    [Parameter(Mandatory=$true)][string]$Still,
    [string]$OutDir = "",
    [string]$BgHex = "",
    [ValidateSet("first-last", "single-first")][string]$Mode = "first-last",
    [switch]$StripAudio
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

if ($OutDir -eq "") { $OutDir = Split-Path $Video -Parent }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$dur = & ffprobe -v error -show_entries format=duration -of csv=p=0 $Video
$tiles = [Math]::Min(15, [Math]::Max(4, [int][Math]::Ceiling([double]$dur)))

$audioStreams = & ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 $Video
if ($audioStreams -match "audio") {
    Write-Host "INFO  检测到模型原始音轨；按原样保留"
} else {
    Write-Host "INFO  模型原始视频没有音轨；不补音"
}

if ($StripAudio) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($Video)
    if ($stem.EndsWith("-noaudio")) { $stem = $stem.Substring(0, $stem.Length - "-noaudio".Length) }
    $noaudio = Join-Path $OutDir "${stem}-noaudio.mp4"
    if ($audioStreams -match "audio") {
        ffmpeg -y -v error -i $Video -map 0:v:0 -c:v copy -an $noaudio
    } else {
        Copy-Item -Force $Video $noaudio
    }
    Write-Host "INFO  完整讲解片无音频素材 -> $noaudio"
}

ffmpeg -y -v error -i $Video `
    -vf "fps=1,scale=203:360,tile=${tiles}x1" -frames:v 1 (Join-Path $OutDir "contact-sheet.jpg")
ffmpeg -y -v error -i $Video -frames:v 1 (Join-Path $OutDir "video-first-frame.jpg")
ffmpeg -y -v error -sseof -0.1 -i $Video -frames:v 1 (Join-Path $OutDir "video-last-frame.jpg")
if ($Mode -eq "single-first") {
    $compareFrame = Join-Path $OutDir "video-first-frame.jpg"
    $compareOut = Join-Path $OutDir "start-frame-comparison.jpg"
    Remove-Item -LiteralPath (Join-Path $OutDir "end-frame-comparison.jpg") -Force -ErrorAction SilentlyContinue
} else {
    $compareFrame = Join-Path $OutDir "video-last-frame.jpg"
    $compareOut = Join-Path $OutDir "end-frame-comparison.jpg"
    Remove-Item -LiteralPath (Join-Path $OutDir "start-frame-comparison.jpg") -Force -ErrorAction SilentlyContinue
}
ffmpeg -y -v error -i $Still -i $compareFrame `
    -filter_complex "[0:v]scale=270:480[a];[1:v]scale=270:480[b];[a][b]hstack" $compareOut

# 客观分（需要 Pillow；失败不阻塞）
$qaScore = Join-Path $PSScriptRoot "qa_score.py"
$py = "python"
$scoreArgs = @($qaScore, "--video", $Video, "--still", $Still, "--mode", $Mode)
if ($Mode -eq "first-last" -and $BgHex -ne "") { $scoreArgs += @("--bg-hex", $BgHex) }
try { & $py @scoreArgs } catch { Write-Host "  (qa_score 需要 Pillow,分数缺省不阻塞)" }

Write-Host "QA assets -> $OutDir"
